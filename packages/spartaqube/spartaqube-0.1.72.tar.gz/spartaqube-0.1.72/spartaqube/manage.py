"""Django's command-line utility for administrative tasks."""
import os
import sys
import re
import json


def sparta_0a0ccf6585(argv):
    """
    Parses the port number from the command-line arguments passed to the runserver command.Returns the port as an integer if found, otherwise defaults to 8000."""
    default_port = 8000
    port = default_port
    if 'runserver' in argv:
        runserver_index = argv.index('runserver')
        if len(argv) > runserver_index + 1:
            address_port = argv[runserver_index + 1]
            if address_port.isdigit():
                port = int(address_port)
            else:
                match = re.search(':(\\d+)$', address_port)
                if match:
                    port = int(match.group(1))
    return port


def sparta_92a349777f():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spartaqube_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?"
            ) from exc
    try:
        is_docker_platform = str(os.environ.get(
            'IS_REMOTE_SPARTAQUBE_CONTAINER', 'False')) == 'True'
    except:
        is_docker_platform = False
    from django.conf import settings as conf_settings
    if True:
        django_port = sparta_0a0ccf6585(sys.argv)
        app_data_dict = {'default_port': django_port}
        current_path = os.path.dirname(__file__)
        api_path = os.path.join(current_path, 'api')
        with open(os.path.join(api_path, 'app_data_asgi.json'), 'w'
            ) as json_file:
            json.dump(app_data_dict, json_file)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    sparta_92a349777f()

#END OF QUBE
