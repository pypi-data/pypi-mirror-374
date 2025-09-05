_A=True
from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),('project','0091_aiplan_existing_api_key_ai_plan')];operations=[migrations.CreateModel(name='CloudPlan',fields=[('id',models.BigAutoField(auto_created=_A,primary_key=_A,serialize=False,verbose_name='ID')),('cloud_key',models.CharField(max_length=100)),('is_verified',models.BooleanField(default=_A)),('date_created',models.DateTimeField(null=_A,verbose_name='Date created')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL,verbose_name='User who registered the cloud server'))])]