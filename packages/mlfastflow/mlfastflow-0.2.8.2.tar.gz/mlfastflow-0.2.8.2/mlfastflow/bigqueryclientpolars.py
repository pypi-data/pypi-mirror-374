from typing import Optional, Dict, List, Any, Union, Tuple
import polars as pl
from google.cloud import bigquery, storage
from google.oauth2 import service_account
from google.api_core import exceptions as google_exceptions
import datetime
import os
from google.api_core import exceptions
import pyarrow
import pyarrow.parquet as pq
from pathlib import Path
import json
import dotenv
import numpy as np # Import numpy for NaN handling
# from graphviz import Digraph

import logging
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import io
# Add this import if you don't have it already for graphviz
try:
    import graphviz
except ImportError:
    graphviz = None # Handle optional dependency

from mlfastflow.utils import timer_decorator # Import the decorator

class BigQueryClientPolars:
    def __init__(
                self,
                project_id: str,
                dataset_id: str,
                key_file: str
                ):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.key_file = key_file

        self.client = None
        self.credentials = None
        self.job_config = None
        self.full_table_id = None
        self.sql = None
        self.bucket_name = None # Initialize bucket_name
        self.output_path = None # Initialize output_path

        self.default_path = Path('/tmp/data/bigquery/')
        if not self.default_path.exists():
            self.default_path.mkdir(parents=True)

        if self.key_file:
            self.credentials = service_account.Credentials.from_service_account_file(
                self.key_file,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            self.client = bigquery.Client(
                credentials=self.credentials,
                project=self.credentials.project_id,
            )


    def get_client(self):
        return BigQueryClientPolars(
            self.project_id,
            self.dataset_id,
            self.key_file
        )

    def show(self) -> None:
        # Use a consistent format for better readability
        config_info = {
            "GCP Configuration": {
                "Project ID": self.project_id,
                "Dataset ID": self.dataset_id,
                "Bucket Name": self.bucket_name or "Not set"
            },
            "Client Status": {
                "BigQuery Client": "Initialized" if self.client else "Not initialized",
                "Credentials": "Set" if self.credentials else "Not set"
            },
            "File Configuration": {
                "Default Path": str(self.default_path),
                "Key File": self.key_file or "Not set",
                "Output Path": str(self.output_path) if self.output_path else "Not set"
            }
        }

        # Print with clear section formatting
        for section, details in config_info.items():
            print(f"\n{section}:")
            print("-" * (len(section) + 1))
            for key, value in details.items():
                print(f"{key:15}: {value}")


    def close(self) -> bool:
        """Close the BigQuery client and clean up resources.

        This method ensures proper cleanup of the BigQuery client connection
        and associated resources. If no client exists, it will return silently.

        The method will attempt to clean up all resources even if an error occurs
        during client closure.

        Returns:
            bool: True if cleanup was successful, False if an error occurred
        """
        # Early return if there's no client to close
        if not hasattr(self, 'client') or self.client is None:
            return True

        success = True

        try:
            self.client.close()
        except Exception as e:
            print(f"Warning: Error while closing client: {str(e)}")
            success = False
        finally:
            # Define all attributes to reset in a list for maintainability
            attrs_to_reset = [
                'client', 'credentials', 'job_config',
                'sql', 'bucket_name', 'default_path', 'output_path'
            ]

            # Reset all attributes to None
            for attr in attrs_to_reset:
                if hasattr(self, attr):
                    setattr(self, attr, None)

        # Provide user feedback after cleanup
        if success:
            print("BigQuery client closed successfully.")
        else:
            print("BigQuery client encountered errors during closure.")

        return success


    def __del__(self):
        """Destructor to ensure proper cleanup of resources."""
        self.close()


    def fix_mixed_types(self,
                        df: pl.DataFrame,
                        columns: Optional[List[str]] = None,
                        strategy: str = 'infer',
                        numeric_errors: str = 'coerce') -> pl.DataFrame:
        """
        Attempts to resolve mixed data types within specified DataFrame columns.

        Mixed types often occur in columns with inconsistent data and can cause issues
        when uploading to databases like BigQuery which require consistent types.

        Args:
            df (pl.DataFrame): The DataFrame to process.
            columns (Optional[List[str]]): A list of column names to check.
                                           If None, checks all columns. Defaults to None.
            strategy (str): The method to use for fixing types:
                            - 'infer': (Default) Tries to convert columns to numeric.
                                       If successful, keeps the numeric type. If not,
                                       converts the column to string.
                            - 'to_string': Converts specified columns unconditionally to strings.
            numeric_errors (str): How numeric conversion handles parsing errors
                                  (only relevant for 'infer' strategy).
                                  Defaults to 'coerce' (errors become null).

        Returns:
            pl.DataFrame: A new DataFrame with potentially fixed data types.

        Raises:
            ValueError: If an invalid strategy is provided.
        """
        if strategy not in ['infer', 'to_string']:
            raise ValueError("strategy must be either 'infer' or 'to_string'")

        # Create a copy to avoid modifying the original
        df_copy = df.clone()
        cols_to_check = columns if columns is not None else df_copy.columns

        print(f"Starting mixed type check with strategy: '{strategy}'...")
        fixed_cols = []

        for col in cols_to_check:
            if col not in df_copy.columns:
                print(f"Warning: Column '{col}' not found in DataFrame. Skipping.")
                continue

            # Get original dtype information
            original_dtype = str(df_copy.schema[col])
            
            try:
                if strategy == 'infer':
                    # Try to infer numeric type
                    try:
                        # Attempt numeric conversion
                        if numeric_errors == 'coerce':
                            # With coerce, errors become null values
                            df_copy = df_copy.with_columns(
                                pl.col(col).cast(pl.Float64, strict=False).alias(col)
                            )
                        else:
                            # Without coerce, strict casting is applied
                            df_copy = df_copy.with_columns(
                                pl.col(col).cast(pl.Float64, strict=True).alias(col)
                            )
                        
                        # Check if successfully converted to numeric
                        new_dtype = str(df_copy.schema[col])
                        if new_dtype != original_dtype:
                            print(f"  Column '{col}': Converted from {original_dtype} to {new_dtype}.")
                            fixed_cols.append(col)
                    
                    except Exception:
                        # Numeric conversion failed, convert to string
                        df_copy = df_copy.with_columns(
                            pl.col(col).cast(pl.Utf8).alias(col)
                        )
                        new_dtype = str(df_copy.schema[col])
                        if new_dtype != original_dtype:
                            print(f"  Column '{col}': Could not infer numeric type, converted from {original_dtype} to {new_dtype}.")
                            fixed_cols.append(col)
                    
                elif strategy == 'to_string':
                    # Unconditionally convert to string
                    df_copy = df_copy.with_columns(
                        pl.col(col).cast(pl.Utf8).alias(col)
                    )
                    new_dtype = str(df_copy.schema[col])
                    if new_dtype != original_dtype:
                        print(f"  Column '{col}': Forced conversion from {original_dtype} to {new_dtype}.")
                        fixed_cols.append(col)

            except Exception as e:
                print(f"  Error processing column '{col}': {str(e)}. Leaving as is.")

        if fixed_cols:
            print(f"Finished mixed type check. Columns modified: {fixed_cols}")
        else:
            print("Finished mixed type check. No columns required changes based on selected strategy.")

        return df_copy

    @timer_decorator
    def run_sql(self, sql: str) -> None:
        if sql is None:
            raise ValueError("sql must be a non-empty string")

        # Check if SQL contains DELETE or TRUNCATE operations
        sql_upper = sql.upper()
        if "DELETE" in sql_upper or "TRUNCATE" in sql_upper:
            print("ERROR: Cannot execute DELETE or TRUNCATE operations for safety reasons")
            return

        try:
            self.client.query(sql)
            print("Query run complete")
        except Exception as e:
            print(f"Error running query: {str(e)}")

    @timer_decorator
    def sql2df(self, sql: str = None) -> Optional[pl.DataFrame]:
        """Execute SQL query and return results as a Polars DataFrame.
        
        Args:
            sql: SQL query string to execute
            
        Returns:
            Polars DataFrame with query results, or None if query fails
            
        Raises:
            ValueError: If sql is None or empty
            RuntimeError: If sql contains potentially destructive operations
        """
        if sql is None or not sql.strip():
            raise ValueError("sql must be a non-empty string")

        # Check for potentially destructive SQL operations
        sql_clean = ' '.join(sql.split())  # Normalize whitespace
        sql_upper = sql_clean.upper()
        
        destructive_operations = [
            'DELETE', 'TRUNCATE', 'DROP', 'ALTER', 'CREATE', 'INSERT', 
            'UPDATE', 'MERGE', 'REPLACE'
        ]
        
        for operation in destructive_operations:
            if f' {operation} ' in f' {sql_upper} ' or sql_upper.startswith(f'{operation} '):
                raise RuntimeError(f"Cannot execute {operation} operations for safety reasons")

        try:
            query_job = self.client.query(sql)
            # Get the query result as an Arrow table directly
            arrow_table = query_job.to_arrow()
            # Convert the Arrow table to a polars DataFrame
            return pl.from_arrow(arrow_table)
        except Exception as e:
            print(f"Error running query: {str(e)}")
            return None

    def sql2lf(self, sql: str) -> pl.LazyFrame:
        """Execute SQL query and return results as a Polars LazyFrame.
        
        This is a convenience method that calls sql2df() and converts the result to LazyFrame.
        
        Args:
            sql: SQL query string to execute
            
        Returns:
            Polars LazyFrame with query results
            
        Raises:
            ValueError: If sql is None or empty
            RuntimeError: If sql contains potentially destructive operations
            Exception: If query execution fails
        """
        df = self.sql2df(sql)
        if df is None:
            raise Exception("Query execution failed")
        return df.lazy()

    @timer_decorator
    def sql2parquet(self, sql: str, destination_path: str, 
                   compression: str = 'snappy',
                   streaming: bool = True,
                   row_group_size: Optional[int] = 1000000) -> bool:
        """Execute SQL query and save results as a Parquet file using Polars streaming.
        
        This method uses Polars LazyFrame with streaming for memory-efficient processing
        of large datasets that may not fit in memory.
        
        Args:
            sql: SQL query string to execute
            destination_path: Local file path where the Parquet file will be saved
            compression: Compression algorithm ('snappy', 'zstd', 'gzip', 'lz4', 'brotli')
            streaming: Whether to use streaming mode for memory efficiency
            row_group_size: Number of rows per row group (affects memory usage and query performance)
            
        Returns:
            bool: True if the operation was successful, False otherwise
            
        Raises:
            ValueError: If sql is None or empty
            RuntimeError: If sql contains potentially destructive operations
        """
        if sql is None or not sql.strip():
            raise ValueError("sql must be a non-empty string")

        # Check for potentially destructive SQL operations
        sql_clean = ' '.join(sql.split())  # Normalize whitespace
        sql_upper = sql_clean.upper()
        
        destructive_operations = [
            'DELETE', 'TRUNCATE', 'DROP', 'ALTER', 'CREATE', 'INSERT', 
            'UPDATE', 'MERGE', 'REPLACE'
        ]
        
        for operation in destructive_operations:
            if f' {operation} ' in f' {sql_upper} ' or sql_upper.startswith(f'{operation} '):
                raise RuntimeError(f"Cannot execute {operation} operations for safety reasons")

        try:
            # Execute query and get Arrow table
            query_job = self.client.query(sql)
            arrow_table = query_job.to_arrow()
            
            # Convert to Polars DataFrame then LazyFrame for streaming operations
            df = pl.from_arrow(arrow_table)
            lazy_df = df.lazy()
            
            # Use streaming sink for memory-efficient writing
            if streaming:
                lazy_df.sink_parquet(
                    destination_path,
                    compression=compression,
                    row_group_size=row_group_size,
                    statistics=True  # Enable statistics for better query performance
                )
            else:
                # For smaller datasets, collect and write normally
                df_collected = lazy_df.collect()
                df_collected.write_parquet(
                    destination_path,
                    compression=compression,
                    row_group_size=row_group_size,
                    statistics=True
                )
            
            print(f"Successfully saved query results to {destination_path}")
            print(f"Rows processed: {df.height}")
            return True
            
        except Exception as e:
            print(f"Error executing query and saving to Parquet: {str(e)}")
            return False

    @timer_decorator
    def df2table(self, df: pl.DataFrame,
                 table_id: str,
                 if_exists: str = 'fail',
                 schema: Optional[List[Dict[str, Any]]] = None,
                 fix_types: bool = False,
                 fix_types_strategy: str = 'infer',
                 chunk_size: Optional[int] = None
                 ) -> bool:
        """
        Upload a polars DataFrame to a BigQuery table.

        Args:
            df (pl.DataFrame): The DataFrame to upload (can be lazy or eager)
            table_id (str): Target table ID
            if_exists (str): Action if table exists: 'fail', 'replace', or 'append'
            schema (Optional[List[Dict[str, Any]]]): BigQuery schema for the table
            fix_types (bool): If True, run the `fix_mixed_types` method before uploading.
                              Defaults to False.
            fix_types_strategy (str): Strategy to use if `fix_types` is True ('infer' or 'to_string').
                                      Defaults to 'infer'.
            chunk_size (Optional[int]): Process DataFrame in chunks for large datasets

        Returns:
            bool: True if upload was successful, False otherwise

        Raises:
            ValueError: If DataFrame is empty or parameters are invalid
        """
        # Input validation - handle both lazy and eager DataFrames
        if df is None:
            raise ValueError("DataFrame cannot be None")
            
        # Convert LazyFrame to DataFrame if needed for validation
        if isinstance(df, pl.LazyFrame):
            try:
                # Use streaming for large datasets
                df_eager = df.collect(streaming=True)
            except Exception as e:
                print(f"Error collecting LazyFrame: {e}")
                return False
        else:
            df_eager = df

        # Check if DataFrame is empty using Polars-idiomatic method
        if df_eager.height == 0:
            raise ValueError("DataFrame cannot be empty")

        if if_exists not in ('fail', 'replace', 'append'):
            raise ValueError("if_exists must be one of: 'fail', 'replace', 'append'")

        # --- Fix mixed types if requested ---
        if fix_types:
            print("Attempting to fix mixed data types before upload...")
            try:
                df_eager = self.fix_mixed_types(df_eager, strategy=fix_types_strategy)
            except Exception as e:
                print(f"Error during type fixing: {e}. Proceeding with original types.")
        # ------------------------------------

        # Set target table
        target_table_id = table_id
        if not target_table_id:
            raise ValueError("No table_id provided")

        # Construct full table ID
        full_table_id = f"{self.dataset_id}.{target_table_id}"

        try:
            # Handle large DataFrames with chunking
            if chunk_size and df_eager.height > chunk_size:
                return self._upload_in_chunks(df_eager, full_table_id, if_exists, schema, chunk_size)
            
            # Convert polars DataFrame to pyarrow table efficiently
            # Use rechunk() to optimize memory layout before conversion
            arrow_table = df_eager.rechunk().to_arrow()
            
            # Validate Arrow table before upload
            if arrow_table.num_rows == 0:
                raise ValueError("Converted Arrow table is empty")
            
            # Configure load job
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.PARQUET,
                write_disposition={
                    'fail': bigquery.WriteDisposition.WRITE_EMPTY,
                    'replace': bigquery.WriteDisposition.WRITE_TRUNCATE,
                    'append': bigquery.WriteDisposition.WRITE_APPEND
                }[if_exists]
            )
            
            # Apply schema if provided
            if schema is not None:
                from google.cloud.bigquery import SchemaField
                # Convert schema dict to SchemaField objects if needed
                if isinstance(schema[0], dict):
                    bq_schema = [SchemaField.from_api_repr(field) for field in schema]
                else:
                    bq_schema = schema
                job_config.schema = bq_schema
            
            # Create a buffer to store parquet data
            buffer = io.BytesIO()
            # Write the Arrow table to the buffer in Parquet format with compression
            pq.write_table(arrow_table, buffer, compression='snappy')
            # Set the buffer position to the beginning
            buffer.seek(0)
            
            # Start the load job
            load_job = self.client.load_table_from_file(
                buffer,
                full_table_id,
                job_config=job_config
            )
            
            # Wait for the job to complete
            load_job.result()
            
            destination_table = self.client.get_table(full_table_id)
            print(f"Successfully uploaded {df_eager.height} rows to {self.project_id}.{full_table_id}")
            return True

        except Exception as e:
            print(f"Error uploading DataFrame to BigQuery: {str(e)}")
            # Provide more context if it's likely a type error after attempting fix
            if fix_types and isinstance(e, google_exceptions.BadRequest):
                 print("Hint: This error might be related to data types even after attempting to fix them.")
                 print("Consider using fix_types_strategy='to_string' or providing an explicit 'schema'.")
            return False

    def _upload_in_chunks(self, df: pl.DataFrame, full_table_id: str, if_exists: str, 
                         schema: Optional[List[Dict[str, Any]]], chunk_size: int) -> bool:
        """Helper method to upload large DataFrames in chunks."""
        total_rows = df.height
        chunks_uploaded = 0
        
        for i in range(0, total_rows, chunk_size):
            chunk = df.slice(i, chunk_size)
            chunk_if_exists = 'append' if chunks_uploaded > 0 else if_exists
            
            success = self.df2table(
                chunk, 
                full_table_id.split('.')[-1],  # Extract table name
                if_exists=chunk_if_exists,
                schema=schema if chunks_uploaded == 0 else None,  # Only set schema on first chunk
                fix_types=False  # Already fixed in parent call
            )
            
            if not success:
                print(f"Failed to upload chunk {chunks_uploaded + 1}")
                return False
                
            chunks_uploaded += 1
            print(f"Uploaded chunk {chunks_uploaded}/{(total_rows + chunk_size - 1) // chunk_size}")
        
        return True

    def sql2gcs(self, sql: str,
                           destination_uri: str,
                           format: str = 'PARQUET',
                           compression: str = 'SNAPPY',
                           create_temp_table: bool = True,
                           wait_for_completion: bool = True,
                           timeout: int = 300,
                           use_sharding: bool = True) -> bool:
        """
        Export BigQuery query results directly to Google Cloud Storage without downloading data locally.
        This uses BigQuery's extract job functionality for efficient data transfer.

        Args:
            sql (str): The SQL query to execute
            destination_uri (str): GCS URI to export to (e.g., 'gs://bucket-name/path/to/file')
                                  For large datasets, use a wildcard pattern like 'gs://bucket-name/path/to/file-*.parquet'
                                  or set use_sharding=True to automatically add the wildcard
            format (str): Export format ('PARQUET', 'CSV', 'JSON', 'AVRO')
            compression (str): Compression type ('NONE', 'GZIP', 'SNAPPY', 'DEFLATE')
            create_temp_table (bool): Whether to create a temporary table for the results
            wait_for_completion (bool): Whether to wait for the export job to complete
            timeout (int): Timeout in seconds for waiting for job completion
            use_sharding (bool): Whether to use sharded export with wildcards. If True and destination_uri doesn't
                                contain wildcards, '-*.ext' will be added before the extension.

        Returns:
            bool: True if export was successful, False otherwise
        """
        # Input validation
        if sql is None or not sql.strip():
            raise ValueError("SQL query cannot be None or empty")

        if not destination_uri or not destination_uri.startswith('gs://'):
            raise ValueError("Destination URI must be a valid GCS path starting with 'gs://'")

        # Validate format and compression
        format = format.upper()
        compression = compression.upper()

        valid_formats = ['PARQUET', 'CSV', 'JSON', 'AVRO']
        valid_compressions = ['NONE', 'GZIP', 'SNAPPY', 'DEFLATE']

        if format not in valid_formats:
            raise ValueError(f"Format must be one of {valid_formats}")

        if compression not in valid_compressions:
            raise ValueError(f"Compression must be one of {valid_compressions}")

        # Check if sharding is needed and add a wildcard pattern if necessary
        if use_sharding and '*' not in destination_uri:
            # Extract file extension if any
            file_extension = ''
            if '.' in destination_uri.split('/')[-1]:
                base_name, file_extension = os.path.splitext(destination_uri)
                destination_uri = f"{base_name}-*{file_extension}"
            else:
                # No extension, just add the wildcard at the end
                destination_uri = f"{destination_uri}-*"

            print(f"Enabled sharding with destination URI: {destination_uri}")

        try:
            # BigQuery extract job requires a table as the source, not a query directly
            # So we first need to either run the query to a destination table or use a temporary table

            if create_temp_table:
                # Create a temporary table to hold the query results
                temp_table_id = f"temp_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}" # Added microseconds for uniqueness
                temp_table_ref = f"{self.project_id}.{self.dataset_id}.{temp_table_id}"

                print(f"Creating temporary table {temp_table_ref} for query results...")

                # Create a job config for the query
                job_config = bigquery.QueryJobConfig(
                    destination=temp_table_ref,
                    write_disposition="WRITE_TRUNCATE"
                )

                # Run the query to the temporary table
                query_job = self.client.query(sql, job_config=job_config)
                query_job.result()  # Wait for query to complete

                print(f"Query executed successfully, results stored in temporary table")

                # Now set up the source table for the extract job
                source_table = self.client.get_table(temp_table_ref)
            else:
                # When not using a temporary table, we need to create a destination table
                # in a different way as RowIterator doesn't have a .table attribute
                print("Running query and creating temporary destination...")

                # Generate a unique job ID
                job_id = f"export_job_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}" # Added microseconds

                # Create a destination table with a temporary name
                temp_table_id = f"temp_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}" # Added microseconds
                temp_table_ref = f"{self.project_id}.{self.dataset_id}.{temp_table_id}"

                # Configure the query job with the destination
                job_config = bigquery.QueryJobConfig(
                    destination=temp_table_ref,
                    write_disposition="WRITE_TRUNCATE"
                )

                # Run the query
                query_job = self.client.query(
                    sql,
                    job_config=job_config,
                    job_id=job_id
                )

                # Wait for query to complete
                query_job.result()

                # Get the destination table reference
                source_table = self.client.get_table(temp_table_ref)

                print(f"Query executed successfully, temporary results available")

            # Configure the extract job
            extract_job_config = bigquery.ExtractJobConfig()
            extract_job_config.destination_format = format

            # Set compression if not NONE
            if compression != 'NONE':
                extract_job_config.compression = compression

            # Start the extract job
            print(f"Starting extract job to {destination_uri}")
            extract_job = self.client.extract_table(
                source_table,
                destination_uri,
                job_config=extract_job_config
            )

            # Wait for the job to complete if requested
            if wait_for_completion:
                print(f"Waiting for extract job to complete (timeout: {timeout} seconds)...")
                extract_job.result(timeout=timeout)  # Wait for the job to finish and raises an exception if fails

                print(f"Extract job completed successfully")

                # Clean up temporary table if created (whether explicitly or implicitly)
                print(f"Cleaning up temporary table {temp_table_ref}")
                try:
                    self.client.delete_table(temp_table_ref, not_found_ok=True) # Add not_found_ok
                except Exception as cleanup_e:
                    print(f"Warning: Failed to clean up temporary table {temp_table_ref}: {cleanup_e}")


            else:
                print(f"Extract job started (job_id: {extract_job.job_id})")
                print(f"You can check the job status in the BigQuery console")
                # Note: If not waiting, the temporary table won't be cleaned up here.

            return True

        except Exception as e:
            print(f"Error exporting query results to GCS: {str(e)}")
            # Attempt cleanup even on error if temp table ref exists
            if 'temp_table_ref' in locals() and temp_table_ref:
                 print(f"Attempting cleanup of temporary table {temp_table_ref} after error...")
                 try:
                     self.client.delete_table(temp_table_ref, not_found_ok=True)
                 except Exception as cleanup_e:
                     print(f"Warning: Failed to clean up temporary table {temp_table_ref} after error: {cleanup_e}")
            return False
            
    def df2gcs(self, df: 'pl.DataFrame',
               destination_uri: str,
               format: str = 'PARQUET',
               compression: str = 'SNAPPY',
               wait_for_completion: bool = True,
               timeout: int = 300,
               use_sharding: bool = True) -> bool:
        """
        Export a Polars DataFrame directly to Google Cloud Storage using BigQuery as an intermediary.
        This loads the DataFrame to a temporary BigQuery table and then uses BigQuery's extract job
        functionality for efficient data transfer to GCS.

        Args:
            df (pl.DataFrame): The Polars DataFrame to export
            destination_uri (str): GCS URI to export to (e.g., 'gs://bucket-name/path/to/file')
                                  For large datasets, use a wildcard pattern like 'gs://bucket-name/path/to/file-*.parquet'
                                  or set use_sharding=True to automatically add the wildcard
            format (str): Export format ('PARQUET', 'CSV', 'JSON', 'AVRO')
            compression (str): Compression type ('NONE', 'GZIP', 'SNAPPY', 'DEFLATE')
            wait_for_completion (bool): Whether to wait for the export job to complete
            timeout (int): Timeout in seconds for waiting for job completion
            use_sharding (bool): Whether to use sharded export with wildcards. If True and destination_uri doesn't
                                contain wildcards, '-*.ext' will be added before the extension.

        Returns:
            bool: True if export was successful, False otherwise
        """
        # Input validation
        if df is None or len(df) == 0:
            raise ValueError("DataFrame cannot be None or empty")

        if not destination_uri or not destination_uri.startswith('gs://'):
            raise ValueError("Destination URI must be a valid GCS path starting with 'gs://'")

        # Validate format and compression
        format = format.upper()
        compression = compression.upper()

        valid_formats = ['PARQUET', 'CSV', 'JSON', 'AVRO']
        valid_compressions = ['NONE', 'GZIP', 'SNAPPY', 'DEFLATE']

        if format not in valid_formats:
            raise ValueError(f"Format must be one of {valid_formats}")

        if compression not in valid_compressions:
            raise ValueError(f"Compression must be one of {valid_compressions}")

        # Check if sharding is needed and add a wildcard pattern if necessary
        if use_sharding and '*' not in destination_uri:
            # Extract file extension if any
            file_extension = ''
            if '.' in destination_uri.split('/')[-1]:
                base_name, file_extension = os.path.splitext(destination_uri)
                destination_uri = f"{base_name}-*{file_extension}"
            else:
                # No extension, just add the wildcard at the end
                destination_uri = f"{destination_uri}-*"

            print(f"Enabled sharding with destination URI: {destination_uri}")

        try:
            # Create a temporary table to hold the DataFrame
            temp_table_id = f"temp_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"  # Added microseconds for uniqueness
            temp_table_ref = f"{self.project_id}.{self.dataset_id}.{temp_table_id}"

            print(f"Creating temporary table {temp_table_ref} for DataFrame...")

            # Convert Polars DataFrame to pandas for upload to BigQuery
            # (BigQuery's client library works with pandas DataFrames)
            pandas_df = df.to_pandas()

            # Configure job for loading the DataFrame to BigQuery
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_TRUNCATE"
            )

            # Load the DataFrame to the temporary BigQuery table
            load_job = self.client.load_table_from_dataframe(
                pandas_df, 
                temp_table_ref,
                job_config=job_config
            )
            load_job.result()  # Wait for the load job to complete

            print(f"DataFrame loaded successfully to temporary table")

            # Get the table reference for the extract job
            source_table = self.client.get_table(temp_table_ref)

            # Configure the extract job
            extract_job_config = bigquery.ExtractJobConfig()
            extract_job_config.destination_format = format

            # Set compression if not NONE
            if compression != 'NONE':
                extract_job_config.compression = compression

            # Start the extract job
            print(f"Starting extract job to {destination_uri}")
            extract_job = self.client.extract_table(
                source_table,
                destination_uri,
                job_config=extract_job_config
            )

            # Wait for the job to complete if requested
            if wait_for_completion:
                print(f"Waiting for extract job to complete (timeout: {timeout} seconds)...")
                extract_job.result(timeout=timeout)  # Wait for the job to finish and raises an exception if fails

                print(f"Extract job completed successfully")

                # Clean up temporary table
                print(f"Cleaning up temporary table {temp_table_ref}")
                try:
                    self.client.delete_table(temp_table_ref, not_found_ok=True)
                except Exception as cleanup_e:
                    print(f"Warning: Failed to clean up temporary table {temp_table_ref}: {cleanup_e}")
            else:
                print(f"Extract job started (job_id: {extract_job.job_id})")
                print(f"You can check the job status in the BigQuery console")
                # Note: If not waiting, the temporary table won't be cleaned up here.

            return True

        except Exception as e:
            print(f"Error exporting DataFrame to GCS: {str(e)}")
            # Attempt cleanup even on error if temp table ref exists
            if 'temp_table_ref' in locals() and temp_table_ref:
                print(f"Attempting cleanup of temporary table {temp_table_ref} after error...")
                try:
                    self.client.delete_table(temp_table_ref, not_found_ok=True)
                except Exception as cleanup_e:
                    print(f"Warning: Failed to clean up temporary table {temp_table_ref} after error: {cleanup_e}")
            return False


    def gcs2table(self, gcs_uri: str,
                 table_id: str,
                 schema: Optional[List] = None,
                 write_disposition: str = 'WRITE_EMPTY',
                 source_format: str = 'PARQUET',
                 allow_jagged_rows: bool = False,
                 ignore_unknown_values: bool = False,
                 max_bad_records: int = 0) -> bool:
        """
        Loads data from Google Cloud Storage directly into a BigQuery table.
        Uses GCP's native loading capabilities without requiring local resources.

        Args:
            gcs_uri: URI of the GCS source file(s) (
                    e.g., 'gs://bucket/folder/file.parquet'
                    or 'gs://bucket/folder/files-*.csv'
                    or 'gs://bucket/folder/*'
                    )
            table_id: Destination table ID in format 'dataset.table_name' or fully qualified
                     'project.dataset.table_name'
            schema: Optional table schema as a list of SchemaField objects.
                   If None, schema is auto-detected (except for CSV).
            write_disposition: How to handle existing data in the table, one of:
                              'WRITE_TRUNCATE' (default): Overwrite the table
                              'WRITE_APPEND': Append to the table
                              'WRITE_EMPTY': Only write if table is empty
            source_format: Format of the source data, one of:
                          'PARQUET' (default), 'CSV', 'JSON', 'AVRO', 'ORC'
            allow_jagged_rows: For CSV only. Allow missing trailing optional columns.
            ignore_unknown_values: Ignore values that don't match schema.
            max_bad_records: Max number of bad records allowed before job fails.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from google.cloud.bigquery import LoadJobConfig, SourceFormat, SchemaField
            from google.cloud.bigquery.job import WriteDisposition

            # Parse write_disposition and source_format
            write_modes = {
                'WRITE_TRUNCATE': WriteDisposition.WRITE_TRUNCATE,
                'WRITE_APPEND': WriteDisposition.WRITE_APPEND,
                'WRITE_EMPTY': WriteDisposition.WRITE_EMPTY,
            }

            formats = {
                'PARQUET': SourceFormat.PARQUET,
                'CSV': SourceFormat.CSV,
                'JSON': SourceFormat.NEWLINE_DELIMITED_JSON,
                'AVRO': SourceFormat.AVRO,
                'ORC': SourceFormat.ORC,
            }

            # Validate inputs
            if write_disposition not in write_modes:
                raise ValueError(f"write_disposition must be one of: {', '.join(write_modes.keys())}")
            if source_format not in formats:
                raise ValueError(f"source_format must be one of: {', '.join(formats.keys())}")

            # Set up job configuration
            job_config = LoadJobConfig()
            job_config.write_disposition = write_modes[write_disposition]
            job_config.source_format = formats[source_format]

            # Set schema if provided, otherwise auto-detect (except for CSV)
            if schema is not None:
                 # Ensure schema is list of SchemaField objects if provided
                 if not all(isinstance(field, SchemaField) for field in schema):
                     # Attempt conversion if list of dicts provided
                     try:
                         schema = [SchemaField.from_api_repr(field) for field in schema]
                         job_config.schema = schema
                     except Exception as schema_e:
                         raise ValueError(f"Invalid schema format provided. Must be list of bigquery.SchemaField or compatible dicts. Error: {schema_e}")
                 else:
                    job_config.schema = schema
            elif source_format == 'CSV':
                # CSV requires a schema or autodetect
                job_config.autodetect = True
                print("Schema not provided for CSV, enabling autodetect.")
            else:
                job_config.autodetect = True

            # Additional settings
            if source_format == 'CSV':
                job_config.allow_jagged_rows = allow_jagged_rows
                job_config.skip_leading_rows = 1  # Assume header by default for CSV
                print("Assuming first row is header for CSV source.")

            job_config.ignore_unknown_values = ignore_unknown_values
            job_config.max_bad_records = max_bad_records

            # Fully qualify the table_id if needed
            if '.' not in table_id:
                # Just table name without dataset, add dataset and project
                table_id_full = f"{self.project_id}.{self.dataset_id}.{table_id}"
            elif table_id.count('.') == 1:
                # table_id is in format 'dataset.table'
                table_id_full = f"{self.project_id}.{table_id}"
            else:
                # Assume fully qualified
                table_id_full = table_id

            # Start the load job
            print(f"Loading data from {gcs_uri} into table {table_id_full} using format {source_format}...")
            # No need for separate storage client here, BQ client handles GCS access
            # if hasattr(self.client, '_credentials'):
            #     # Reuse the credentials from the BigQuery client
            #     storage_client = storage.Client(
            #         project=self.project_id,
            #         credentials=self.client._credentials
            #     )
            # else:
            #     # Fallback to default credentials if unable to reuse
            #     storage_client = storage.Client(project=self.project_id)

            load_job = self.client.load_table_from_uri(
                gcs_uri,
                table_id_full,
                job_config=job_config
            )

            # Wait for job to complete
            load_job.result()  # This waits for the job to finish and raises an exception if fails

            # Get result information
            destination_table = self.client.get_table(table_id_full)
            print(f"Loaded {destination_table.num_rows} rows into {table_id_full}")
            return True

        except google_exceptions.NotFound as e:
             print(f"Error loading data: Table or GCS path not found: {str(e)}")
             return False
        except Exception as e:
            print(f"Error loading data from GCS to table: {str(e)}")
            return False

    def delete_gcs_folder(self, gcs_folder_path: str, dry_run: bool = False) -> Tuple[bool, int]:
        """
        Delete a folder and all its contents from Google Cloud Storage.

        Args:
            gcs_folder_path: GCS path to the folder to delete
                            (e.g., 'gs://bucket/folder/' or 'gs://bucket/folder')
            dry_run: If True, only list objects that would be deleted without actually deleting

        Returns:
            Tuple of (success, count) where:
            - success: Boolean indicating if the operation was successful
            - count: Number of objects deleted or that would be deleted (if dry_run)
        """
        try:
            from google.cloud import storage

            # Validate the GCS path
            if not gcs_folder_path.startswith('gs://'):
                raise ValueError("GCS path must start with 'gs://'")

            # Normalize the path - ensure it ends with a slash for proper prefix matching
            if not gcs_folder_path.endswith('/'):
                gcs_folder_path_norm = gcs_folder_path + '/'
            else:
                gcs_folder_path_norm = gcs_folder_path

            # Parse the GCS path to get bucket and prefix
            path_without_prefix = gcs_folder_path_norm[5:]  # Remove 'gs://'
            parts = path_without_prefix.split('/', 1)
            bucket_name = parts[0]
            folder_prefix = parts[1] if len(parts) > 1 else "" # Handle root folder case

            if not bucket_name:
                 raise ValueError("Invalid GCS path: Bucket name missing.")

            # Create a storage client reusing BigQuery credentials if possible
            if self.credentials:
                storage_client = storage.Client(
                    project=self.project_id,
                    credentials=self.credentials # Use BQ client credentials
                )
            else:
                # Fallback if BQ client wasn't initialized with key_file
                storage_client = storage.Client(project=self.project_id)

            # Get the bucket
            bucket = storage_client.bucket(bucket_name) # Use bucket() method

            # List all blobs with the folder prefix
            blobs_to_delete = list(bucket.list_blobs(prefix=folder_prefix))

            # Count blobs to be deleted
            count = len(blobs_to_delete)

            if count == 0:
                print(f"No objects found in folder: {gcs_folder_path_norm}")
                return True, 0

            # If this is a dry run, just print what would be deleted
            if dry_run:
                print(f"DRY RUN: Would delete {count} objects from {gcs_folder_path_norm}:")
                for blob in blobs_to_delete:
                    print(f" - gs://{bucket_name}/{blob.name}")
                return True, count

            # Delete all blobs
            print(f"Deleting {count} objects from {gcs_folder_path_norm}...")
            # Use delete_blobs for potential efficiency, though it might make individual calls
            # Consider batching for very large numbers if performance is critical
            # Note: delete_blobs doesn't have a built-in parallel execution guarantee in the client library itself.
            # It sends individual requests. For true parallelism, manual threading/asyncio might be needed.
            errors = bucket.delete_blobs(blobs_to_delete)

            # Check for errors during deletion (delete_blobs returns None on success or list of errors)
            # This part seems incorrect based on documentation, delete_blobs doesn't return errors this way.
            # Let's iterate and delete individually to report errors better.
            deleted_count = 0
            errors_occurred = False
            for blob in blobs_to_delete:
                try:
                    blob.delete()
                    deleted_count += 1
                except Exception as blob_delete_e:
                    print(f"  Error deleting blob gs://{bucket_name}/{blob.name}: {blob_delete_e}")
                    errors_occurred = True

            if errors_occurred:
                 print(f"Successfully deleted {deleted_count} out of {count} objects from {gcs_folder_path_norm}. Some errors occurred.")
                 return False, deleted_count # Indicate partial success
            else:
                 print(f"Successfully deleted {count} objects from {gcs_folder_path_norm}")
                 return True, count

        except google_exceptions.NotFound:
             print(f"Error deleting GCS folder: Bucket '{bucket_name}' not found or insufficient permissions.")
             return False, 0
        except Exception as e:
            print(f"Error deleting GCS folder: {str(e)}")
            return False, 0

    def create_gcs_folder(self, gcs_folder_path: str) -> bool:
        """
        Create a folder in Google Cloud Storage.

        In GCS, folders are virtual constructs. This method creates a zero-byte object
        with the folder name that ends with a slash, making it appear as a folder in
        the GCS console. If the folder already exists, it does nothing and returns True.

        Args:
            gcs_folder_path: Path to folder to create, should end with '/'
                            (e.g., 'gs://bucket/folder/')

        Returns:
            bool: True if successful or folder already exists, False otherwise
        """
        try:
            from google.cloud import storage

            # Validate the GCS path
            if not gcs_folder_path.startswith('gs://'):
                raise ValueError("GCS path must start with 'gs://'")

            if not gcs_folder_path.endswith('/'):
                gcs_folder_path += '/'  # Ensure path ends with /

            # Parse the GCS path to get bucket and folder path
            path_without_prefix = gcs_folder_path[5:]  # Remove 'gs://'
            parts = path_without_prefix.split('/', 1)
            bucket_name = parts[0]
            folder_path = parts[1] if len(parts) > 1 else "" # Object name (folder marker)

            if not bucket_name:
                 raise ValueError("Invalid GCS path: Bucket name missing.")
            if not folder_path:
                 print(f"Cannot create a folder marker for the bucket root ('gs://{bucket_name}/'). Operation skipped.")
                 return True # Technically no action needed for bucket root

            # Create a storage client reusing BigQuery credentials if possible
            if self.credentials:
                storage_client = storage.Client(
                    project=self.project_id,
                    credentials=self.credentials # Use BQ client credentials
                )
            else:
                 # Fallback if BQ client wasn't initialized with key_file
                storage_client = storage.Client(project=self.project_id)

            # Get the bucket
            bucket = storage_client.bucket(bucket_name)

            # Create a marker blob with slash at the end
            marker_blob = bucket.blob(folder_path)

            # Check if the marker object already exists
            if marker_blob.exists():
                print(f"Folder already exists: {gcs_folder_path}")
                return True

            # Upload an empty string to create the marker object
            marker_blob.upload_from_string('', content_type='application/x-directory') # Use standard marker type

            print(f"Successfully created folder: {gcs_folder_path}")
            return True

        except google_exceptions.NotFound:
             print(f"Error creating GCS folder: Bucket '{bucket_name}' not found or insufficient permissions.")
             return False
        except Exception as e:
            print(f"Error creating GCS folder: {str(e)}")
            return False

    def _get_table_schema(self, table_id: str) -> dict:
        """Fetches the schema for a given BigQuery table.

        Args:
            table_id: The full table ID (project.dataset.table).

        Returns:
            A dictionary mapping column names to their data types,
            or an empty dictionary if the table is not found or an error occurs.
        """
        schema_dict = {}
        try:
            table = self.client.get_table(table_id)
            logging.info(f"Fetched schema for table: {table_id}")
            for field in table.schema:
                schema_dict[field.name] = field.field_type
            return schema_dict
        except NotFound:
            logging.error(f"Table not found: {table_id}")
            return {}
        except Exception as e:
            logging.error(f"Error fetching schema for {table_id}: {e}")
            return {}

        
    def erd(self, table_list: list, output_filename: str = 'bq_erd', output_format: str = 'png', view_diagram: bool = False):
        """
        Generates an Entity Relationship Diagram (ERD) for a list of BigQuery tables.

        Identifies potential relationships by matching column names across tables.

        Requires the 'graphviz' Python package and the Graphviz system library
        (https://graphviz.org/download/).

        Args:
            table_list: A list of full BigQuery table IDs (project.dataset.table).
            output_filename: The base name for the output file (without extension).
            output_format: The output format for the diagram (e.g., 'png', 'svg', 'pdf').
            view_diagram: If True, attempts to open the generated diagram file.

        Returns:
            The path to the generated diagram file if successful, None otherwise.
        """
        if graphviz is None:
            logging.error("The 'graphviz' library is required for ERD generation.")
            print("Please install it: pip install graphviz")
            print("Also ensure the Graphviz system library is installed: https://graphviz.org/download/")
            return None

        # Use a Digraph for directed relationships (optional, could use Graph)
        # Use strict=True to avoid duplicate edges between the same nodes
        dot = graphviz.Digraph('BigQuery ERD', comment='Entity Relationship Diagram',
                               graph_attr={'rankdir': 'LR', 'splines': 'ortho'}, # Layout options
                               node_attr={'shape': 'plaintext'}, # Use HTML-like labels
                               edge_attr={'arrowhead': 'none', 'arrowtail': 'none'}, # Style edges
                               strict=True) # Avoid duplicate edges

        table_schemas = {}
        column_map = {} # Map column names to tables that contain them

        # 1. Fetch schemas and build nodes
        logging.info("Fetching table schemas...")
        for table_id in table_list:
            schema = self._get_table_schema(table_id)
            if not schema:
                logging.warning(f"Could not fetch schema for {table_id}, skipping.")
                continue
            table_schemas[table_id] = schema

            # Create an HTML-like label for the table node
            # Note: Limited HTML support in graphviz, keep it simple.
            label = f'''<
            <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>{table_id.split('.')[-1]}</B></TD></TR>
            <TR><TD BGCOLOR="lightgrey"><B>type</B></TD><TD BGCOLOR="lightgrey"><B>name</B></TD></TR>
            '''
            for col_name, col_type in schema.items():
                label += f'<TR><TD ALIGN="LEFT">{col_type}</TD><TD ALIGN="LEFT" PORT="{col_name}">{col_name}</TD></TR>'
                # Add column to map for relationship finding
                if col_name not in column_map:
                    column_map[col_name] = []
                column_map[col_name].append(table_id)
            label += '</TABLE>>'

            dot.node(table_id, label=label)
            logging.info(f"Added node for table: {table_id}")

        # 2. Identify and add relationships (edges)
        logging.info("Identifying relationships based on matching column names...")
        added_edges = set() # Keep track of edges to avoid duplicates visually if strict=False was used
        for column_name, containing_tables in column_map.items():
            if len(containing_tables) > 1:
                # Create edges between all pairs of tables sharing this column
                from itertools import combinations
                for table1, table2 in combinations(containing_tables, 2):
                    # Create a unique key for the edge regardless of direction
                    edge_key = tuple(sorted((table1, table2)))
                    if edge_key not in added_edges:
                         # Connect using the specific column ports
                         # Note: Ports need to match the TD PORT attribute above
                        dot.edge(f'{table1}:{column_name}', f'{table2}:{column_name}')
                        added_edges.add(edge_key)
                        logging.info(f"Added edge between {table1} and {table2} on column '{column_name}'")

        # 3. Render the graph
        try:
            logging.info(f"Rendering ERD to {output_filename}.{output_format}...")
            # Use cleanup=True to remove the source file after rendering
            # Use view=view_diagram to automatically open the file
            rendered_path = dot.render(output_filename, format=output_format, view=view_diagram, cleanup=True)
            logging.info(f"ERD successfully generated: {rendered_path}")
            return rendered_path
        except graphviz.backend.execute.ExecutableNotFound:
            logging.error("Graphviz executable not found. Ensure Graphviz is installed and in your system's PATH.")
            print("Download Graphviz from: https://graphviz.org/download/")
            return None
        except Exception as e:
            logging.error(f"Error rendering graph: {e}")
            return None