import os, sys, json, base64, pickle, warnings, uuid, time
import webbrowser
import pandas as pd
import urllib.parse
from IPython.core.display import display, HTML
from IPython.display import IFrame
import warnings
warnings.filterwarnings("ignore", message="Consider using IPython.display.IFrame instead", category=UserWarning)

current_path = os.path.dirname(__file__)
base_project = os.path.dirname(current_path)
sys.path.insert(0, current_path)
sys.path.insert(0, base_project)

from spartaqube_utils import get_ws_settings, request_service, process_scalar_args, extract_port, replace_port, convert_to_dataframe, convert_dataframe_to_json, reinstall_channels
import spartaqube_install as spartaqube_install
warnings.filterwarnings("ignore", category=UserWarning)

class Spartaqube:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance.api_key = None

        return cls._instance
    
    def __init__(self, api_key=None, port=None, silent=False, b_open_browser=False, workers:int=None):
        '''
        If api_key specified, no need to specify port
        '''

        def print_success_infos():
            if not silent:
                print(f"GUI exposed at {self.domain_or_ip}")
                print(f"SpartaQube documentation at {self.domain_or_ip}/api")

        if self._initialized:  # Skip if already initialized
            if self.api_key != api_key: # We are trying to create a new instance with a different token to the previous instance
                pass
            else:
                print_success_infos()
                return
        self._initialized = True  # Mark as initialized

        # Init mandatory attributes
        self.silent = silent
        self.api_key = api_key
        self.plot_types_df = None

        b_start_local_server = False
        if api_key is None: # Public user with local server
            b_start_local_server = True
            if port is None: # Use default port
                port = spartaqube_install.generate_free_wsgi_port()
            else: # Use the user's port input
                pass

            self.domain_or_ip = f'http://localhost:{port}'
            self.api_token_id = 'public'
            if not silent:
                print("\nWarning: SpartaQube is currently running with the public user.\nTo enhance your experience, consider creating an account to obtain an API key.\n")
        else: # Use api_key for auth
            try:
                self.domain_or_ip, self.api_token_id = get_ws_settings(api_key)
            except:
                raise Exception("Invalid api_key")
            
            
            if len([elem for elem in ['localhost', '127.0.0.1'] if elem in self.domain_or_ip]) > 0:
                b_start_local_server = True
                # port = extract_port(self.domain_or_ip)
                # port = spartaqube_install.generate_free_wsgi_port(port)
                # self.domain_or_ip = replace_port(self.domain_or_ip, port)
            else:
                # No need to start a local spartaqube server in this case, as we'll use a remote one
                pass

        if b_start_local_server:
            sys.stdout.write("Preparing SpartaQube, please wait...")
            try:
                spartaqube_install.entrypoint(port=port, silent=silent, workers=workers, b_open_browser=False)
            except Exception as e:
                print("An error occurred")
                print(str(e))

                if "cannot import name '__version__' from 'channels'" in str(e):
                    try:
                        reinstall_channels()
                        time.sleep(1)
                        # Restart script
                        os.execv(sys.executable, [sys.executable] + sys.argv)
                    except Exception as e_channels:
                        print("An error occurred")
                        print(str(e_channels))

        # Finally test the application
        is_wsgi_running = False
        try:
            app_status_dict = self.get_status()
            if app_status_dict['res'] == 1:
                is_wsgi_running = app_status_dict['output'] == 1
        except:
            pass
    
        if is_wsgi_running:
            print_success_infos()
        else: # Application is not running
            error_msg = ''
            if not is_wsgi_running:
                if api_key is None: # Public user with local server
                    error_msg = f"SpartaQube application is not running on {self.domain_or_ip}. Make sure the port is not already allocated to another application."
                else:
                    error_msg = f"SpartaQube application is not running on {self.domain_or_ip}. Please check the api_key"
                
                self._initialized = False
                raise Exception(error_msg)
            
        if b_open_browser:
            webbrowser.open(f"http://localhost:{port}/home")

    def get_common_api_params(self) -> dict:
        return {
            'api_token_id': self.api_token_id,
        }

    def query_service(self, service_name:str, data_dict:dict) -> dict:
        '''
        POST requests
        '''
        return request_service(self, service_name=service_name, data_dict=data_dict)
    
    def get_status(self):
        data_dict = self.get_common_api_params()
        return self.query_service('get_status', data_dict)
    
    def get_status_ws(self):
        data_dict = self.get_common_api_params()
        return self.query_service('get_status_ws', data_dict)

    def stop_server(self):
        spartaqube_install.stop_server()

    def help(self):
        help_dict =  {
            'url': f"{self.domain_or_ip}/api",
            'widget': {
                'get_widgets': 'Spartaqube().get_widgets()',
                'get_widget': 'Spartaqube().get_widget(widget_id)',
                'get_widget_data': 'Spartaqube().get_widget(widget_id)'
            },
            'plot': {
                'get_plot_types': 'Spartaqube().get_plot_types()'
            },
            'dataframe': {

            },
            'connectors': {

            }
        }
        from pprint import pprint
        pprint(help_dict)

    # ******************************************************************************************************************
    # LIBRARY/WIDGETS
    # ******************************************************************************************************************
    def get_widgets(self) -> list:
        if not self.silent:
            if not hasattr(self, 'api_key'):
                print("\nWarning: SpartaQube is currently running with the public user.\nUse your API key to access your personal widgets.\n")
        data_dict = self.get_common_api_params()
        return self.query_service('get_widgets', data_dict)
    
    def get_widget(self, widget_id, width='60%', height=500, detached=False):
        if not self.silent:
            if not hasattr(self, 'api_key'):
                print("\nWarning: SpartaQube is currently running with the public user.\nUse your API key to access your personal widgets.\n")
        
        if not self.has_widget_id(widget_id):
            print("You don't have access to this widget")
            return
        
        if detached:
            webbrowser.open(f"{self.domain_or_ip}/plot-widget/{widget_id}")
            return
        
        return HTML(f'<iframe src="{self.domain_or_ip}/plot-widget/{widget_id}/{self.api_token_id}" width="{width}" height="{height}" frameborder="0" allow="clipboard-write"></iframe>')
        # return IFrame(src=f"{self.domain_or_ip}/plot-widget?id={widget_id}&api_token_id={self.api_token_id}", width=width, height=height)
        
    def get_widget_data(self, widget_id) -> list:
        '''
        Get widget data
        '''
        data_dict = self.get_common_api_params()
        data_dict['widget_id'] = widget_id
        res_dict = self.query_service('get_widget_data', data_dict)
        if res_dict['res'] == 1:
            res_list = []
            for json_data in res_dict['data']:
                data_dict = json.loads(json_data)
                res_list.append(pd.DataFrame(data=data_dict['data'], index=data_dict['index'], columns=data_dict['columns']))
            return res_list

        return res_dict

    def has_widget_id(self, widget_id) -> bool:
        data_dict = self.get_common_api_params()
        data_dict['widget_id'] = widget_id
        res_dict = self.query_service('has_widget_id', data_dict)
        if res_dict['res'] == 1:
            return res_dict['has_access']

        return False
    
    # ******************************************************************************************************************
    # PLOTS
    # ******************************************************************************************************************
    def iplot(self, *argv, width='100%', height=750, detached=False):
        '''
        Interactive plot using GUI
        '''
        if len(argv) == 0:
            raise Exception('You must pass at least one input variable to plot')
        else:
            notebook_variables_dict = dict()
            for key_idx, value in enumerate(argv):
                if value is None:
                    continue
                notebook_variables_df = convert_to_dataframe(value)
                notebook_variables_dict[key_idx] = convert_dataframe_to_json(notebook_variables_df)

            # Serialize the data as JSON
            iframe_id = str(uuid.uuid4())
            serialized_data = json.dumps(notebook_variables_dict)
            # Generate HTML form to POST data
            iframe_name = iframe_id
            if detached:
                iframe_name = "detached"
            iframe_html = f"""
            <form id="dataForm_{iframe_id}" action="{self.domain_or_ip}/plot-gui" method="POST" target="{iframe_id}">
                <input type="hidden" name="data" value='{serialized_data}' />
            </form>
            <iframe 
                id="{iframe_id}"
                name="{iframe_name}"
                width="{width}" 
                height="{height}" 
                frameborder="0" 
                allow="clipboard-write"></iframe>
            <script>
                // Submit the form automatically to send data to the iframe
                document.getElementById('dataForm_{iframe_id}').submit();
            </script>
            """
            return HTML(iframe_html)

    def plot(self, x:list=None, y:list=None, r:list=None, legend:list=None, labels:list=None, ohlcv:list=None, shaded_background:list=None, 
            datalabels:list=None, border:list=None, background:list=None, border_style:list=None, tooltips_title:list=None, tooltips_label:list=None,
            chart_type='line', interactive=True, widget_id=None, title=None, title_css:dict=None, stacked:bool=False, date_format:str=None, time_range:bool=False,
            gauge:dict=None, gauge_zones:list=None, gauge_zones_labels:list=None, gauge_zones_height:list=None, 
            dataframe:pd.DataFrame=None, dates:list=None, returns:list=None, returns_bmk:list=None,
            options:dict=None, width='100%', height=750, detached=False):
        '''
        Programmatically plot
        '''
        kwargs = locals()
        process_scalar_args(kwargs)
        notebook_variables_dict = dict()
        for key, var in kwargs.items():
            if var is None:
                continue
            if key == 'self':  # Skip 'self' argument
                continue
            notebook_variables_df = convert_to_dataframe(var)
            notebook_variables_dict[key] = convert_dataframe_to_json(notebook_variables_df)

        type_chart = None
        if 'chart_type' not in kwargs:
            if 'widget_id' not in kwargs:
                raise Exception("Missing chart_type parameter. For instance: chart_type='line'")
            else:
                type_chart = 0
        
        if type_chart is None:
            if self.plot_types_df is None:
                self.plot_types_df = self.get_plot_types(b_return_type_id=True)
            
            type_chart_series = self.plot_types_df[self.plot_types_df['ID'] == chart_type]            
            if len(type_chart_series) > 0:
                type_chart = type_chart_series.iloc[0].type_plot
            else:
                raise Exception("Invalid chart type. Use an ID found in the DataFrame get_plot_types()")
        
        # Url variables
        interactive = kwargs.get('interactive', True)
        widget_id = kwargs.get('widget_id', None)
        vars_html_dict = {
            'interactive_api': 1 if interactive else 0,
            'is_api_template': 1 if widget_id is not None else 0,
            'widget_id': widget_id,
        }
        json_vars_html = json.dumps(vars_html_dict)
        encoded_json_str = urllib.parse.quote(json_vars_html)
        # Data for iframe
        data_res_dict = dict() 
        data_res_dict['res'] = 1
        data_res_dict['notebook_variables'] = notebook_variables_dict
        data_res_dict['type_chart'] = type_chart
        data_res_dict['override_options'] = notebook_variables_dict.get('options', dict())
        # Serialize data
        serialized_data = json.dumps(data_res_dict)
        # Return iframe
        iframe_id = str(uuid.uuid4())
        iframe_name = iframe_id
        if detached:
            iframe_name = "detached"
        iframe_html = f"""
            <form id="dataForm_{iframe_id}" action="{self.domain_or_ip}/plot-api/{encoded_json_str}" method="POST" target="{iframe_id}">
                <input type="hidden" name="data" value='{serialized_data}' />
            </form>
            <iframe 
                id="{iframe_id}"
                name="{iframe_name}"
                width="{width}" 
                height="{height}" 
                frameborder="0" 
                allow="clipboard-write"></iframe>

            <script>
                // Submit the form automatically to send data to the iframe
                document.getElementById('dataForm_{iframe_id}').submit();
            </script>
            """
        return HTML(iframe_html)
    
    def plot_documentation(self, chart_type='line'):
        '''
        This function should display both the command (code) and display the output
        '''
        plot_types_df = self.get_plot_types()
        if len(plot_types_df[plot_types_df['ID'] == chart_type]) > 0:
            url_doc = f"{self.domain_or_ip}/api#plot-{chart_type}"
            print(url_doc)
        else:
            raise Exception("Invalid chart type. Use an ID found in the DataFrame get_plot_types()")

    def plot_template(self, *args, **kwargs):
        '''
        Plot data using existing widget template
        '''
        if 'widget_id' in kwargs:
            return self.plot(*args, **kwargs)

        raise Exception('Missing widget_id')

    def get_plot_types(self, b_return_type_id=False) -> pd.DataFrame:
        '''
        Returns the list of available plot type as dataframe
        '''
        data_dict = self.get_common_api_params()
        data_df = pd.DataFrame(self.query_service('get_plot_types', data_dict))
        if not b_return_type_id:
            cols = data_df.columns
            cols = [elem for elem in cols if elem != 'type_plot']
            data_df = data_df[cols]
        return data_df
    
    def plot_example(self, chart_type='line') -> dict:
        '''
        # TODO SPARTAQUBE: to implement
        '''
        pass 

    def save_plot(self, name, description=None, expose:bool=True, static:bool=False, public:bool=False, password=None):
        '''
        # TODO SPARATAQUBE: to implement
        '''
        pass

    # ******************************************************************************************************************
    # CONNECTORS
    # ******************************************************************************************************************
    def get_connectors(self):
        '''
        Return the list of available connectors
        '''
        data_dict = self.get_common_api_params()
        return self.query_service('get_connectors', data_dict)

    def get_connector_tables(self, connector_id):
        '''
        Return list of available tables for a connector
        '''
        data_dict = self.get_common_api_params()
        data_dict['connector_id'] = connector_id
        return self.query_service('get_connector_tables', data_dict)
    
    def get_data_from_connector(self, connector_id, table:str=None, sql_query:str=None, output_format:str=None, dynamic_inputs:dict=None):
        '''
        output_format: DataFrame, raw
        '''
        data_dict = self.get_common_api_params()
        data_dict['connector_id'] = connector_id
        data_dict['table_name'] = table
        data_dict['query_filter'] = sql_query
        data_dict['bApplyFilter'] = 1 if sql_query is not None else 0
        dynamic_inputs_params = []
        if dynamic_inputs is not None:
            for key, val in dynamic_inputs.items():
                dynamic_inputs_params.append({'input': key, 'default': val})

        data_dict['dynamic_inputs'] = dynamic_inputs_params
        res_data_dict:dict = self.query_service('get_data_from_connector', data_dict)
        if res_data_dict['res'] != 1:
            return res_data_dict
        
        is_df_format = False
        if output_format is None:
            is_df_format = True
        else:
            if output_format == 'DataFrame':
                is_df_format = True

        if is_df_format:
            if res_data_dict['res'] == 1:
                data_dict_ = json.loads(res_data_dict['data'])
            return pd.DataFrame(data_dict_['data'], index=data_dict_['index'], columns=data_dict_['columns'])
        else:
            return json.loads(res_data_dict['data'])

    # ******************************************************************************************************************
    # DATA STORE: SpartaQube internal dataframe connectors
    # ******************************************************************************************************************
    def format_dispo(self, dispo) -> str:
        dispo_blob = pickle.dumps(dispo)
        return base64.b64encode(dispo_blob).decode("utf-8")  # JSON-friendly string

    def put_df(self, df:pd.DataFrame, table_name:str, dispo=None, mode='append'):
        '''
        Insert dataframe
        mode: append or replace. If replace, it is based on the dispo date
        '''
        data_dict = self.get_common_api_params()
        blob = pickle.dumps(df)
        encoded_blob = base64.b64encode(blob).decode("utf-8")  # JSON-friendly string
        data_dict['df'] = encoded_blob
        data_dict['table_name'] = table_name
        data_dict['mode'] = mode
        data_dict['dispo'] = self.format_dispo(dispo)
        if mode not in ['append', 'replace']:
            raise Exception("Mode should be: 'append' or 'replace'")
        
        if isinstance(dispo, pd.Series) or (type(dispo).__name__ == 'ndarray' and type(dispo).__module__ == 'numpy'):
            dispo = list(dispo)
            data_dict['dispo'] = self.format_dispo(dispo)

        if isinstance(dispo, list):
            if len(dispo) != len(df):
                raise Exception("If you want to use a list of dispo, it must have the same length at the dataframe")
        
        res_dict = self.query_service('put_df', data_dict)
        if res_dict['res'] == 1:
            print("Dataframe inserted successfully!")
        return res_dict

    def drop_df(self, table_name, slug=None):
        '''
        Drop dataframe
        '''
        data_dict = self.get_common_api_params()
        data_dict['table_name'] = table_name
        data_dict['slug'] = slug
        res_dict = self.query_service('drop_df', data_dict)
        if res_dict['res'] == 1:
            print("Dataframe dropped successfully!")
        return res_dict

    def drop_dispo_df(self, table_name, dispo, slug=None):
        '''
        Drop specific dispo date
        '''
        data_dict = self.get_common_api_params()
        data_dict['table_name'] = table_name
        data_dict['dispo'] = self.format_dispo(dispo)
        data_dict['slug'] = slug
        res_dict = self.query_service('drop_dispo_df', data_dict)
        if res_dict['res'] == 1:
            print(f"Dataframe dropped successfully for dispo {dispo} !")
        return res_dict

    def drop_df_by_id(self, id):
        '''
        Drop the dataframe using id
        '''
        data_dict = self.get_common_api_params()
        data_dict['id'] = id
        res_dict = self.query_service('drop_df_by_id', data_dict)
        if res_dict['res'] == 1:
            print(f"Dataframe dropped successfully!")
        return res_dict

    def get_available_df(self) -> pd.DataFrame:
        '''
        Get available dataframes
        '''
        data_dict = self.get_common_api_params()
        return self.query_service('get_available_df', data_dict)
    
    def get_df(self, table_name, dispo=None, slug=None, b_concat=True) -> pd.DataFrame:
        '''
        Get dataframe
        '''
        data_dict = self.get_common_api_params()
        data_dict['table_name'] = table_name
        data_dict['dispo'] = self.format_dispo(dispo)
        data_dict['slug'] = slug
        res_dict = self.query_service('get_df', data_dict)
        if res_dict['res'] == 1:
            data_list = pickle.loads(base64.b64decode(res_dict['encoded_blob'].encode('utf-8')))
            data_df_list = [pickle.loads(elem_dict['df_blob']).assign(dispo=elem_dict['dispo']) for elem_dict in data_list]
            if b_concat:
                try:
                    df_all = pd.concat(
                        data_df_list, 
                        # ignore_index=True
                    )
                    df_all["__index__"] = df_all.index
                    try:
                        df_all["__index__"] = pd.to_datetime(df_all["__index__"])
                    except Exception:
                        pass
                    
                    df_all = df_all.sort_values(by=["dispo", "__index__"], ascending=[True, True])
                    df_all = df_all.drop(columns=["__index__"])
                    return df_all
                except Exception as e:
                    print("Could not concatenate all dataframes together with following error message:")
                    raise(str(e))
            else:
                return data_df_list
            
        return res_dict
    
    def has_dataframe_slug(self, slug) -> bool:
        data_dict = self.get_common_api_params()
        data_dict['slug'] = slug
        res_dict = self.query_service('has_dataframe_slug', data_dict)
        if res_dict['res'] == 1:
            return res_dict['has_access']

        return False
    
    def open_df(self, slug, width='100%', height=600, detached=False):
        if not self.silent:
            if not hasattr(self, 'api_key'):
                print("\nWarning: SpartaQube is currently running with the public user.\nUse your API key to access your personal widgets.\n")
        
        if not self.has_dataframe_slug(slug):
            print("You don't have access to this widget dataframe")
            return
        
        if detached:
            webbrowser.open(f"{self.domain_or_ip}/plot-dataframe/{slug}")
            return
        
        return HTML(f'<iframe src="{self.domain_or_ip}/plot-dataframe/{slug}/{self.api_token_id}"  width="{width}" height="{height}" frameborder="0" allow="clipboard-write"></iframe>')
        # return IFrame(src=f"{self.domain_or_ip}/plot-widget?id={widget_id}&api_token_id={self.api_token_id}", width=width, height=height)
        
    def open_data_df(self, data_df:pd.DataFrame, name='',  width='100%', height=600, detached=False):
        # Serialize the data as JSON
        iframe_id = str(uuid.uuid4())
        df_json = convert_dataframe_to_json(data_df)
        serialized_data = json.dumps(df_json)
        iframe_name = iframe_id
        if detached:
            iframe_name = name
        # Generate HTML form to POST data
        iframe_html = f"""
        <form id="dataForm_{iframe_id}" action="{self.domain_or_ip}/plot-gui-df" method="POST" target="{iframe_id}">
            <input type="hidden" name="data" value='{serialized_data}' />
            <input type="hidden" name="name" value='{name}' />
        </form>
        <iframe 
            id="{iframe_id}"
            name="{iframe_name}"
            width="{width}" 
            height="{height}" 
            frameborder="0" 
            allow="clipboard-write"></iframe>
        <script>
            // Submit the form automatically to send data to the iframe
            document.getElementById('dataForm_{iframe_id}').submit();
        </script>
        """
        return HTML(iframe_html)
