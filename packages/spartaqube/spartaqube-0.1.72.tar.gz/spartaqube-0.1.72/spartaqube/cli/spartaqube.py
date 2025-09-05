import typer,utils as utils_cli
from pprint import pprint
from cryptography.fernet import Fernet
import spartaqube_cli as spartaqube_cli
app=typer.Typer()
@app.command()
def runserver(port=None):spartaqube_cli.runserver(port)
@app.command()
def list():spartaqube_cli.list()
@app.command()
def sparta_dff6929791():spartaqube_cli.sparta_dff6929791()
@app.command()
def token(ip_addr,http_domain):A=spartaqube_cli.token(ip_addr,http_domain);print(A)
@app.command()
def sparta_4d4d41a39f():print('Hello world!')
if __name__=='__main__':app()