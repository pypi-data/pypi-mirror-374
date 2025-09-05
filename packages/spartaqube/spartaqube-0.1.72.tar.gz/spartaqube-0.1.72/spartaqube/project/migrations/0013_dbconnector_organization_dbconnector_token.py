_A='dbconnector'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0012_plotdbchart_is_public_widget')];operations=[migrations.AddField(model_name=_A,name='organization',field=models.CharField(max_length=100,null=True)),migrations.AddField(model_name=_A,name='token',field=models.CharField(max_length=100,null=True))]