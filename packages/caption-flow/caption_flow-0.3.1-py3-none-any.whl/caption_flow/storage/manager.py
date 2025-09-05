"""Arrow/Parquet storage management with dynamic column support for outputs."""

import asyncio
import gc
import json
import logging
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Set, Dict, Any
import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow import fs
import pandas as pd
from collections import defaultdict, deque
import time
import numpy as np

from ..models import Job, Caption, Contributor, StorageContents, JobId

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class StorageManager:
    """Manages Arrow/Parquet storage with dynamic columns for output fields."""

    def __init__(
        self,
        data_dir: Path,
        caption_buffer_size: int = 100,
        contributor_buffer_size: int = 50,
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.captions_path = self.data_dir / "captions.parquet"
        self.jobs_path = self.data_dir / "jobs.parquet"
        self.contributors_path = self.data_dir / "contributors.parquet"
        self.stats_path = self.data_dir / "storage_stats.json"  # Persist stats here

        # In-memory buffers for batching writes
        self.caption_buffer = []
        self.job_buffer = []
        self.contributor_buffer = []

        # Buffer size configuration
        self.caption_buffer_size = caption_buffer_size
        self.contributor_buffer_size = contributor_buffer_size

        # Track existing job_ids to prevent duplicates
        self.existing_contributor_ids: Set[str] = set()
        self.existing_caption_job_ids: Set[str] = set()
        self.existing_job_ids: Set[str] = set()

        # Track known output fields for schema evolution
        self.known_output_fields: Set[str] = set()

        # In-memory statistics (loaded once at startup, then tracked incrementally)
        self.stats = {
            "disk_rows": 0,  # Rows in parquet file
            "disk_outputs": 0,  # Total outputs in parquet file
            "field_counts": {},  # Count of outputs per field on disk
            "total_captions_written": 0,  # Total rows written during this session
            "total_caption_entries_written": 0,  # Total individual captions written
            "total_flushes": 0,
            "duplicates_skipped": 0,
            "session_field_counts": {},  # Outputs per field written this session
        }

        # Rate tracking
        self.row_additions = deque(maxlen=100)  # Store (timestamp, row_count) tuples
        self.start_time = time.time()
        self.last_rate_log_time = time.time()

        # Base caption schema without dynamic output fields
        self.base_caption_fields = [
            ("job_id", pa.string()),
            ("dataset", pa.string()),
            ("shard", pa.string()),
            ("chunk_id", pa.string()),
            ("item_key", pa.string()),
            ("item_index", pa.int32()),
            ("filename", pa.string()),
            ("url", pa.string()),
            ("caption_count", pa.int32()),
            ("contributor_id", pa.string()),
            ("timestamp", pa.timestamp("us")),
            ("quality_scores", pa.list_(pa.float32())),
            ("image_width", pa.int32()),
            ("image_height", pa.int32()),
            ("image_format", pa.string()),
            ("file_size", pa.int64()),
            ("processing_time_ms", pa.float32()),
            ("metadata", pa.string()),
        ]

        # Current caption schema (will be updated dynamically)
        self.caption_schema = None

        self.job_schema = pa.schema(
            [
                ("job_id", pa.string()),
                ("dataset", pa.string()),
                ("shard", pa.string()),
                ("item_key", pa.string()),
                ("status", pa.string()),
                ("assigned_to", pa.string()),
                ("created_at", pa.timestamp("us")),
                ("updated_at", pa.timestamp("us")),
            ]
        )

        self.contributor_schema = pa.schema(
            [
                ("contributor_id", pa.string()),
                ("name", pa.string()),
                ("total_captions", pa.int64()),
                ("trust_level", pa.int32()),
            ]
        )

    def _save_stats(self):
        """Persist current stats to disk."""
        try:
            with open(self.stats_path, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def _load_stats(self):
        """Load stats from disk if available."""
        if self.stats_path.exists():
            try:
                with open(self.stats_path, "r") as f:
                    loaded_stats = json.load(f)
                    # Merge loaded stats with defaults
                    self.stats.update(loaded_stats)
                    logger.info(f"Loaded stats from {self.stats_path}")
            except Exception as e:
                logger.error(f"Failed to load stats: {e}")

    def _calculate_initial_stats(self):
        """Calculate stats from parquet file - only called once at initialization."""
        if not self.captions_path.exists():
            return

        logger.info("Calculating initial statistics from parquet file...")

        try:
            # Get metadata to determine row count
            table_metadata = pq.read_metadata(self.captions_path)
            self.stats["disk_rows"] = table_metadata.num_rows

            # Simply use the known_output_fields that were already detected during initialization
            # This avoids issues with PyArrow schema parsing
            if self.known_output_fields and table_metadata.num_rows > 0:
                # Read the entire table since column-specific reading is causing issues
                table = pq.read_table(self.captions_path)
                df = table.to_pandas()

                total_outputs = 0
                field_counts = {}

                # Count outputs in each known output field
                for field_name in self.known_output_fields:
                    if field_name in df.columns:
                        field_count = 0
                        column_data = df[field_name]

                        # Iterate through values more carefully to avoid numpy array issues
                        for i in range(len(column_data)):
                            value = column_data.iloc[i]
                            # Handle None/NaN values first
                            if value is None:
                                continue
                            # For lists/arrays, check if they're actually None or have content
                            try:
                                # If it's a list-like object, count its length
                                if hasattr(value, "__len__") and not isinstance(value, str):
                                    # Check if it's a pandas null value by trying to check the first element
                                    if len(value) > 0:
                                        field_count += len(value)
                                    # Empty lists are valid but contribute 0
                            except TypeError:
                                # Value is scalar NA/NaN, skip it
                                continue
                            except:
                                # Any other error, skip this value
                                continue

                        if field_count > 0:
                            field_counts[field_name] = field_count
                            total_outputs += field_count

                self.stats["disk_outputs"] = total_outputs
                self.stats["field_counts"] = field_counts

                # Clean up
                del df, table
                gc.collect()
            else:
                self.stats["disk_outputs"] = 0
                self.stats["field_counts"] = {}

            logger.info(
                f"Initial stats: {self.stats['disk_rows']} rows, {self.stats['disk_outputs']} outputs, fields: {list(self.stats['field_counts'].keys())}"
            )

        except Exception as e:
            logger.error(f"Failed to calculate initial stats: {e}", exc_info=True)
            # Set default values
            self.stats["disk_rows"] = 0
            self.stats["disk_outputs"] = 0
            self.stats["field_counts"] = {}

        # Save the calculated stats
        self._save_stats()

    def _update_stats_for_new_captions(self, captions_added: List[dict], rows_added: int):
        """Update stats incrementally as new captions are added."""
        # Update row counts
        self.stats["disk_rows"] += rows_added
        self.stats["total_captions_written"] += rows_added

        # Count outputs in the new captions
        outputs_added = 0
        for caption in captions_added:
            for field_name in self.known_output_fields:
                if field_name in caption and isinstance(caption[field_name], list):
                    count = len(caption[field_name])
                    outputs_added += count

                    # Update field-specific counts
                    if field_name not in self.stats["field_counts"]:
                        self.stats["field_counts"][field_name] = 0
                    self.stats["field_counts"][field_name] += count

                    if field_name not in self.stats["session_field_counts"]:
                        self.stats["session_field_counts"][field_name] = 0
                    self.stats["session_field_counts"][field_name] += count

        self.stats["disk_outputs"] += outputs_added
        self.stats["total_caption_entries_written"] += outputs_added

    def _is_column_empty(self, df: pd.DataFrame, column_name: str) -> bool:
        """Check if a column is entirely empty, null, or contains only zeros/empty lists."""
        if column_name not in df.columns:
            return True

        col = df[column_name]

        # Check if all values are null/NaN
        if col.isna().all():
            return True

        # For numeric columns, check if all non-null values are 0
        if pd.api.types.is_numeric_dtype(col):
            non_null_values = col.dropna()
            if len(non_null_values) > 0 and (non_null_values == 0).all():
                return True

        # For list columns, check if all are None or empty lists
        if col.dtype == "object":
            non_null_values = col.dropna()
            if len(non_null_values) == 0:
                return True
            # Check if all non-null values are empty lists
            all_empty_lists = True
            for val in non_null_values:
                if isinstance(val, list) and len(val) > 0:
                    all_empty_lists = False
                    break
                elif not isinstance(val, list):
                    all_empty_lists = False
                    break
            if all_empty_lists:
                return True

        return False

    def _get_non_empty_columns(
        self, df: pd.DataFrame, preserve_base_fields: bool = True
    ) -> List[str]:
        """Get list of columns that contain actual data.

        Args:
            df: DataFrame to check
            preserve_base_fields: If True, always include base fields even if empty
        """
        base_field_names = {field[0] for field in self.base_caption_fields}
        non_empty_columns = []

        for col in df.columns:
            # Always keep base fields if preserve_base_fields is True
            if preserve_base_fields and col in base_field_names:
                non_empty_columns.append(col)
            elif not self._is_column_empty(df, col):
                non_empty_columns.append(col)

        return non_empty_columns

    def _calculate_rates(self) -> Dict[str, float]:
        """Calculate row addition rates over different time windows."""
        current_time = time.time()
        rates = {}

        # Define time windows in minutes
        windows = {"1min": 1, "5min": 5, "15min": 15, "60min": 60}

        # Clean up old entries beyond the largest window
        cutoff_time = current_time - (60 * 60)  # 60 minutes
        while self.row_additions and self.row_additions[0][0] < cutoff_time:
            self.row_additions.popleft()

        # Calculate rates for each window
        for window_name, window_minutes in windows.items():
            window_seconds = window_minutes * 60
            window_start = current_time - window_seconds

            # Sum rows added within this window
            rows_in_window = sum(
                count for timestamp, count in self.row_additions if timestamp >= window_start
            )

            # Calculate rate (rows per second)
            # For windows larger than elapsed time, use elapsed time
            elapsed = current_time - self.start_time
            actual_window = min(window_seconds, elapsed)

            if actual_window > 0:
                rate = rows_in_window / actual_window
                rates[window_name] = rate
            else:
                rates[window_name] = 0.0

        # Calculate instantaneous rate (last minute)
        instant_window_start = current_time - 60  # Last 60 seconds
        instant_rows = sum(
            count for timestamp, count in self.row_additions if timestamp >= instant_window_start
        )
        instant_window = min(60, current_time - self.start_time)
        rates["instant"] = instant_rows / instant_window if instant_window > 0 else 0.0

        # Calculate overall rate since start
        total_elapsed = current_time - self.start_time
        if total_elapsed > 0:
            rates["overall"] = self.stats["total_captions_written"] / total_elapsed
        else:
            rates["overall"] = 0.0

        return rates

    def _log_rates(self, rows_added: int):
        """Log rate information if enough time has passed."""
        current_time = time.time()

        # Log rates every 10 seconds or if it's been more than 30 seconds
        time_since_last_log = current_time - self.last_rate_log_time
        if time_since_last_log < 10 and rows_added < 50:
            return

        rates = self._calculate_rates()

        # Format the rate information
        rate_str = (
            f"Rate stats - Instant: {rates['instant']:.1f} rows/s | "
            f"Avg (5m): {rates['5min']:.1f} | "
            f"Avg (15m): {rates['15min']:.1f} | "
            f"Avg (60m): {rates['60min']:.1f} | "
            f"Overall: {rates['overall']:.1f} rows/s"
        )

        logger.info(rate_str)
        self.last_rate_log_time = current_time

    def _get_existing_output_columns(self) -> Set[str]:
        """Get output field columns that actually exist in the parquet file."""
        if not self.captions_path.exists():
            return set()

        table_metadata = pq.read_metadata(self.captions_path)
        existing_columns = set(table_metadata.schema.names)
        base_field_names = {field[0] for field in self.base_caption_fields}

        return existing_columns - base_field_names

    def _build_caption_schema(self, output_fields: Set[str]) -> pa.Schema:
        """Build caption schema with dynamic output fields."""
        fields = self.base_caption_fields.copy()

        # Add dynamic output fields (all as list of strings for now)
        for field_name in sorted(output_fields):  # Sort for consistent ordering
            fields.append((field_name, pa.list_(pa.string())))

        return pa.schema(fields)

    async def initialize(self):
        """Initialize storage files if they don't exist."""
        # Load persisted stats if available
        self._load_stats()

        if not self.captions_path.exists():
            # Create initial schema with just base fields
            self.caption_schema = self._build_caption_schema(set())

            # Create empty table
            empty_dict = {field[0]: [] for field in self.base_caption_fields}
            empty_table = pa.Table.from_pydict(empty_dict, schema=self.caption_schema)
            pq.write_table(empty_table, self.captions_path)
            logger.info(f"Created empty caption storage at {self.captions_path}")

            # Initialize stats
            self.stats["disk_rows"] = 0
            self.stats["disk_outputs"] = 0
            self.stats["field_counts"] = {}
        else:
            # Load existing schema and detect output fields
            existing_table = pq.read_table(self.captions_path)
            existing_columns = set(existing_table.column_names)

            # Identify output fields (columns not in base schema)
            base_field_names = {field[0] for field in self.base_caption_fields}
            self.known_output_fields = existing_columns - base_field_names

            # Check if we need to migrate from old "outputs" JSON column
            if "outputs" in existing_columns:
                logger.info("Migrating from JSON outputs to dynamic columns...")
                await self._migrate_outputs_to_columns(existing_table)
            else:
                # Build current schema from existing columns
                self.caption_schema = self._build_caption_schema(self.known_output_fields)

            # Load existing caption job_ids
            self.existing_caption_job_ids = set(existing_table["job_id"].to_pylist())
            logger.info(f"Loaded {len(self.existing_caption_job_ids)} existing caption job_ids")
            logger.info(f"Known output fields: {sorted(self.known_output_fields)}")

            # Calculate initial stats if not already loaded from file
            if self.stats["disk_rows"] == 0:
                self._calculate_initial_stats()

        # Initialize other storage files...
        if not self.contributors_path.exists():
            empty_dict = {"contributor_id": [], "name": [], "total_captions": [], "trust_level": []}
            empty_table = pa.Table.from_pydict(empty_dict, schema=self.contributor_schema)
            pq.write_table(empty_table, self.contributors_path)
            logger.info(f"Created empty contributor storage at {self.contributors_path}")
        else:
            existing_contributors = pq.read_table(
                self.contributors_path, columns=["contributor_id"]
            )
            self.existing_contributor_ids = set(existing_contributors["contributor_id"].to_pylist())
            logger.info(f"Loaded {len(self.existing_contributor_ids)} existing contributor IDs")

    async def _migrate_outputs_to_columns(self, existing_table: pa.Table):
        """Migrate from JSON outputs column to dynamic columns."""
        df = existing_table.to_pandas()

        # Collect all unique output field names
        output_fields = set()
        for outputs_json in df.get("outputs", []):
            if outputs_json:
                try:
                    outputs = json.loads(outputs_json)
                    output_fields.update(outputs.keys())
                except:
                    continue

        # Add legacy "captions" field if it exists and isn't already a base field
        if "captions" in df.columns and "captions" not in {f[0] for f in self.base_caption_fields}:
            output_fields.add("captions")

        logger.info(f"Found output fields to migrate: {sorted(output_fields)}")

        # Create new columns for each output field
        for field_name in output_fields:
            if field_name not in df.columns:
                df[field_name] = None

        # Migrate data from outputs JSON to columns
        for idx, row in df.iterrows():
            if pd.notna(row.get("outputs")):
                try:
                    outputs = json.loads(row["outputs"])
                    for field_name, field_values in outputs.items():
                        df.at[idx, field_name] = field_values
                except:
                    continue

            # Handle legacy captions column if it's becoming a dynamic field
            if "captions" in output_fields and pd.notna(row.get("captions")):
                if pd.isna(df.at[idx, "captions"]):
                    df.at[idx, "captions"] = row["captions"]

        # Drop the old outputs column
        if "outputs" in df.columns:
            df = df.drop(columns=["outputs"])

        # Remove empty columns before saving (but preserve base fields)
        non_empty_columns = self._get_non_empty_columns(df, preserve_base_fields=True)
        df = df[non_empty_columns]

        # Update known fields and schema based on non-empty columns
        base_field_names = {field[0] for field in self.base_caption_fields}
        self.known_output_fields = set(non_empty_columns) - base_field_names
        self.caption_schema = self._build_caption_schema(self.known_output_fields)

        # Write migrated table
        migrated_table = pa.Table.from_pandas(df, schema=self.caption_schema)
        pq.write_table(migrated_table, self.captions_path)
        logger.info("Migration complete - outputs now stored in dynamic columns")

        # Recalculate stats after migration
        self._calculate_initial_stats()

    async def save_caption(self, caption: Caption):
        """Save a caption entry, grouping outputs by job_id/item_key (not separating captions)."""
        caption_dict = asdict(caption)

        # Extract item_index from metadata if present
        if "metadata" in caption_dict and isinstance(caption_dict["metadata"], dict):
            item_index = caption_dict["metadata"].get("_item_index")
            if item_index is not None:
                caption_dict["item_index"] = item_index

        # Extract outputs and handle them separately
        outputs = caption_dict.pop("outputs", {})

        # Remove old "captions" field if it exists (will be in outputs)
        caption_dict.pop("captions", None)

        # Grouping key: (job_id, item_key)
        _job_id = caption_dict.get("job_id")
        job_id = JobId.from_dict(_job_id).get_sample_str()
        group_key = job_id

        # Check for duplicate - if this job_id already exists on disk, skip it
        if group_key in self.existing_caption_job_ids:
            self.stats["duplicates_skipped"] += 1
            logger.debug(f"Skipping duplicate job_id: {group_key}")
            return

        # Try to find existing buffered row for this group
        found_row = False
        for idx, row in enumerate(self.caption_buffer):
            check_key = row.get("job_id")
            if check_key == group_key:
                found_row = True
                # Merge outputs into existing row
                for field_name, field_values in outputs.items():
                    if field_name not in self.known_output_fields:
                        self.known_output_fields.add(field_name)
                    if field_name in row and isinstance(row[field_name], list):
                        row[field_name].extend(field_values)
                    else:
                        row[field_name] = list(field_values)
                # Optionally update other fields (e.g., caption_count)
                if "caption_count" in caption_dict:
                    old_count = row.get("caption_count", 0)
                    row["caption_count"] = old_count + caption_dict["caption_count"]
                return  # Already merged, no need to add new row

        # If not found, create new row
        for field_name, field_values in outputs.items():
            if field_name not in self.known_output_fields:
                self.known_output_fields.add(field_name)
                logger.info(f"New output field detected: {field_name}")
            caption_dict[field_name] = list(field_values)

        # Serialize metadata to JSON if present
        if "metadata" in caption_dict:
            caption_dict["metadata"] = json.dumps(caption_dict.get("metadata", {}))
        else:
            caption_dict["metadata"] = "{}"

        if isinstance(caption_dict.get("job_id"), dict):
            caption_dict["job_id"] = job_id

        self.caption_buffer.append(caption_dict)

        if len(self.caption_buffer) >= self.caption_buffer_size:
            logger.debug("Caption buffer full, flushing captions.")
            await self._flush_captions()

    async def _flush_captions(self):
        """Write caption buffer to parquet with dynamic schema."""
        if not self.caption_buffer:
            return

        try:
            num_rows = len(self.caption_buffer)

            # Count total outputs across all fields
            total_outputs = 0
            for row in self.caption_buffer:
                for field_name in self.known_output_fields:
                    if field_name in row and isinstance(row[field_name], list):
                        total_outputs += len(row[field_name])

            logger.debug(
                f"Flushing {num_rows} rows with {total_outputs} total outputs to disk. preparing data..."
            )

            # Keep a copy of captions for stats update
            captions_to_write = list(self.caption_buffer)

            # Prepare data with all required columns
            prepared_buffer = []
            new_job_ids = []
            for row in self.caption_buffer:
                prepared_row = row.copy()

                # Track job_ids for deduplication
                job_id = prepared_row.get("job_id")
                if job_id:
                    new_job_ids.append(job_id)

                # Ensure all base fields are present
                for field_name, field_type in self.base_caption_fields:
                    if field_name not in prepared_row:
                        prepared_row[field_name] = None

                # Ensure all output fields are present (even if None)
                for field_name in self.known_output_fields:
                    if field_name not in prepared_row:
                        prepared_row[field_name] = None

                prepared_buffer.append(prepared_row)

            # Build schema with all known fields (base + output)
            logger.debug("building schema...")
            schema = self._build_caption_schema(self.known_output_fields)
            logger.debug("schema built, creating table...")
            table = pa.Table.from_pylist(prepared_buffer, schema=schema)

            if self.captions_path.exists():
                # Read existing table - this is necessary for parquet format
                logger.debug("Reading existing captions file...")
                existing = pq.read_table(self.captions_path)

                logger.debug("writing new rows...")
                # Concatenate with promote_options="default" to handle schema differences automatically
                logger.debug("concat tables...")
                combined = pa.concat_tables([existing, table], promote_options="default")

                # Write combined table
                pq.write_table(combined, self.captions_path, compression="snappy")

                actual_new = len(table)
            else:
                # Write new file with all fields
                pq.write_table(table, self.captions_path, compression="snappy")
                actual_new = num_rows
            logger.debug("write complete.")

            # Clean up
            del prepared_buffer, table

            # Update the in-memory job_id set for efficient deduplication
            self.existing_caption_job_ids.update(new_job_ids)

            # Update statistics incrementally
            self._update_stats_for_new_captions(captions_to_write, actual_new)
            self.stats["total_flushes"] += 1

            # Clear buffer
            self.caption_buffer.clear()

            # Track row additions for rate calculation
            if actual_new > 0:
                current_time = time.time()
                self.row_additions.append((current_time, actual_new))

                # Log rates
                self._log_rates(actual_new)

            logger.info(
                f"Successfully wrote captions (new rows: {actual_new}, "
                f"total rows written: {self.stats['total_captions_written']}, "
                f"total captions written: {self.stats['total_caption_entries_written']}, "
                f"duplicates skipped: {self.stats['duplicates_skipped']}, "
                f"output fields: {sorted(list(self.known_output_fields))})"
            )

            # Save stats periodically
            if self.stats["total_flushes"] % 10 == 0:
                self._save_stats()

        finally:
            self.caption_buffer.clear()
            # Force garbage collection
            gc.collect()

    async def optimize_storage(self):
        """Optimize storage by dropping empty columns. Run this periodically or on-demand."""
        if not self.captions_path.exists():
            logger.info("No captions file to optimize")
            return

        logger.info("Starting storage optimization...")

        # Read the full table
        backup_path = None
        table = pq.read_table(self.captions_path)
        df = table.to_pandas()
        original_columns = len(df.columns)

        # Find non-empty columns (don't preserve empty base fields)
        non_empty_columns = self._get_non_empty_columns(df, preserve_base_fields=False)

        # Always keep at least job_id
        if "job_id" not in non_empty_columns:
            non_empty_columns.append("job_id")

        if len(non_empty_columns) < original_columns:
            # We have columns to drop
            df_optimized = df[non_empty_columns]

            # Rebuild schema for non-empty columns only
            base_field_names = {f[0] for f in self.base_caption_fields}
            fields = []
            output_fields = set()

            # Process columns in a consistent order: base fields first, then output fields
            for col in non_empty_columns:
                if col in base_field_names:
                    # Find the base field definition
                    for fname, ftype in self.base_caption_fields:
                        if fname == col:
                            fields.append((fname, ftype))
                            break
                else:
                    # Output field
                    output_fields.add(col)

            # Add output fields in sorted order
            for field_name in sorted(output_fields):
                fields.append((field_name, pa.list_(pa.string())))

            # Create optimized schema and table
            optimized_schema = pa.schema(fields)
            optimized_table = pa.Table.from_pandas(df_optimized, schema=optimized_schema)

            # Backup the original file (optional)
            backup_path = self.captions_path.with_suffix(".parquet.bak")
            import shutil

            shutil.copy2(self.captions_path, backup_path)

            # Write optimized table
            pq.write_table(optimized_table, self.captions_path, compression="snappy")

            # Update known output fields and recalculate stats
            self.known_output_fields = output_fields

            # Remove dropped fields from stats
            dropped_fields = set(self.stats["field_counts"].keys()) - output_fields
            for field in dropped_fields:
                del self.stats["field_counts"][field]
                if field in self.stats["session_field_counts"]:
                    del self.stats["session_field_counts"][field]

            logger.info(
                f"Storage optimization complete: {original_columns} -> {len(non_empty_columns)} columns. "
                f"Removed columns: {sorted(set(df.columns) - set(non_empty_columns))}"
            )
        else:
            logger.info(f"No optimization needed - all {original_columns} columns contain data")

        # Report file size reduction
        import os

        if backup_path and backup_path.exists():
            original_size = os.path.getsize(backup_path)
            new_size = os.path.getsize(self.captions_path)
            reduction_pct = (1 - new_size / original_size) * 100
            logger.info(
                f"File size: {original_size/1024/1024:.1f}MB -> {new_size/1024/1024:.1f}MB "
                f"({reduction_pct:.1f}% reduction)"
            )

        # Save updated stats
        self._save_stats()

    async def save_contributor(self, contributor: Contributor):
        """Save or update contributor stats - buffers until batch size reached."""
        self.contributor_buffer.append(asdict(contributor))

        if len(self.contributor_buffer) >= self.contributor_buffer_size:
            await self._flush_contributors()

    async def _flush_jobs(self):
        """Write job buffer to parquet."""
        if not self.job_buffer:
            return

        table = pa.Table.from_pylist(self.job_buffer, schema=self.job_schema)

        # For jobs, we need to handle updates (upsert logic)
        if self.jobs_path.exists():
            existing = pq.read_table(self.jobs_path).to_pandas()
            new_df = table.to_pandas()

            # Update existing records or add new ones
            for _, row in new_df.iterrows():
                mask = existing["job_id"] == row["job_id"]
                if mask.any():
                    # Update existing
                    for col in row.index:
                        existing.loc[existing[mask].index, col] = row[col]
                else:
                    # Add new
                    existing = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)

            updated_table = pa.Table.from_pandas(existing, schema=self.job_schema)
            pq.write_table(updated_table, self.jobs_path)
        else:
            pq.write_table(table, self.jobs_path)

        self.job_buffer.clear()
        logger.debug(f"Flushed {len(self.job_buffer)} jobs")

    async def _flush_contributors(self):
        """Write contributor buffer to parquet."""
        if not self.contributor_buffer:
            return

        table = pa.Table.from_pylist(self.contributor_buffer, schema=self.contributor_schema)

        # Handle updates for contributors
        if self.contributors_path.exists():
            existing = pq.read_table(self.contributors_path).to_pandas()
            new_df = table.to_pandas()

            for _, row in new_df.iterrows():
                mask = existing["contributor_id"] == row["contributor_id"]
                if mask.any():
                    for col in row.index:
                        existing.loc[mask, col] = row[col]
                else:
                    existing = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)

            updated_table = pa.Table.from_pandas(existing, schema=self.contributor_schema)
            pq.write_table(updated_table, self.contributors_path)
        else:
            pq.write_table(table, self.contributors_path)

        self.contributor_buffer.clear()

    async def checkpoint(self):
        """Force flush all buffers to disk - called periodically by orchestrator."""
        logger.info(
            f"Checkpoint: Flushing buffers (captions: {len(self.caption_buffer)}, "
            f"jobs: {len(self.job_buffer)}, contributors: {len(self.contributor_buffer)})"
        )

        await self._flush_captions()
        await self._flush_jobs()
        await self._flush_contributors()

        # Save stats on checkpoint
        self._save_stats()

        # Log final rate statistics
        if self.stats["total_captions_written"] > 0:
            rates = self._calculate_rates()
            logger.info(
                f"Checkpoint complete. Total rows: {self.stats['total_captions_written']}, "
                f"Total caption entries: {self.stats['total_caption_entries_written']}, "
                f"Duplicates skipped: {self.stats['duplicates_skipped']} | "
                f"Overall rate: {rates['overall']:.1f} rows/s"
            )
        else:
            logger.info(
                f"Checkpoint complete. Total rows: {self.stats['total_captions_written']}, "
                f"Total caption entries: {self.stats['total_caption_entries_written']}, "
                f"Duplicates skipped: {self.stats['duplicates_skipped']}"
            )

    def get_all_processed_job_ids(self) -> Set[str]:
        """Get all processed job_ids - useful for resumption."""
        # Return the in-memory set which is kept up-to-date
        # Also add any job_ids currently in the buffer
        all_job_ids = self.existing_caption_job_ids.copy()

        for row in self.caption_buffer:
            if "job_id" in row:
                all_job_ids.add(row["job_id"])

        return all_job_ids

    async def get_storage_contents(
        self,
        limit: Optional[int] = None,
        columns: Optional[List[str]] = None,
        include_metadata: bool = True,
    ) -> StorageContents:
        """Retrieve storage contents for export.

        Args:
            limit: Maximum number of rows to retrieve
            columns: Specific columns to include (None for all)
            include_metadata: Whether to include metadata in the result

        Returns:
            StorageContents instance with the requested data
        """
        if not self.captions_path.exists():
            return StorageContents(
                rows=[],
                columns=[],
                output_fields=list(self.known_output_fields),
                total_rows=0,
                metadata={"message": "No captions file found"},
            )

        # Flush buffers first to ensure all data is on disk
        await self.checkpoint()

        # Determine columns to read
        if columns:
            # Validate requested columns exist
            table_metadata = pq.read_metadata(self.captions_path)
            available_columns = set(table_metadata.schema.names)
            invalid_columns = set(columns) - available_columns
            if invalid_columns:
                raise ValueError(f"Columns not found: {invalid_columns}")
            columns_to_read = columns
        else:
            # Read all columns
            columns_to_read = None

        # Read the table
        table = pq.read_table(self.captions_path, columns=columns_to_read)
        df = table.to_pandas()

        # Apply limit if specified
        if limit:
            df = df.head(limit)

        # Convert to list of dicts
        rows = df.to_dict("records")

        # Parse metadata JSON strings back to dicts if present
        if "metadata" in df.columns:
            for row in rows:
                if row.get("metadata"):
                    try:
                        row["metadata"] = json.loads(row["metadata"])
                    except:
                        pass  # Keep as string if parsing fails

        # Prepare metadata
        metadata = {}
        if include_metadata:
            metadata.update(
                {
                    "export_timestamp": pd.Timestamp.now().isoformat(),
                    "total_available_rows": self.stats.get("disk_rows", 0),
                    "rows_exported": len(rows),
                    "storage_path": str(self.captions_path),
                    "field_stats": self.stats.get("field_counts", {}),
                }
            )

        return StorageContents(
            rows=rows,
            columns=list(df.columns),
            output_fields=list(self.known_output_fields),
            total_rows=len(df),
            metadata=metadata,
        )

    async def get_processed_jobs_for_chunk(self, chunk_id: str) -> Set[str]:
        """Get all processed job_ids for a given chunk."""
        if not self.captions_path.exists():
            return set()

        # Read only job_id and chunk_id columns
        table = pq.read_table(self.captions_path, columns=["job_id", "chunk_id"])
        df = table.to_pandas()

        # Filter by chunk_id and return job_ids
        chunk_jobs = df[df["chunk_id"] == chunk_id]["job_id"].tolist()
        return set(chunk_jobs)

    async def get_caption_stats(self) -> Dict[str, Any]:
        """Get statistics about stored captions from cached values."""
        total_rows = self.stats["disk_rows"] + len(self.caption_buffer)

        # Count outputs in buffer
        buffer_outputs = 0
        buffer_field_counts = defaultdict(int)
        for row in self.caption_buffer:
            for field_name in self.known_output_fields:
                if field_name in row and isinstance(row[field_name], list):
                    count = len(row[field_name])
                    buffer_outputs += count
                    buffer_field_counts[field_name] += count

        # Merge buffer counts with disk counts
        field_stats = {}
        for field_name in self.known_output_fields:
            disk_count = self.stats["field_counts"].get(field_name, 0)
            buffer_count = buffer_field_counts.get(field_name, 0)
            total_count = disk_count + buffer_count

            if total_count > 0:
                field_stats[field_name] = {
                    "total_items": total_count,
                    "disk_items": disk_count,
                    "buffer_items": buffer_count,
                }

        total_outputs = self.stats["disk_outputs"] + buffer_outputs

        return {
            "total_rows": total_rows,
            "total_outputs": total_outputs,
            "output_fields": sorted(list(self.known_output_fields)),
            "field_stats": field_stats,
        }

    async def count_captions(self) -> int:
        """Count total outputs across all dynamic fields from cached values."""
        # Use cached disk count
        total = self.stats["disk_outputs"]

        # Add buffer counts
        for row in self.caption_buffer:
            for field_name in self.known_output_fields:
                if field_name in row and isinstance(row[field_name], list):
                    total += len(row[field_name])

        return total

    async def count_caption_rows(self) -> int:
        """Count total rows from cached values."""
        return self.stats["disk_rows"] + len(self.caption_buffer)

    async def get_contributor(self, contributor_id: str) -> Optional[Contributor]:
        """Retrieve a contributor by ID."""
        # Check buffer first
        for buffered in self.contributor_buffer:
            if buffered["contributor_id"] == contributor_id:
                return Contributor(**buffered)

        if not self.contributors_path.exists():
            return None

        table = pq.read_table(self.contributors_path)
        df = table.to_pandas()

        row = df[df["contributor_id"] == contributor_id]
        if row.empty:
            return None

        return Contributor(
            contributor_id=row.iloc[0]["contributor_id"],
            name=row.iloc[0]["name"],
            total_captions=int(row.iloc[0]["total_captions"]),
            trust_level=int(row.iloc[0]["trust_level"]),
        )

    async def get_top_contributors(self, limit: int = 10) -> List[Contributor]:
        """Get top contributors by caption count."""
        contributors = []

        if self.contributors_path.exists():
            table = pq.read_table(self.contributors_path)
            df = table.to_pandas()

            # Sort by total_captions descending
            df = df.sort_values("total_captions", ascending=False).head(limit)

            for _, row in df.iterrows():
                contributors.append(
                    Contributor(
                        contributor_id=row["contributor_id"],
                        name=row["name"],
                        total_captions=int(row["total_captions"]),
                        trust_level=int(row["trust_level"]),
                    )
                )

        return contributors

    async def get_output_field_stats(self) -> Dict[str, Any]:
        """Get statistics about output fields from cached values."""
        # Combine disk and buffer stats
        field_counts = self.stats["field_counts"].copy()

        # Add buffer counts
        for row in self.caption_buffer:
            for field_name in self.known_output_fields:
                if field_name in row and isinstance(row[field_name], list):
                    if field_name not in field_counts:
                        field_counts[field_name] = 0
                    field_counts[field_name] += len(row[field_name])

        total_outputs = sum(field_counts.values())

        return {
            "total_fields": len(field_counts),
            "field_counts": field_counts,
            "total_outputs": total_outputs,
            "fields": sorted(list(field_counts.keys())),
        }

    async def close(self):
        """Close storage and flush buffers."""
        await self.checkpoint()

        # Log final rate statistics
        if self.stats["total_captions_written"] > 0:
            rates = self._calculate_rates()
            logger.info(
                f"Storage closed. Total rows: {self.stats['total_captions_written']}, "
                f"Total caption entries: {self.stats['total_caption_entries_written']}, "
                f"Duplicates skipped: {self.stats['duplicates_skipped']} | "
                f"Final rates - Overall: {rates['overall']:.1f} rows/s, "
                f"Last hour: {rates['60min']:.1f} rows/s"
            )
        else:
            logger.info(
                f"Storage closed. Total rows: {self.stats['total_captions_written']}, "
                f"Total caption entries: {self.stats['total_caption_entries_written']}, "
                f"Duplicates skipped: {self.stats['duplicates_skipped']}"
            )

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get all storage-related statistics from cached values."""
        # Count outputs in buffer
        buffer_outputs = 0
        for row in self.caption_buffer:
            for field_name in self.known_output_fields:
                if field_name in row and isinstance(row[field_name], list):
                    buffer_outputs += len(row[field_name])

        # Get field-specific stats
        field_stats = await self.get_caption_stats()
        total_rows_including_buffer = self.stats["disk_rows"] + len(self.caption_buffer)

        # Calculate rates
        rates = self._calculate_rates()

        return {
            "total_captions": self.stats["disk_outputs"] + buffer_outputs,
            "total_rows": total_rows_including_buffer,
            "buffer_size": len(self.caption_buffer),
            "total_written": self.stats["total_captions_written"],
            "total_entries_written": self.stats["total_caption_entries_written"],
            "duplicates_skipped": self.stats["duplicates_skipped"],
            "total_flushes": self.stats["total_flushes"],
            "output_fields": sorted(list(self.known_output_fields)),
            "field_breakdown": field_stats.get("field_stats", {}),
            "contributor_buffer_size": len(self.contributor_buffer),
            "rates": {
                "instant": f"{rates['instant']:.1f} rows/s",
                "5min": f"{rates['5min']:.1f} rows/s",
                "15min": f"{rates['15min']:.1f} rows/s",
                "60min": f"{rates['60min']:.1f} rows/s",
                "overall": f"{rates['overall']:.1f} rows/s",
            },
        }
