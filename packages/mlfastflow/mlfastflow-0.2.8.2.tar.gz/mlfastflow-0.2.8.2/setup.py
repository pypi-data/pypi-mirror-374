from setuptools import setup, find_packages

setup(
    name="mlfastflow",
    version="0.2.8.2",
    author="Xileven",
    author_email="hi@bringyouhome.com",
    description="packages for fast dataflow and workflow processing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/mlfastflow/",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "faiss-cpu",
        "fastparquet>=0.6.1",
        "google-auth>=2.0.0",
        "google-cloud-bigquery>=3.0.0",
        "google-cloud-storage>=2.0.0",
        "graphviz>=0.19.0",
        "ipywidgets>=7.6.0",  # Required for ydata-profiling
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "pandas-gbq>=0.17.0",
        "polars>=0.17.1",
        "pyarrow>=12.0.0",
        "pydantic>=2.5.1",
        "pydantic-core>=2.5.1",
        "pydantic-settings>=2.5.1",
        "pydantic-usage>=2.5.1",
        "python-dotenv>=0.19.0",
        "tqdm>=4.64.0",  # For progress bars and used in profiling
        "ydata-profiling>=4.5.0",  # For data profiling functionality (recommended over pandas-profiling)
    ],
    package_data={
        '': ['README.md'],
    },
    project_urls={
        'Documentation': 'https://pypi.org/project/mlfastflow/',
        'Source': 'https://pypi.org/project/mlfastflow/',
        'Tracker': 'https://pypi.org/project/mlfastflow/',
    }
)
