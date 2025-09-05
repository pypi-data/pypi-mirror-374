_A='session_id'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0093_cloudplan_is_destroyed_alter_cloudplan_is_verified')];operations=[migrations.AddField(model_name='aiplan',name=_A,field=models.CharField(max_length=100,null=True)),migrations.AddField(model_name='cloudplan',name=_A,field=models.CharField(max_length=100,null=True))]