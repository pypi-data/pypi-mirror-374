_A='aiplan'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0089_aiplan_userprofile_api_key_ai_plan_and_more')];operations=[migrations.AlterField(model_name=_A,name='b_use_personal_key',field=models.BooleanField(default=False)),migrations.AlterField(model_name=_A,name='is_api_plan_verified',field=models.BooleanField(default=False))]