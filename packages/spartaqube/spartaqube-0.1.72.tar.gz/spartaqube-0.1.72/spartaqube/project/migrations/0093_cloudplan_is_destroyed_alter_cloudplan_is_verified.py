_A='cloudplan'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0092_cloudplan')];operations=[migrations.AddField(model_name=_A,name='is_destroyed',field=models.BooleanField(default=False)),migrations.AlterField(model_name=_A,name='is_verified',field=models.BooleanField(default=False))]