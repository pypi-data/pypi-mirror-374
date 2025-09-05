_A='userprofile'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0038_rename_dashboard_venv_developer_developer_venv')];operations=[migrations.AddField(model_name=_A,name='is_size_reduced_api',field=models.BooleanField(default=False)),migrations.AddField(model_name=_A,name='is_size_reduced_plot_db',field=models.BooleanField(default=False))]