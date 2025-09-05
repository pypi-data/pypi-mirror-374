import os,sys,getpass,platform
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060,sparta_19f1944ceb
def sparta_f8e0507a40(full_path,b_print=False):
	B=b_print;A=full_path
	try:
		if not os.path.exists(A):
			os.makedirs(A)
			if B:print(f"Folder created successfully at {A}")
		elif B:print(f"Folder already exists at {A}")
	except Exception as C:print(f"An error occurred: {C}")
def sparta_65175fef66():
	if sparta_19f1944ceb():A='/app/APPDATA/local_db/db.sqlite3'
	else:C=sparta_a4e746f060();B=os.path.join(C,'data');sparta_f8e0507a40(B);A=os.path.join(B,'db.sqlite3')
	return A