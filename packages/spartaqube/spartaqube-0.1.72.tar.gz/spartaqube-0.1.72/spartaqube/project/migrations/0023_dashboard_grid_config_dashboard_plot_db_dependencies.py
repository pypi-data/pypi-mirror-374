_A='dashboard'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0022_dashboard_dashboardshared')];operations=[migrations.AddField(model_name=_A,name='grid_config',field=models.TextField(null=True)),migrations.AddField(model_name=_A,name='plot_db_dependencies',field=models.TextField(null=True))]