_E='Darwin'
_D='Windows'
_C=True
_B='errorMsg'
_A='res'
import os,subprocess,platform
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import sparta_a253265c85,sparta_0f6223a0af
def sparta_9f1de43185(folder_path):
	A=folder_path;A=sparta_a253265c85(A)
	if not os.path.isdir(A):return{_A:-1,_B:f"The folder path '{A}' does not exist."}
	C=platform.system()
	try:
		if C==_D:B=f'start cmd /c code "{A}"';os.system(B)
		elif C==_E:B=f'osascript -e \'tell application "Terminal" to do script "code \\"{A}\\" && exit"\'';subprocess.run(B,shell=_C)
		elif C=='Linux':B=f"gnome-terminal -- bash -c 'code \"{A}\"; exit'";subprocess.run(B,shell=_C)
		else:return{_A:-1,_B:f"Unsupported platform: {C}"}
	except Exception as D:return{_A:-1,_B:f"Failed to open folder in VSCode: {D}"}
	return{_A:1}
def sparta_46a11b5877(folder_path):
	A=sparta_a253265c85(folder_path)
	if not os.path.isdir(A):return{_A:-1,_B:f"The provided path '{A}' is not a valid directory."}
	B=platform.system()
	try:
		if B==_D:os.system(f'start cmd /K "cd /d {A}"')
		elif B=='Linux':subprocess.run(['x-terminal-emulator','--working-directory',A],check=_C)
		elif B==_E:C=f'''
            tell application "Terminal"
                do script "cd {A}"
                activate
            end tell
            ''';subprocess.run(['osascript','-e',C],check=_C)
		else:return{_A:-1,_B:'Unsupported operating system.'}
	except Exception as D:return{_A:-1,_B:f"Failed to open terminal at '{A}': {D}"}
	return{_A:1}