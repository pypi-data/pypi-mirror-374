_A='dataframellm'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0085_dataframellm_venv')];operations=[migrations.AddField(model_name=_A,name='max_retry',field=models.IntegerField(default=5)),migrations.AddField(model_name=_A,name='self_correcting',field=models.BooleanField(default=True))]