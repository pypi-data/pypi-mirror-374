"""Simple example using the Sourcing class."""

from pyfastflow import Sourcing
import pandas as pd

def main():
    """Run a simple example using the Sourcing class."""
    # Create sample dataframes
    query_df = pd.DataFrame({
        'id': [1, 2, 3],
        'text': ['sample query 1', 'sample query 2', 'sample query 3']
    })
    
    db_df = pd.DataFrame({
        'id': [101, 102, 103, 104, 105],
        'text': ['database item 1', 'database item 2', 'database item 3', 
                'database item 4', 'database item 5']
    })
    
    # Initialize Sourcing instance
    sourcing = Sourcing(
        query_df=query_df,
        db_df=db_df,
        columns_for_sourcing=['text'],
        label='id'
    )
    
    # Process data
    print("Initialized Sourcing instance.")
    print(f"Working with {len(query_df)} query items and {len(db_df)} database items.")
    
    # Note: This is a simplified example and may need adjustment based on 
    # the exact implementation of the Sourcing class


if __name__ == "__main__":
    main()