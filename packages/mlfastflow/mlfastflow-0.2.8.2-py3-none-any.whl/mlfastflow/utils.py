"""Utility functions for the mlfastflow package."""

import os
import time
import warnings
from functools import wraps
from pathlib import Path
from typing import List, Optional, Union, Any

try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pandas as pd
except ImportError:
    pd = None


def timer_decorator(func):
    """Decorator that prints the execution time of the decorated function.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function
    """
    @wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            run_time = end_time - start_time
            print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
    return wrapper_timer


def concat_files(
    folder_path: Union[str, Path], 
    file_type: str = 'csv', 
    add_source_column: bool = False
) -> Optional[str]:
    """Concatenate all files of a specific type in a folder and its subfolders.
    
    Args:
        folder_path: Path to the folder containing files to concatenate
        file_type: File extension to look for ('csv' or 'parquet')
        add_source_column: If True, adds a 'SOURCE' column with the filename
    
    Returns:
        Path to the concatenated output file, or None if no files were processed
        
    Raises:
        ImportError: If polars is not installed
        ValueError: If file_type is not supported
        FileNotFoundError: If folder_path doesn't exist
    """
    if pl is None:
        raise ImportError("polars is required for concat_files. Install with: pip install polars")
    
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder path does not exist: {folder_path}")
    
    if not folder_path.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")
    
    supported_types = {'csv', 'parquet'}
    if file_type.lower() not in supported_types:
        raise ValueError(f"Unsupported file type: {file_type}. Supported types: {supported_types}")
    
    # Define output filename at the same level as input folder
    output_file = folder_path.parent / f"{folder_path.name}_combined.{file_type}"
    
    # Get all files with the specified extension recursively
    pattern = f"**/*.{file_type}"
    all_files = list(folder_path.glob(pattern))
    
    if not all_files:
        print(f"No .{file_type} files found in {folder_path}")
        return None
    
    print(f"Found {len(all_files)} .{file_type} files to combine")
    
    # Read and concatenate all files
    dataframes = []
    failed_files = []
    
    for file_path in all_files:
        try:
            if file_type.lower() == 'csv':
                df = pl.read_csv(file_path)
            else:  # parquet
                df = pl.read_parquet(file_path)
                
            # Add source column if requested
            if add_source_column:
                df = df.with_columns(pl.lit(file_path.name).alias("SOURCE"))
                
            dataframes.append(df)
        except Exception as e:
            failed_files.append((file_path, str(e)))
            print(f"Error reading file {file_path}: {e}")
    
    if failed_files:
        print(f"Failed to read {len(failed_files)} files")
    
    if not dataframes:
        print("No valid dataframes to concatenate")
        return None
    
    try:
        # Concatenate all dataframes
        combined_df = pl.concat(dataframes)
        
        # Save the combined dataframe
        if file_type.lower() == 'csv':
            combined_df.write_csv(output_file)
        else:  # parquet
            combined_df.write_parquet(output_file)
        
        print(f"Combined {len(dataframes)} files into {output_file}")
        return str(output_file)
        
    except Exception as e:
        print(f"Error concatenating or saving files: {e}")
        return None


def profile(
    df: Any,
    title: str = "Data Profiling Report",
    output_path: Optional[Union[str, Path]] = None,
    minimal: bool = True,
) -> Optional[Any]:
    """Generate a data profiling report for a DataFrame.
    
    Args:
        df: A polars or pandas DataFrame
        title: Title of the report
        output_path: Directory path where the HTML report will be saved.
            If None, saves to current directory
        minimal: Whether to generate a minimal report (faster) or a complete report
        
    Returns:
        ProfileReport wrapper object or None if profiling fails
        
    Raises:
        ImportError: If required packages are not installed
        ValueError: If DataFrame is empty or invalid
    """
    try:
        from ydata_profiling import ProfileReport
    except ImportError:
        raise ImportError("ydata-profiling is required for profile. Install with: pip install ydata-profiling")
    
    if pd is None:
        raise ImportError("pandas is required for profile. Install with: pip install pandas")
    
    # Suppress irrelevant warnings
    warnings.filterwarnings("ignore", message=".*IProgress not found.*")
    
    # Disable promotional banners
    os.environ["YDATA_PROFILING_DISABLE_PREMIUM_BANNER"] = "1"
    
    # Convert to pandas DataFrame if necessary
    if hasattr(df, 'to_pandas'):
        # This is a polars DataFrame
        pandas_df = df.to_pandas()
    elif hasattr(df, 'dtypes'):
        # Assume it's already a pandas DataFrame
        pandas_df = df
    else:
        raise ValueError("Input must be a pandas or polars DataFrame")
    
    # Check for empty DataFrame
    if len(pandas_df) == 0:
        raise ValueError("Cannot profile an empty DataFrame")
    
    try:
        # Create the profiling report
        profile_report = ProfileReport(
            pandas_df,
            title=title,
            minimal=minimal,
        )
        
        # Create safe filename from title
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = safe_title.replace(" ", "_") + ".html"
        
        # Determine full output path
        if output_path is not None:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            full_path = output_dir / filename
        else:
            full_path = Path(filename)
        
        # Save the report
        profile_report.to_file(full_path)
        print(f"Profile report saved to {full_path}")
        
        # Create a non-displaying wrapper to prevent showing in Jupyter
        class ProfileReportWrapper:
            """Wrapper to prevent automatic display in Jupyter notebooks."""
            
            def __init__(self, profile_report):
                self._profile = profile_report
                
            def to_file(self, *args, **kwargs):
                """Save the report to a file."""
                return self._profile.to_file(*args, **kwargs)
                
            def _repr_html_(self):
                """Block automatic HTML display in Jupyter."""
                return None
                
            def __getattr__(self, name):
                """Delegate attribute access to the original profile."""
                return getattr(self._profile, name)
                
        return ProfileReportWrapper(profile_report)
        
    except Exception as e:
        print(f"Error generating profile report: {e}")
        print("This may happen with problematic data. Try with different data or parameters.")
        return None



def csv2parquet(
    input_path: Union[str, Path], 
    output_dir: Optional[Union[str, Path]] = None, 
    sub_folders: bool = False, 
    schema_overrides: Optional[dict] = None
) -> List[str]:
    """Convert CSV file(s) to Parquet format using Polars for better performance.
    
    Args:
        input_path: Path to a CSV file or directory containing CSV files
        output_dir: Directory to save the Parquet files. If None, saves in the same location as input
        sub_folders: If True and input_path is a directory, process subfolders recursively
        schema_overrides: Dictionary to override column types when reading CSV
        
    Returns:
        List of paths to the created Parquet files
        
    Raises:
        ImportError: If polars is not installed
        FileNotFoundError: If input_path doesn't exist
    """
    if pl is None:
        raise ImportError("polars is required for csv2parquet. Install with: pip install polars")
    
    input_path = Path(input_path).resolve()
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    
    # Prepare output directory if specified
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = None
    
    created_files = []
    failed_files = []
    
    def _convert_file(csv_file: Path, output_file: Path) -> bool:
        """Convert a single CSV file to Parquet."""
        try:
            print(f"Converting {csv_file} to {output_file}")
            # Use scan_csv for lazy evaluation and better memory efficiency
            lazy_df = pl.scan_csv(csv_file, schema_overrides=schema_overrides)
            lazy_df.collect().write_parquet(output_file)
            created_files.append(str(output_file))
            return True
        except Exception as e:
            failed_files.append((csv_file, str(e)))
            print(f"Error converting {csv_file}: {e}")
            return False
    
    # Case 1: Input is a file
    if input_path.is_file():
        if input_path.suffix.lower() != '.csv':
            print(f"Warning: {input_path} is not a CSV file. Skipping.")
            return created_files
        
        # Determine output path
        if output_path:
            output_file = output_path / f"{input_path.stem}.parquet"
        else:
            output_file = input_path.with_suffix('.parquet')
        
        _convert_file(input_path, output_file)
    
    # Case 2: Input is a directory
    elif input_path.is_dir():
        # Get CSV files based on sub_folders setting
        if sub_folders:
            csv_files = list(input_path.rglob('*.csv'))
        else:
            csv_files = list(input_path.glob('*.csv'))
        
        if not csv_files:
            print(f"No CSV files found in {input_path}")
            return created_files
        
        print(f"Found {len(csv_files)} CSV files to convert")
        
        for csv_file in csv_files:
            # Create corresponding output directory structure if output_dir is specified
            if output_path:
                # Calculate relative path from input directory
                rel_path = csv_file.relative_to(input_path)
                output_file = output_path / rel_path.with_suffix('.parquet')
                # Ensure parent directory exists
                output_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_file = csv_file.with_suffix('.parquet')
            
            _convert_file(csv_file, output_file)
    
    else:
        raise ValueError(f"Input path is neither a file nor a directory: {input_path}")
    
    # Summary
    if created_files:
        print(f"Successfully converted {len(created_files)} file(s) to Parquet")
    
    if failed_files:
        print(f"Failed to convert {len(failed_files)} file(s)")
    
    if not created_files and not failed_files:
        print("No files were processed")
    
    return created_files