_A='kernelprocess'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0054_kernelprocess_dashboard_exec_id_kernelprocess_name_and_more')];operations=[migrations.RemoveField(model_name=_A,name='is_live'),migrations.AddField(model_name=_A,name='is_delete',field=models.BooleanField(default=False))]