import os, sys
from django.db import models
current_path = os.path.dirname(__file__)
app_path = os.path.dirname(current_path)
backend_path = os.path.dirname(app_path)
sys.path.insert(0, backend_path)
from models import *

#END OF QUBE
