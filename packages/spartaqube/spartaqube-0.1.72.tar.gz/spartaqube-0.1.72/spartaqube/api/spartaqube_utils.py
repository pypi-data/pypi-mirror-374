import os
import sys
import subprocess
import shutil
import base64
import json
import copy
import hashlib
import uuid
import requests
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
from decimal import Decimal
from datetime import datetime, date, time, timedelta
from urllib.parse import urlparse, urlunparse

def extract_port(url_or_ip):
    '''
    Extracts the port number from a URL or IP address.
    '''
    parsed = urlparse(url_or_ip)
    port = parsed.port
    if port is None and ':' in url_or_ip:
        try:
            ip, port = url_or_ip.rsplit(':', 1)
            port = int(port)
        except ValueError:
            port = None
    return port

def replace_port(url_or_ip, new_port):
    '''
    Replace port in url
    '''
    try:
        # Parse the input using urlparse
        parsed = urlparse(url_or_ip)
        if parsed.netloc:  # If it's a valid URL
            # Split the netloc into hostname and current port (if any)
            if ':' in parsed.netloc:
                hostname, _ = parsed.netloc.rsplit(':', 1)
            else:
                hostname = parsed.netloc
            # Construct the new netloc with the new port
            new_netloc = f"{hostname}:{new_port}"
            # Reconstruct the URL with the new netloc
            updated_url = urlunparse(
                (parsed.scheme, new_netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
            )
            return updated_url
        elif ':' in url_or_ip:  # If it's a raw IP:port
            ip, _ = url_or_ip.rsplit(':', 1)
            return f"{ip}:{new_port}"
        else:
            # If no port exists and it's not a valid URL, add the new port
            return f"{url_or_ip}:{new_port}"
    except Exception as e:
        raise ValueError(f"Invalid input: {url_or_ip}. Error: {e}")

def is_scalar(input) -> bool:
    scalar_types = {
        int, str, float, bool, complex, type(None), bytes, bytearray,
        pd.Timestamp, pd.Timedelta, pd.Period, pd.Interval,
        pd.Categorical, pd.IntervalDtype, pd.CategoricalDtype,
        pd.SparseDtype, pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.Int64Dtype,
        pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype,
        pd.Float32Dtype, pd.Float64Dtype,
        pd.BooleanDtype, pd.StringDtype, pd.offsets.DateOffset,
        np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64,
        np.float16, np.float32, np.float64, np.complex64, np.complex128,
        np.bool_, np.bytes_, np.str_,
        datetime, date, time, timedelta,
        Decimal
    }
    
    return isinstance(input, tuple(scalar_types))
    
def process_scalar_args(args:list):
    '''
    Process scalar -> list for polymorphism
    '''
    def process_dataframe(df):
        cols = df.columns
        len_col = len(cols)
        if len_col >= 1:
            return [df[col] for col in cols] # list of series
        return df

    def process_scalar_list(input):
        if input is not None:
            if input.__class__.__name__.lower() == 'ndarray': # Convert to dataframe first if ndarray
                input = pd.DataFrame(input)
            
            if isinstance(input, pd.Series):
                return [input]
            if isinstance(input, pd.DataFrame):
                return process_dataframe(input)
            if isinstance(input, pd.DatetimeIndex):
                return [input.tolist()]
            if isinstance(input, pd.core.indexes.base.Index):
                return input.tolist()
            
            if len(input) > 0:
                if is_scalar(input[0]):
                    return [input]
                
                # If list of dataframes:
                if all(isinstance(df, pd.DataFrame) for df in input):
                    merged_df = pd.concat(input, axis=1)
                    return process_dataframe(merged_df)
                
                # If list of ndarray:
                if all(df.__class__.__name__.lower() == 'ndarray' for df in input):
                    input = [pd.DataFrame(df) for df in input]
                    merged_df = pd.concat(input, axis=1)
                    merged_df.columns = [f'Y{i+1}' for i in range(len(input))]
                    return process_dataframe(merged_df)
                
        return input
    
    args_to_scalar_process = ['x', 'y', 'r', 'datalabels', 'border', 'background', 'tooltips', 'border_style']
    for this_arg in args_to_scalar_process:
        try:
            args[this_arg] = process_scalar_list(args[this_arg])
        except:
            pass

    if 'ohlcv' in args:
        if isinstance(args['ohlcv'], pd.DataFrame):
            this_df = args['ohlcv']
            args['ohlcv'] = [this_df[col] for col in this_df.columns]

def rename_duplicate_columns(df):
    """
    Rename columns such that they are unique
    """
    # Get the current column names
    columns = df.columns.tolist()
    # Create a dictionary to count occurrences of column names
    counts = {}
    # Iterate through column names and rename duplicates
    new_columns = []
    for col in columns:
        if col in counts:
            counts[col] += 1
            new_columns.append(f"{col}_{counts[col]}")
        else:
            counts[col] = 0
            new_columns.append(col)
    
    # Rename the columns in the DataFrame
    df.columns = new_columns
    return df

def safe_to_json(df):
    """
    Try to convert the dataframe to JSON with specified parameters.
    If a TypeError occurs, convert problematic data to string and try again.
    """
    if len(df) == 0:
        return pd.DataFrame().to_json(orient='split', date_format='iso')
    
    try:
        res = df.to_json(orient='split', date_format='iso')
    except Exception as e:
        # Identify columns with non-serializable data
        non_serializable_columns = []
        for col in df.columns:
            try:
                df[[col]].to_json(orient='split', date_format='iso')
            except:
                non_serializable_columns.append(col)

        # Convert only the non-serializable columns to string
        for col in non_serializable_columns:
            df[col] = df[col].apply(lambda x: str(x) if not pd.isnull(x) else x)
        
        # Try to convert to JSON again
        res = df.to_json(orient='split', date_format='iso')
    
    return res

def convert_dataframe_to_json(data_df:pd.DataFrame) -> pd.DataFrame:
    return safe_to_json(data_df)

def convert_to_dataframe(input_data, variable_name=None) -> pd.DataFrame:
    '''
    Convert any input variable into a pandas DataFrame
    '''
    output_df = convert_to_dataframe_func(input_data)
    if output_df is not None:
        if len(list(output_df.columns)) == 1:
            if len(str(output_df.columns[0])) <= 1:
                if variable_name is not None:
                   output_df.columns = [variable_name]
    else:
        output_df = pd.DataFrame()

    return output_df

def convert_to_dataframe_func(input_data) -> pd.DataFrame:
    '''
    Convert any input variable into a pandas DataFrame
    '''
    # print("convert_to_dataframe_func input_data")
    # print(type(input_data))
    try:
        # Check if the input is already a pandas DataFrame
        if isinstance(input_data, pd.DataFrame):
            return input_data
        
        # If it's a pd.Series
        if isinstance(input_data, pd.Series):
            return input_data.to_frame()
        
        if isinstance(input_data, pd.DatetimeIndex):
            return pd.DataFrame(input_data.to_list())
        
        # If it's a dictionary, convert it to a DataFrame
        if isinstance(input_data, dict):
            input_data_cp = copy.deepcopy(input_data)
            for key in input_data_cp:
                if not isinstance(input_data_cp[key], (list, pd.Series)):
                    input_data_cp[key] = [input_data_cp[key]]
            
            return pd.DataFrame(input_data_cp)
            # return pd.DataFrame.from_dict(input_data)

        # If it's a list or a tuple, try to convert it to a DataFrame
        if isinstance(input_data, (list, tuple)):
            if len(input_data) > 0:
                if not is_scalar(input_data[0]): # In this case, it's possible that we have a list of dataframe for instance
                    # if all(isinstance(df, pd.DataFrame) for df in input_data):
                    
                    # Case of list of dictionary
                    is_list_of_dict = list(set([isinstance(elem, dict) for elem in input_data]))[0]
                    if is_list_of_dict:
                        res_df =  pd.DataFrame([input_data])
                        if len(res_df.columns) != len(set(res_df.columns)):
                            res_df = rename_duplicate_columns(res_df)
                        return res_df

                    input_data = [convert_to_dataframe_func(elem) for elem in input_data]
                    merged_df = pd.concat(input_data, axis=1)
                    if len(merged_df.columns) != len(set(merged_df.columns)):
                        merged_df = rename_duplicate_columns(merged_df)
                    return merged_df

            return pd.DataFrame(input_data)

        # If it's a NumPy array, convert it to a DataFrame
        # if 'numpy' in str(type(input_data)).lower():
        #     return pd.DataFrame(input_data)
        if input_data.__class__.__name__.lower() == 'ndarray':
            return pd.DataFrame(input_data)
        
        # If it's a scalar or any other type that can be converted to a scalar, create a DataFrame
        if is_scalar(input_data):
            return pd.DataFrame([input_data])

        # Raise an exception for unsupported data types
        try:
            return pd.DataFrame([input_data])
        except Exception as e:
            print("Except convert to dataframe")
            print(e)
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None
    
def get_ws_settings(api_key:str) -> list:
    return (Fernet(get_keygen_fernet().encode('utf-8'))).decrypt(base64.b64decode(api_key)).decode('utf-8').split('@')[1:]

def get_keygen_fernet() -> str:
    return base64.b64encode(hashlib.md5('spartaqube-api-key'.encode('utf-8')).hexdigest().encode('utf-8')).decode('utf-8')

def request_service(spartaqube_api_intance, service_name:str, data_dict:dict) -> dict:
    '''
    Web service request
    '''
    proxies_dict = {"http": os.environ.get('http_proxy', None), "https": os.environ.get('https_proxy', None)}
    data_dict['api_service'] = service_name
    json_data_params = {
        'jsonData': json.dumps(data_dict)
    }
    headers = {
        "Content-Type": "application/json"
    }
    url = f"{spartaqube_api_intance.domain_or_ip}/api_web_service"
    url = url.replace('localhost', '127.0.0.1')
    res_req = requests.post(url, json=json_data_params, headers=headers, proxies=proxies_dict)
    status_code = res_req.status_code
    if status_code != 200:
        print(f"An error occurred, status_code: {status_code}")
        return {
            'res': -1,
            'status_code': status_code,
        }

    return json.loads(res_req.text)

def upload_resources(spartaqube_api_intance, data_dict:dict, file_path:str) -> dict:
    '''
    Upload resources (file or folder)
    '''

    def upload_func(files):
        proxies_dict = {"http": os.environ.get('http_proxy', None), "https": os.environ.get('https_proxy', None)}
        json_data_params = {
            'jsonData': json.dumps(data_dict)
        }
        headers = {
            "Content-Type": "application/json"
        }
        url = f"{spartaqube_api_intance.domain_or_ip}:{spartaqube_api_intance.http_port}/api_web_service"
        # print("url  > "+str(url))
        res_req = requests.post(url, json=json_data_params, headers=headers, files=files, proxies=proxies_dict)
        status_code = res_req.status_code
        if status_code != 200:
            print(f"An error occurred, status_code: {status_code}")
            return {
                'res': -1,
                'status_code': status_code,
            }

        return json.loads(res_req.text)
    
    data_dict['api_service'] = 'upload'
    is_file = False
    if os.path.isfile(file_path):
        is_file = True

    if is_file:
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        files = {'file': (f"{file_name}.{file_extension}", open(file_path, 'rb'))}
        return upload_func(files)
    else: # We are dealing with a folder, we are going to recursively upload each file
        pass

def reinstall_channels():
    try:
        # Step 1: Uninstall channels
        print("Uninstalling 'channels'...")
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'channels', '-y'], check=True)

        # Step 2: Force remove any remaining files
        channels_path = "/usr/local/lib/python3.11/site-packages/channels"
        try:
            if shutil.os.path.exists(channels_path):
                print("Removing leftover 'channels' files...")
                shutil.rmtree(channels_path)
        except:
            pass

        # Step 3: Reinstall channels
        print("Reinstalling 'channels' v3.0.4...")
        # subprocess.run([sys.executable, '-m', 'pip', 'install', 'channels==3.0.4'], check=True)
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'channels==3.0.4', 
             '--trusted-host', 'pypi.org',
             '--trusted-host', 'pypi.python.org',
             '--trusted-host', 'files.pythonhosted.org'],
            check=True
        )

        # Step 4: Verify installation
        print("Verifying installation...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'channels'], capture_output=True, text=True)
        if 'Version: 3.0.4' in result.stdout:
            print("'channels' successfully reinstalled (v3.0.4).")
        else:
            print("Installation failed. Please investigate.")
    except subprocess.CalledProcessError as e:
        print(f"Error during process: {e}")
        
def process_dataframe_components(df_all):
    '''
    
    '''
    df_all["__index__"] = df_all.index
    try:
        df_all["__index__"] = pd.to_datetime(df_all["__index__"])
    except Exception:
        pass
    
    df_all = df_all.sort_values(by=["dispo", "__index__"], ascending=[True, True])
    df_all = df_all.drop(columns=["__index__"])
    return df_all

