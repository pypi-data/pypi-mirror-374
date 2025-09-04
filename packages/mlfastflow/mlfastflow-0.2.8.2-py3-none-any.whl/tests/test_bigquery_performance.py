"""Performance tests for BigQueryClient loop scenarios."""

import time
import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from mlfastflow.bigqueryclient import BigQueryClient


class TestBigQueryClientPerformance(unittest.TestCase):
    """Test performance improvements for BigQueryClient in loop scenarios."""

    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.mock_env_vars = {
            'BAMA_DEV_PROJECT_ID': 'test-project',
            'BAMA_DEV_DATASET_ID': 'test-dataset',
            'BAMA_DEV_KEY_FILE': '/path/to/test-key.json'
        }
        
    @patch('mlfastflow.bigqueryclient.service_account')
    @patch('mlfastflow.bigqueryclient.bigquery')
    def test_connection_reuse_performance(self, mock_bigquery, mock_service_account):
        """Test that connections are reused and don't degrade in loops."""
        # Mock credentials and client
        mock_credentials = Mock()
        mock_credentials.project_id = 'test-project'
        mock_service_account.Credentials.from_service_account_file.return_value = mock_credentials
        
        mock_client = Mock()
        mock_bigquery.Client.return_value = mock_client
        
        # Mock query job and results
        mock_query_job = Mock()
        mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mock_query_job.to_dataframe.return_value = mock_df
        mock_client.query.return_value = mock_query_job
        
        # Create client
        client = BigQueryClient(
            project_id='test-project',
            dataset_id='test-dataset', 
            key_file='/path/to/test-key.json'
        )
        
        # Simulate loop execution with timing
        query_times = []
        num_iterations = 20
        
        for i in range(num_iterations):
            start_time = time.time()
            
            sql = f"SELECT * FROM test_table WHERE id = {i}"
            result = client.sql2df(sql)
            
            end_time = time.time()
            query_times.append(end_time - start_time)
            
            # Verify result
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(len(result), 3)
        
        # Verify connection was created only once initially
        # (may be refreshed based on refresh criteria)
        initial_calls = mock_bigquery.Client.call_count
        self.assertGreaterEqual(initial_calls, 1)
        
        # Verify query method was called for each iteration
        self.assertEqual(mock_client.query.call_count, num_iterations)
        
        # Verify query counter is working
        self.assertEqual(client._query_count, num_iterations)
        
        # Performance check: later queries shouldn't be significantly slower
        # (allowing for some variance due to mocking overhead)
        early_queries_avg = sum(query_times[:5]) / 5
        late_queries_avg = sum(query_times[-5:]) / 5
        
        # Late queries should not be more than 50% slower than early ones
        performance_degradation = (late_queries_avg - early_queries_avg) / early_queries_avg
        self.assertLess(performance_degradation, 0.5, 
                       f"Performance degraded by {performance_degradation*100:.1f}%")
        
        print(f"Early queries avg: {early_queries_avg:.4f}s")
        print(f"Late queries avg: {late_queries_avg:.4f}s")
        print(f"Performance change: {performance_degradation*100:.1f}%")

    @patch('mlfastflow.bigqueryclient.service_account')
    @patch('mlfastflow.bigqueryclient.bigquery')
    @patch('mlfastflow.bigqueryclient.storage')
    def test_storage_client_caching(self, mock_storage, mock_bigquery, mock_service_account):
        """Test that storage clients are cached and reused."""
        # Mock credentials and clients
        mock_credentials = Mock()
        mock_credentials.project_id = 'test-project'
        mock_service_account.Credentials.from_service_account_file.return_value = mock_credentials
        
        mock_bq_client = Mock()
        mock_bigquery.Client.return_value = mock_bq_client
        
        mock_storage_client = Mock()
        mock_storage.Client.return_value = mock_storage_client
        
        # Create client
        client = BigQueryClient(
            project_id='test-project',
            dataset_id='test-dataset',
            key_file='/path/to/test-key.json'
        )
        
        # Call storage client getter multiple times
        storage_client1 = client._get_storage_client()
        storage_client2 = client._get_storage_client()
        storage_client3 = client._get_storage_client()
        
        # Verify same instance is returned
        self.assertIs(storage_client1, storage_client2)
        self.assertIs(storage_client2, storage_client3)
        
        # Verify storage.Client was called only once
        self.assertEqual(mock_storage.Client.call_count, 1)

    @patch('mlfastflow.bigqueryclient.service_account')
    @patch('mlfastflow.bigqueryclient.bigquery')
    def test_connection_refresh_mechanism(self, mock_bigquery, mock_service_account):
        """Test that connections are refreshed when criteria are met."""
        # Mock credentials and client
        mock_credentials = Mock()
        mock_credentials.project_id = 'test-project'
        mock_service_account.Credentials.from_service_account_file.return_value = mock_credentials
        
        mock_client = Mock()
        mock_bigquery.Client.return_value = mock_client
        
        # Create client
        client = BigQueryClient(
            project_id='test-project',
            dataset_id='test-dataset',
            key_file='/path/to/test-key.json'
        )
        
        # Verify initial connection was created
        initial_calls = mock_bigquery.Client.call_count
        self.assertGreaterEqual(initial_calls, 1)
        
        # Simulate high query count to trigger refresh
        client._query_count = 150  # Above default threshold of 100
        
        # Mock query to trigger refresh check
        mock_query_job = Mock()
        mock_query_job.to_dataframe.return_value = pd.DataFrame({'test': [1]})
        mock_client.query.return_value = mock_query_job
        
        # Execute query which should trigger refresh
        client.sql2df("SELECT 1 as test")
        
        # Verify connection was refreshed (additional Client() call)
        final_calls = mock_bigquery.Client.call_count
        self.assertGreater(final_calls, initial_calls)
        
        # Verify query count was reset
        self.assertEqual(client._query_count, 1)  # Reset to 0, then incremented by 1

    def test_memory_cleanup(self):
        """Test that resources are properly cleaned up."""
        with patch('mlfastflow.bigqueryclient.service_account') as mock_sa, \
             patch('mlfastflow.bigqueryclient.bigquery') as mock_bq:
            
            # Mock setup
            mock_credentials = Mock()
            mock_credentials.project_id = 'test-project'
            mock_sa.Credentials.from_service_account_file.return_value = mock_credentials
            
            mock_client = Mock()
            mock_bq.Client.return_value = mock_client
            
            # Create and use client
            client = BigQueryClient(
                project_id='test-project',
                dataset_id='test-dataset',
                key_file='/path/to/test-key.json'
            )
            
            # Verify client was created
            self.assertIsNotNone(client.client)
            self.assertIsNotNone(client.credentials)
            
            # Close client
            client.close()
            
            # Verify cleanup
            self.assertIsNone(client.client)
            self.assertIsNone(client.credentials)
            self.assertIsNone(client._storage_client)
            self.assertIsNone(client._connection_created_at)


if __name__ == '__main__':
    unittest.main()