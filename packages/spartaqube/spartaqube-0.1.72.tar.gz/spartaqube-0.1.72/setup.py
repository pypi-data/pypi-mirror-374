import os, json
import setuptools
import pkg_resources

def get_install_pandas_requires():
    try:
        # Check if pandas is already installed
        pkg_resources.get_distribution('pandas')
        return []  # Don't require pandas if it's already installed
    except pkg_resources.DistributionNotFound:
        return ['pandas==1.5.3']  # Install pandas 1.5.3 if it's not installed

def get_install_numpy_requires():
    try:
        # Check if numpy is already installed
        pkg_resources.get_distribution('numpy')
        return []  # Don't require numpy if it's already installed
    except pkg_resources.DistributionNotFound:
        return ['numpy==1.26.4']  # Install numpy 1.26.4 if it's not installed
    
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spartaqube", # Replace with your own username
    version='0.1.72',
    author="Spartacus",
    author_email="spartaqube@gmail.com",
    description="SpartaQube is a plug and play solution to visualize your data and build web components",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://spartaqube.com",
    packages=setuptools.find_packages(),
    scripts=['installer/spartaqube.sh', 'installer/spartaqube.bat', 'installer/spartaqube_launcher.py'],
    package_data={
        'spartaqube': [
            '**/*'
        ]
    },  # Include all files in all directories
    include_package_data=True,
    install_requires=[
        'anthropic',
        # 'aerospike',            # DYNAMIC OPTIONAL
        # 'arcticdb',
        # 'cassandra-driver',     # DYNAMIC OPTIONAL
        'channels==3.0.4',
        # 'clickhouse_connect',   # DYNAMIC OPTIONAL
        'cloudpickle',
        # 'couchdb',              # DYNAMIC OPTIONAL
        # 'cx_Oracle',            # DYNAMIC OPTIONAL
        'django>=4.0,<5.0',
        'django-channels',
        'django-cors-headers',
        'django_debug_toolbar',
        'django-picklefield',
        'django-prometheus',
        'djangorestframework',
        'duckdb',
        'gitpython',
        # 'gunicorn',
        # 'influxdb_client',      # DYNAMIC OPTIONAL
        'ipython==8.17.2',
        'ipykernel==6.29.4',
        'jupyter_client',
        # 'jupyter_core',
        # 'jupyterlab',
        'legacy-cgi==2.6.2',
        'loguru==0.7.2',
        'mysql-connector-python',
        'networkx',
        'nbconvert',
        'numpy>=1.18,<=4.0',   # Specify a version range instead of a fixed version
        # *get_install_numpy_requires(),  # Conditionally add numpy
        'openai',
        'openpyxl',
        'pandas>=1.0,<=4.0',    # Allow flexibility to avoid conflicts with installed versions
        # *get_install_pandas_requires(),  # Conditionally add pandas
        'Pillow',
        'psycopg2-binary',
        'pymongo',
        'pymssql',
        'PyMySQL',
        'pyodbc',
        'python-dateutil',
        'pytz',
        'pyzmq',
        'quantstats',
        # 'questdb',              # DYNAMIC OPTIONAL
        # 'redis',                # DYNAMIC OPTIONAL
        'requests',
        'requests-oauthlib',
        'simplejson',
        'SQLAlchemy',
        'statsmodels',
        'tiktoken',
        'tinykernel',
        'tqdm',
        'typer',
        'uvicorn',
        'uvicorn[standard]',
        # 'waitress',
        'websocket-client',
        'whitenoise',
        'yfinance==0.2.61',
        # Add any other dependencies your project requires
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)