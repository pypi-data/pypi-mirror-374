_A='aiplansubscription'
from django.db import migrations
class Migration(migrations.Migration):dependencies=[('project','0096_remove_aiplan_subscription_id_aiplansubscription')];operations=[migrations.RenameField(model_name=_A,old_name='subscription_id',new_name='subscription_key'),migrations.RemoveField(model_name=_A,name='tmp_key')]