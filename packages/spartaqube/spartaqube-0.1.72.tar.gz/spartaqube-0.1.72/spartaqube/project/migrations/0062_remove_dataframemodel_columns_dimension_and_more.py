_A='dataframemodel'
from django.db import migrations
class Migration(migrations.Migration):dependencies=[('project','0061_dataframemodel_columns_dimension_and_more')];operations=[migrations.RemoveField(model_name=_A,name='columns_dimension'),migrations.RemoveField(model_name=_A,name='disk_size'),migrations.RemoveField(model_name=_A,name='rows_dimension')]