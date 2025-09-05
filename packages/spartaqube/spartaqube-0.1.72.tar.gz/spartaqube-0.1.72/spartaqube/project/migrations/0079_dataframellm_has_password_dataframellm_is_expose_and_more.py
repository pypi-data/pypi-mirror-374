_B=False
_A='dataframellm'
from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),('project','0078_dataframellm')];operations=[migrations.AddField(model_name=_A,name='has_password',field=models.BooleanField(default=_B)),migrations.AddField(model_name=_A,name='is_expose',field=models.BooleanField(default=_B)),migrations.AddField(model_name=_A,name='is_public',field=models.BooleanField(default=_B)),migrations.AddField(model_name=_A,name='password_e',field=models.CharField(max_length=100,null=True)),migrations.AddField(model_name=_A,name='user',field=models.ForeignKey(null=True,on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL,verbose_name='User owner'))]