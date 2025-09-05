import os, uuid, json

def generate_remote_token(length=20):
    return str(uuid.uuid4().hex)[:length]

def is_docker_version():
    return os.getenv('IS_REMOTE_SPARTAQUBE_CONTAINER', 'False') == 'True'

def get_remote_token() -> str:
    try:
        current_path = os.path.dirname(__file__)
        with open(os.path.join(current_path, 'remote_token.json'), "r") as json_file:
            loaded_data_dict = json.load(json_file)
        
        return loaded_data_dict['token']
    except:
        return None

def create_token_func() -> str:
    if is_docker_version():
        token = generate_remote_token()
        app_data_dict = {'token': token}
        current_path = os.path.dirname(__file__)
        with open(os.path.join(current_path, "remote_token.json"), "w") as json_file:
            json.dump(app_data_dict, json_file)

        return token

def set_token_at_startup():
    '''
    This is executed on the remote docker server only
    '''
    if is_docker_version():
        remote_token = get_remote_token()
        b_generate_new_token = True
        if remote_token is not None:
            if len(remote_token) > 0:
                b_generate_new_token = False

        if b_generate_new_token:
            create_token_func()
            
