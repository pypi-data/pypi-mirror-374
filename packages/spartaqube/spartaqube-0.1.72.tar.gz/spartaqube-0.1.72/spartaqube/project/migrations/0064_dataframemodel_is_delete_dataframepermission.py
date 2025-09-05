_C='is_delete'
_B=False
_A=True
from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):dependencies=[('project','0063_dataframemodel_has_widget_password_and_more')];operations=[migrations.AddField(model_name='dataframemodel',name=_C,field=models.BooleanField(default=_B)),migrations.CreateModel(name='DataFramePermission',fields=[('id',models.BigAutoField(auto_created=_A,primary_key=_A,serialize=_B,verbose_name='ID')),('token',models.CharField(max_length=100,null=_A)),(_C,models.BooleanField(default=_B)),('date_created',models.DateTimeField(null=_A,verbose_name='Date created')),('dataframe_model',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='project.dataframemodel'))])]