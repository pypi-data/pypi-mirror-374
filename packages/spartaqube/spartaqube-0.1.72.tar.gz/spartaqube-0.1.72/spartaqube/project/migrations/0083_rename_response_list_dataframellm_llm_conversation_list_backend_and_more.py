_A='dataframellm'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0082_dataframellm_dataframe_llm_id')];operations=[migrations.RenameField(model_name=_A,old_name='response_list',new_name='llm_conversation_list_backend'),migrations.AddField(model_name=_A,name='response_list_frontend',field=models.TextField(null=True))]