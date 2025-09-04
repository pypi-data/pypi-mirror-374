"""Tests for the utils module of the mlfastflow package."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import polars as pl

from mlfastflow.utils import timer_decorator, concat_files, profile, csv2parquet


class TestTimerDecorator(unittest.TestCase):
    """Test cases for the timer_decorator function."""

    @patch('builtins.print')
    def test_timer_decorator_basic(self, mock_print):
        """Test that timer decorator works and prints timing."""
        @timer_decorator
        def test_func():
            return "test_result"
        
        result = test_func()
        
        self.assertEqual(result, "test_result")
        mock_print.assert_called_once()
        # Check that the print call contains the function name and timing info
        call_args = mock_print.call_args[0][0]
        self.assertIn("test_func", call_args)
        self.assertIn("secs", call_args)

    @patch('builtins.print')
    def test_timer_decorator_with_exception(self, mock_print):
        """Test that timer decorator still prints timing even when function raises exception."""
        @timer_decorator
        def test_func():
            raise ValueError("test error")
        
        with self.assertRaises(ValueError):
            test_func()
        
        # Timer should still print even when exception occurs
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn("test_func", call_args)
        self.assertIn("secs", call_args)


class TestConcatFiles(unittest.TestCase):
    """Test cases for the concat_files function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test CSV files
        self.csv1_path = self.temp_path / "test1.csv"
        self.csv2_path = self.temp_path / "test2.csv"
        
        # Create test data
        df1 = pl.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        df2 = pl.DataFrame({"a": [3, 4], "b": ["z", "w"]})
        
        df1.write_csv(self.csv1_path)
        df2.write_csv(self.csv2_path)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_concat_csv_files(self):
        """Test concatenating CSV files."""
        result_path = concat_files(self.temp_path, file_type='csv')
        
        self.assertIsNotNone(result_path)
        result_file = Path(result_path)
        self.assertTrue(result_file.exists())
        
        # Check the concatenated content
        result_df = pl.read_csv(result_file)
        self.assertEqual(len(result_df), 4)  # 2 + 2 rows

    def test_concat_with_source_column(self):
        """Test concatenating files with source column."""
        result_path = concat_files(self.temp_path, file_type='csv', add_source_column=True)
        
        self.assertIsNotNone(result_path)
        result_df = pl.read_csv(result_path)
        self.assertIn("SOURCE", result_df.columns)

    def test_concat_nonexistent_folder(self):
        """Test concat_files with nonexistent folder."""
        nonexistent_path = self.temp_path / "nonexistent"
        
        with self.assertRaises(FileNotFoundError):
            concat_files(nonexistent_path)

    def test_concat_unsupported_file_type(self):
        """Test concat_files with unsupported file type."""
        with self.assertRaises(ValueError):
            concat_files(self.temp_path, file_type='xlsx')

    def test_concat_no_files_found(self):
        """Test concat_files when no files of specified type are found."""
        # Create empty directory
        empty_dir = self.temp_path / "empty"
        empty_dir.mkdir()
        
        result = concat_files(empty_dir, file_type='csv')
        self.assertIsNone(result)


class TestProfile(unittest.TestCase):
    """Test cases for the profile function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test DataFrame
        self.test_df = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'text': ['a', 'b', 'c', 'd', 'e'],
            'float': [1.1, 2.2, 3.3, 4.4, 5.5]
        })

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_profile_pandas_dataframe(self):
        """Test profiling a pandas DataFrame."""
        result = profile(self.test_df, output_path=str(self.temp_path))
        
        self.assertIsNotNone(result)
        # Check that HTML file was created
        html_files = list(self.temp_path.glob("*.html"))
        self.assertEqual(len(html_files), 1)

    def test_profile_polars_dataframe(self):
        """Test profiling a polars DataFrame."""
        polars_df = pl.from_pandas(self.test_df)
        result = profile(polars_df, output_path=str(self.temp_path))
        
        self.assertIsNotNone(result)
        # Check that HTML file was created
        html_files = list(self.temp_path.glob("*.html"))
        self.assertEqual(len(html_files), 1)

    def test_profile_empty_dataframe(self):
        """Test profiling an empty DataFrame."""
        empty_df = pd.DataFrame()
        
        with self.assertRaises(ValueError):
            profile(empty_df)

    def test_profile_invalid_input(self):
        """Test profiling with invalid input."""
        with self.assertRaises(ValueError):
            profile("not_a_dataframe")

    def test_profile_custom_title(self):
        """Test profiling with custom title."""
        custom_title = "My Custom Report"
        result = profile(self.test_df, title=custom_title, output_path=str(self.temp_path))
        
        self.assertIsNotNone(result)
        # Check that file with custom title was created
        expected_filename = "My_Custom_Report.html"
        expected_path = self.temp_path / expected_filename
        self.assertTrue(expected_path.exists())


class TestCsv2Parquet(unittest.TestCase):
    """Test cases for the csv2parquet function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test CSV file
        self.csv_file = self.temp_path / "test.csv"
        test_df = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.5, 20.3, 30.1]
        })
        test_df.write_csv(self.csv_file)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_convert_single_file(self):
        """Test converting a single CSV file to Parquet."""
        result = csv2parquet(self.csv_file)
        
        self.assertEqual(len(result), 1)
        parquet_file = Path(result[0])
        self.assertTrue(parquet_file.exists())
        self.assertEqual(parquet_file.suffix, '.parquet')
        
        # Verify content
        df = pl.read_parquet(parquet_file)
        self.assertEqual(len(df), 3)
        self.assertEqual(df.columns, ["id", "name", "value"])

    def test_convert_directory(self):
        """Test converting all CSV files in a directory."""
        # Create another CSV file
        csv_file2 = self.temp_path / "test2.csv"
        test_df2 = pl.DataFrame({"x": [4, 5], "y": ["D", "E"]})
        test_df2.write_csv(csv_file2)
        
        result = csv2parquet(self.temp_path)
        
        self.assertEqual(len(result), 2)
        for file_path in result:
            self.assertTrue(Path(file_path).exists())
            self.assertEqual(Path(file_path).suffix, '.parquet')

    def test_convert_with_output_dir(self):
        """Test converting with custom output directory."""
        output_dir = self.temp_path / "output"
        result = csv2parquet(self.csv_file, output_dir=output_dir)
        
        self.assertEqual(len(result), 1)
        result_file = Path(result[0])
        self.assertTrue(result_file.exists())
        # Use resolve() to handle symlinks consistently
        self.assertEqual(result_file.parent.resolve(), output_dir.resolve())

    def test_convert_nonexistent_file(self):
        """Test converting nonexistent file."""
        nonexistent_file = self.temp_path / "nonexistent.csv"
        
        with self.assertRaises(FileNotFoundError):
            csv2parquet(nonexistent_file)

    def test_convert_non_csv_file(self):
        """Test converting non-CSV file."""
        txt_file = self.temp_path / "test.txt"
        txt_file.write_text("not a csv")
        
        result = csv2parquet(txt_file)
        self.assertEqual(len(result), 0)

    def test_convert_with_subdirectories(self):
        """Test converting CSV files in subdirectories."""
        # Create subdirectory with CSV file
        sub_dir = self.temp_path / "subdir"
        sub_dir.mkdir()
        csv_file_sub = sub_dir / "sub_test.csv"
        test_df_sub = pl.DataFrame({"a": [1], "b": ["test"]})
        test_df_sub.write_csv(csv_file_sub)
        
        result = csv2parquet(self.temp_path, sub_folders=True)
        
        # Should find both the main CSV and the subdirectory CSV
        self.assertEqual(len(result), 2)
        
        # Check that subdirectory structure is preserved
        sub_parquet_files = [f for f in result if "subdir" in f]
        self.assertEqual(len(sub_parquet_files), 1)


class TestUtilsIntegration(unittest.TestCase):
    """Integration tests for utils functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_csv_to_parquet_to_profile_workflow(self):
        """Test a complete workflow: CSV -> Parquet -> Profile."""
        # Create CSV file
        csv_file = self.temp_path / "workflow_test.csv"
        df = pl.DataFrame({
            "id": range(100),
            "category": ["A", "B", "C"] * 33 + ["A"],
            "value": [i * 0.1 for i in range(100)]
        })
        df.write_csv(csv_file)
        
        # Convert to Parquet
        parquet_files = csv2parquet(csv_file)
        self.assertEqual(len(parquet_files), 1)
        
        # Load Parquet and profile
        parquet_df = pl.read_parquet(parquet_files[0])
        profile_result = profile(parquet_df, output_path=str(self.temp_path))
        
        self.assertIsNotNone(profile_result)
        # Check that profile HTML was created
        html_files = list(self.temp_path.glob("*.html"))
        self.assertEqual(len(html_files), 1)


if __name__ == "__main__":
    unittest.main()