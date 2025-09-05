_F='is_default'
_E='palette'
_D='palette_id'
_C='res'
_B='color'
_A=False
import uuid
from datetime import datetime
import pytz
UTC=pytz.utc
from project.models_spartaqube import PaletteColors
from project.sparta_440f6a201b.sparta_5c1010991f import qube_2808664dfd as qube_2808664dfd
DEFAULT_PALETTE=[{_B:'rgba(255, 99, 132, 0.8)'},{_B:'rgba(255, 159, 64, 0.8)'},{_B:'rgba(255, 205, 86, 0.8)'},{_B:'rgba(75, 192, 192, 0.8)'},{_B:'rgba(54, 162, 235, 0.8)'},{_B:'rgba(153, 102, 255, 0.8)'},{_B:'rgba(201, 203, 207, 0.8)'}]
def sparta_5437fd0356(user_obj):
	B=user_obj
	if B.is_anonymous:return DEFAULT_PALETTE
	C=PaletteColors.objects.filter(user=B,is_default=True,is_delete=_A).all()
	if C.count()>0:D=C[0];A=D.palette;A+=DEFAULT_PALETTE
	else:A=DEFAULT_PALETTE
	return A
def sparta_cc13fe8da2(json_data,user_obj):
	C=PaletteColors.objects.filter(user=user_obj,is_delete=_A).all().order_by('-is_default');B=[]
	for A in C:B.append({'name':A.name,_D:A.palette_id,_E:A.palette,_F:A.is_default})
	return{_C:1,'palette_list':B}
def sparta_437acd1f3c(json_data,user_obj):
	B=user_obj;A=json_data;E=A[_E];C=A[_F];D=datetime.now().astimezone(UTC);F=str(uuid.uuid4())
	if C:PaletteColors.objects.filter(user=B,is_delete=_A).update(is_default=_A)
	PaletteColors.objects.create(palette_id=F,user=B,palette=E,name=A['name'],is_default=C,last_update=D,date_created=D);return{_C:1}
def sparta_ecc18d5a7e(json_data,user_obj):
	B=user_obj;PaletteColors.objects.filter(user=B,is_delete=_A).update(is_default=_A);D=json_data[_D];C=PaletteColors.objects.filter(user=B,palette_id=D,is_delete=_A).all()
	if C.count()>0:A=C[0];A.is_default=True;A.last_update=datetime.now().astimezone(UTC);A.save()
	return{_C:1}
def sparta_db6cdec802(json_data,user_obj):
	C=json_data[_D];B=PaletteColors.objects.filter(user=user_obj,palette_id=C,is_delete=_A).all()
	if B.count()>0:A=B[0];A.is_delete=True;A.last_update=datetime.now().astimezone(UTC);A.save()
	return{_C:1}