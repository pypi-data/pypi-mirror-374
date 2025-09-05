import os


def sparta_b5b8332b5e(post_data):
    current_path = os.path.dirname(__file__)
    backend_path = os.path.dirname(current_path)
    root_path = os.path.dirname(backend_path)
    file_path = post_data['filePath']
    if post_data['isFrontend']:
        full_file_path = os.path.join(root_path, 'frontend', 'js',
            'components', 'examples', file_path)
    else:
        full_file_path = os.path.join(root_path, 'backend', 'examples',
            file_path)
    with open(full_file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    return {'res': 1, 'output': f'{file_content}'}

#END OF QUBE
