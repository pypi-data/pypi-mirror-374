from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):dependencies=[('project','0066_plotdbchart_is_created_from_dataframe')];operations=[migrations.AddField(model_name='dataframemodel',name='plot_db_chart',field=models.ForeignKey(null=True,on_delete=django.db.models.deletion.CASCADE,to='project.plotdbchart'))]