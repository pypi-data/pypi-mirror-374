import json,time,base64,requests
from datetime import datetime
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from django.conf import settings as conf_settings
from project.models import UserProfile,CloudPlan
def sparta_cf9a0b8141(data):return base64.urlsafe_b64encode(data).decode().rstrip('=')
def sparta_7f63e84328(obj):return sparta_cf9a0b8141(json.dumps(obj,separators=(',',':'),sort_keys=True).encode())
def sparta_246c0975d5(ttl_seconds=180):H='ES256';G='alg';A='big';B=ec.generate_private_key(ec.SECP256R1());C=B.public_key().public_numbers();I={'kty':'EC','crv':'P-256','x':sparta_cf9a0b8141(C.x.to_bytes(32,A)),'y':sparta_cf9a0b8141(C.y.to_bytes(32,A)),G:H,'use':'sig'};J={G:H,'typ':'JWT'};D=int(time.time());K={'iat':D,'exp':D+ttl_seconds};E=sparta_7f63e84328(J);F=sparta_7f63e84328(K);L=f"{E}.{F}".encode();M=B.sign(L,ec.ECDSA(hashes.SHA256()));N,O=decode_dss_signature(M);P=N.to_bytes(32,A)+O.to_bytes(32,A);Q=f"{E}.{F}.{b64url(P)}";return I,Q
def sparta_ba7bc02e18(cloud_key):
	Q='ipv4';P='errorMsg';J='status';I='error';F=cloud_key;D='res';R,S=sparta_246c0975d5(180);T={'cloud_key':F,'token':S,'jwk':R};G=requests.post(f"{conf_settings.SERVER_CF}/server-status",json=T,allow_redirects=False)
	if G.status_code!=200:
		K='Invalid params'
		try:A=json.loads(G.text);K=A[I]
		except:pass
		return{D:-1,P:K}
	L=-1;M=-1;H='initializing';E='localhost';A=json.loads(G.text)
	if A[D]==-1:
		N='Internal error'
		try:
			O=json.loads(A[I])
			if int(O[J])==404:
				U=json.loads(O['data'])[I]
				if U['code']=='not_found':
					N='Server does not exist';C=CloudPlan.objects.filter(cloud_key=F).all()
					if C.count()>0:B=C[0];B.is_destroyed=True;B.save()
		except:pass
		return{D:-1,P:N}
	elif A[D]==1:
		H=A[J]
		if H=='running':
			M=1;E=A[Q]
			try:
				V=requests.post(f"http://{E}/heartbeat",timeout=2)
				if V.status_code==200:
					L=1;C=CloudPlan.objects.filter(cloud_key=F).all()
					if C.count()>0:B=C[0];B.is_verified=True;B.ipv4=E;B.save()
			except Exception as W:print('except heartbeat');print(W)
	return{D:1,'status_server':M,'status_app':L,Q:f"http://{E}",J:H}