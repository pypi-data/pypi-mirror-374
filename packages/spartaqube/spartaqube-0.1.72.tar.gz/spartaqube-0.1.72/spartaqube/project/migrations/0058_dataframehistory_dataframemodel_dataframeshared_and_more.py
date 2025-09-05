_K='user_group'
_J='share_rights'
_I='project.dataframemodel'
_H='dataframe_model'
_G='Last update'
_F='last_update'
_E='Date created'
_D='date_created'
_C='dataframesshared'
_B=False
_A=True
from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),('project','0057_dataframes_dataframesshared')];operations=[migrations.CreateModel(name='DataFrameHistory',fields=[('id',models.BigAutoField(auto_created=_A,primary_key=_A,serialize=_B,verbose_name='ID')),('df_blob',models.BinaryField(null=_A)),('dispo',models.DateTimeField(null=_A,verbose_name='Dispo date')),(_D,models.DateTimeField(null=_A,verbose_name=_E)),(_F,models.DateTimeField(null=_A,verbose_name=_G))]),migrations.CreateModel(name='DataFrameModel',fields=[('id',models.BigAutoField(auto_created=_A,primary_key=_A,serialize=_B,verbose_name='ID')),('table_name',models.CharField(max_length=100,null=_A)),('slug',models.SlugField(max_length=150,null=_A,unique=_A)),(_D,models.DateTimeField(null=_A,verbose_name=_E)),(_F,models.DateTimeField(null=_A,verbose_name=_G))]),migrations.CreateModel(name='DataFrameShared',fields=[('id',models.BigAutoField(auto_created=_A,primary_key=_A,serialize=_B,verbose_name='ID')),(_D,models.DateTimeField(null=_A,verbose_name=_E)),('is_delete',models.BooleanField(default=_B)),('is_owner',models.BooleanField(default=_B)),(_H,models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=_I)),(_J,models.ForeignKey(null=_A,on_delete=django.db.models.deletion.CASCADE,to='project.sharerights')),('user',models.ForeignKey(null=_A,on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL,verbose_name='User to share the indicator with')),(_K,models.ForeignKey(null=_A,on_delete=django.db.models.deletion.CASCADE,to='project.usergroup',verbose_name='Group to share the indicator with'))]),migrations.RemoveField(model_name=_C,name='dataframe'),migrations.RemoveField(model_name=_C,name=_J),migrations.RemoveField(model_name=_C,name='user'),migrations.RemoveField(model_name=_C,name=_K),migrations.DeleteModel(name='DataFrames'),migrations.DeleteModel(name='DataFramesShared'),migrations.AddField(model_name='dataframehistory',name=_H,field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=_I))]