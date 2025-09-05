_A=True
from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),('project','0075_llmport_host')];operations=[migrations.CreateModel(name='LLMSettings',fields=[('id',models.BigAutoField(auto_created=_A,primary_key=_A,serialize=False,verbose_name='ID')),('is_autorun',models.BooleanField(default=False)),('cloud_model',models.CharField(default='gpt-3.5 turbo',max_length=100,null=_A)),('last_update',models.DateTimeField(null=_A,verbose_name='Last update')),('date_created',models.DateTimeField(null=_A,verbose_name='Date created')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL))])]