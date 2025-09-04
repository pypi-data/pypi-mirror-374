#%%
import sys
import os
from pathlib import Path

# Add parent directory to path so Python can find the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly from the module file, bypassing __init__.py
from mlfastflow.bigqueryclient import BigQueryClient
import dotenv
dotenv.load_dotenv('/Users/jinwenliu/github/.env/.env', override=True)


gg = BigQueryClient(
    project_id = os.getenv('GCP_PROJECT_ID'),
    dataset_id = os.getenv('GCP_DATASET_ID'),
    key_file=os.getenv('GCP_KEY_FILE')
)


sql = f"SELECT * FROM `{gg.project_id}.{gg.dataset_id}.fear_and_greed_index`"

# Use sql2df instead of run_sql to get DataFrame results
df = gg.sql2df(sql)

print(df)



#%%
# Test export_query_to_gcs - this uses BigQuery's native export functionality
# This method is much more efficient for large datasets as it exports directly from BigQuery to GCS
# without pulling data through your client machine

# Basic usage with sharding for large datasets
# gg.sql2gcs(
#     sql=f"SELECT * FROM `{gg.project_id}.{gg.dataset_id}.stock_prices`",
#     destination_uri="gs://mlfastflow/data/stock_prices.parquet"
# )


#%%
# gg.gcs2table(
#     gcs_uri="gs://mlfastflow/data/stock_prices.parquet",
#     table_id="stock_prices_from_gcs",
#     write_disposition="WRITE_TRUNCATE",

# )


#%%

# Test deleting a GCS folder
print("\n=== Testing GCS folder deletion ===")
success, count = gg.delete_gcs_folder(
    gcs_folder_path="gs://mlfastflow/data/queries1"  # Note: works with or without trailing slash
)
print(f"Folder deletion success: {success}, objects deleted: {count}")

# %%
gg.create_gcs_folder("gs://mlfastflow/data/queries1")
# %%
