_D='subscription_id'
_C='cloudplan'
_B='session_id'
_A='aiplan'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0094_aiplan_session_id_cloudplan_session_id')];operations=[migrations.RemoveField(model_name=_A,name=_B),migrations.RemoveField(model_name=_C,name=_B),migrations.AddField(model_name=_A,name=_D,field=models.CharField(max_length=100,null=True)),migrations.AddField(model_name=_C,name=_D,field=models.CharField(max_length=100,null=True))]