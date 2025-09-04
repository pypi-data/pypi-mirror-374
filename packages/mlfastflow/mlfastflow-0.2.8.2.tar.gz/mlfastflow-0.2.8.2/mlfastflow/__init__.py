"""MLFastFlow - packages for fast dataflow and workflow processing."""

__version__ = "0.2.8.2"

# Import core components
from mlfastflow.core import Flow

# Import sourcing functionality
import mlfastflow.Sourcing as Sourcing
from mlfastflow.Sourcing import sourcing

# Import fastKNN functionality  
import mlfastflow.FastKNN as FastKNN
from mlfastflow.FastKNN import fastKNN
 
# Import BigQueryClient
import mlfastflow.bigqueryclient as bigqueryclient
from mlfastflow.bigqueryclient import BigQueryClient
import mlfastflow.bigqueryclientpolars as bigqueryclientpolars
from mlfastflow.bigqueryclientpolars import BigQueryClientPolars

# Import utils module (functions accessible via utils.function_name)
import mlfastflow.utils as utils

# Import utility functions directly
from mlfastflow.utils import timer_decorator, concat_files, profile, csv2parquet

# Make these classes and modules available at the package level
__all__ = [
    'Flow',
    'bigqueryclient',  # module
    'BigQueryClient',  # class
    'BigQueryClientPolars',  # class
    'bigqueryclientpolars',  # module
    'Sourcing',        # module, the Sourcing.py file
    'sourcing',        # class, the sourcing class in Sourcing.py
    'FastKNN',         # module, the FastKNN.py file
    'fastKNN',         # class, the fastKNN class in FastKNN.py
    'utils',           # module
    'timer_decorator', # function
    'concat_files',    # function
    'profile',         # function
    'csv2parquet',     # function
]
