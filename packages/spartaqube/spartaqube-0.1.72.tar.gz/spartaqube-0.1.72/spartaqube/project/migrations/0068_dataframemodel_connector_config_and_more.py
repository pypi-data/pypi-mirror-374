_A='dataframemodel'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0067_dataframemodel_plot_db_chart')];operations=[migrations.AddField(model_name=_A,name='connector_config',field=models.TextField(null=True)),migrations.AddField(model_name=_A,name='is_dataframe_connector',field=models.BooleanField(default=False))]