"""Module for fast KNN functionality in the mlfastflow package."""

import pandas as pd
import numpy as np
import faiss
from getpass import getpass
import datetime


class fastKNN:
    def __init__(self,
                 query_df: pd.DataFrame,
                 search_df: pd.DataFrame,
                 knn_keys: list[str],
                 label: str,
                #  query_remove_columns: list[str] = None,
                #  db_remove_columns: list[str] = None,
                 fillna_method: str = 'zero',
                 k_neighbors: int = 1000,
                 fastKNN_rate: float = 0.2, 
                 remove_duplicate: bool = False,
                 credentials: str = None
    ):
        self.query_df = query_df # assume it has label
        self.search_df = search_df

        # keep a copy for validation
        self.query_df_raw = query_df.copy()
        self.search_df_raw = search_df.copy()  
        self.sourced_search_df_with_label = None,

        self.knn_keys = knn_keys
        self.label = label

        # self.query_remove_columns = query_remove_columns
        # self.db_remove_columns = db_remove_columns

        self.fillna_method = fillna_method
        self.k_neighbors = k_neighbors
        self.fastKNN_rate = fastKNN_rate
        self.remove_duplicate = remove_duplicate

        self.D = None
        self.I = None

        self.indices = []  # Initialize as empty list
        self.sourced_search_df = pd.DataFrame()  # Initialize as empty DataFrame
        self.credentials = credentials

        start = datetime.datetime.now()
        self.pre_process()
        end = datetime.datetime.now()
        print(f"Preprocessing took {end-start}")

    def pre_process(self):
        """
        Prepare query and database DataFrames for similarity matching.
        
        This method performs the following preprocessing steps:
        1. Filter query DataFrame to include only rows where label=1 (if label column exists)
        2. Select only the columns specified for fastKNN from both DataFrames
        3. Handle missing values in both DataFrames by filling them
        
        No parameters are required as it operates on the instance variables.
        No return value as it modifies the DataFrames in-place.
        """
        
        print("Pre-processing started")
        if self.label in self.query_df.columns:
            # Filter query DataFrame to only include rows where the label column equals 1
            self.query_df = self.query_df[self.query_df[self.label]==1]
            # Note: If label column doesn't exist, assume query_df is already filtered
        
        # Select columns for fastKNN from both DataFrames
        self.query_df = self.query_df[self.knn_keys]
        print("Query DataFrame filtered and columns selected")
            
        self.search_df = self.search_df[self.knn_keys]
        print("Database DataFrame filtered and columns selected")

        
        # Fill missing values in both DataFrames
        self.query_df = self.fillna(self.query_df)
        print("Missing values in query DataFrame filled")
        
        self.search_df = self.fillna(self.search_df)
        print("Missing values in database DataFrame filled")

        if self.remove_duplicate:
            self.query_df = self.query_df.drop_duplicates()
            self.search_df = self.search_df.drop_duplicates()
            print("Removed duplicate rows from both DataFrames")
        
        print("Pre-processing completed")

    def set_fillna_method(self, method):
        self.fillna_method = method

    def fillna(self, df):
        try:
            if self.fillna_method == 'zero':
                return df.fillna(0)
            elif self.fillna_method == 'mean':
                mean_values = df.mean()
                if mean_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(mean_values)
                    return df.fillna(0)  # Fill remaining NAs with 0
                return df.fillna(mean_values)
            elif self.fillna_method == 'median':
                median_values = df.median()
                if median_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(median_values)
                    return df.fillna(0)
                return df.fillna(median_values)
            elif self.fillna_method == 'mode':
                mode_values = df.mode().iloc[0]
                if mode_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(mode_values)
                    return df.fillna(0)
                return df.fillna(mode_values)
            elif self.fillna_method == 'max':
                max_values = df.max()
                if max_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(max_values)
                    return df.fillna(0)
                return df.fillna(max_values)
            elif self.fillna_method == 'min':
                min_values = df.min()
                if min_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(min_values)
                    return df.fillna(0)
                return df.fillna(min_values)
            else:
                print("Invalid fillna_method. Using 'zero' method instead.")
                return df.fillna(0)
        except Exception as e:
            print(f"Error in fillna: {str(e)}. Using 'zero' method instead.")
            return df.fillna(0)
    
    def _get_credentials(self):
        """
        Internal method for credential verification.

        Prompts user for credentials and returns the input credential.
        Used for access control in the run method.
        """
        credential = getpass("Please enter your credentials: ")
        return credential

    def indexing(self):
        # credential box
        # input_credential = self._get_credentials()
        # if input_credential != 'hijinwen':
        #     print("Access denied: Invalid credentials")
        #     return False
            
        start = datetime.datetime.now()
        try:
            
            # faiss
            index = faiss.IndexFlatL2(self.query_df.shape[1])
            index.add(self.search_df)
            
            # Ensure k doesn't exceed database size
            effective_k = min(self.k_neighbors, len(self.search_df))
            self.D, self.I = index.search(self.query_df, effective_k)

            self.indices = list(set([index for sublist in self.I for index in sublist]))
            
            end = datetime.datetime.now()
            print(f"Indexing took {end-start}")
            return self.indices
            
        except Exception as e:
            print(f"Error running fastKNN: {str(e)}")
            return False
        

    def fastKNN(self):
        """Returns the fastKNN results as a DataFrame."""
        self.indexing()
        self.sourced_search_df = self.search_df.iloc[self.indices]
        self.sourced_search_df_with_label = self.search_df_raw.iloc[self.indices]
        # self.sourced_search_df = self.sourced_search_df.drop_duplicates()
        return self.sourced_search_df, self.sourced_search_df_with_label

    def validate(self):
        if self.label not in self.search_df_raw.columns:
            print("Label is needed in database for validation.")
            return

        """Validates the fastKNN results by comparing label counts."""
        try:
            if self.indices is None or not self.indices:
                print("No results to validate. Run the fastKNN process first.")
                return
                
            # labels in db_db
            self.raw_label_number = self.search_df_raw[self.search_df_raw[self.label]==1].shape[0]
            
            self.sourced_label_number = self.sourced_search_df_with_label[self.sourced_search_df_with_label[self.label]==1].shape[0] 

            print("Label before fastKNN: " + str(self.raw_label_number))
            print("Label after fastKNN: " + str(self.sourced_label_number))

            print("Number of rows before fastKNN: " + str(self.search_df_raw.shape[0]))
            print("Number of rows after fastKNN: " + str(self.sourced_search_df.shape[0]))

        except Exception as e:
            print(f"Error validating: {str(e)}")
