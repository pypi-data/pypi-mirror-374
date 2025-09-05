_A='kernel'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0048_kernel_lumino_layout')];operations=[migrations.AddField(model_name=_A,name='is_static_variables',field=models.BooleanField(default=False)),migrations.AddField(model_name=_A,name='kernel_variables',field=models.TextField(null=True))]