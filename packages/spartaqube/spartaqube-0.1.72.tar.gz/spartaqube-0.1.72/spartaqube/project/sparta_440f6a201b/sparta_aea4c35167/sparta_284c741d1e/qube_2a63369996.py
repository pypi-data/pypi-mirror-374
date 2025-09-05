_O='{\n        "showTicks": True,\n        "renderTicks": {\n            "showTicks": True,\n            "divisions": 10,\n        },\n        "zones":{"bInvertColor":True,"bMiddleColor":True,"colorLeft":"#20FF86","colorMiddle":"#F8E61C","colorRight":"#FF0000","maxHeightDeviation":5,"tiltZones":55}\n    }'
_N="{'min': 0, 'max': 100, 'value': 34}"
_M='gauge1'
_L='12px'
_K='center'
_J='blue'
_I='font-size'
_H='text-align'
_G='color'
_F='from spartaqube import Spartaqube as Spartaqube'
_E='Example to plot a simple gauge with gauge.js'
_D='code'
_C='sub_description'
_B='description'
_A='title'
import json
from django.conf import settings as conf_settings
def sparta_852c623f9f(type=_M):B=_F;D={_G:_J,_H:_K,_I:_L};A=_N;C='{\n        "showTicks": True,\n        "renderTicks": {\n            "showTicks": True,\n            "divisions": 10,\n        },\n    }';return[{_A:f"{type.capitalize()}",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  title=['{type} example'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with custom options",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  title=['{type} example'], 
  options={C},
  height=500
)
plot_example"""}]
def sparta_fb06f3f572():return sparta_852c623f9f(type=_M)
def sparta_38e98f5092():return sparta_852c623f9f(type='gauge2')
def sparta_1b3b7fe508():type='gauge3';B=_F;D={_G:_J,_H:_K,_I:_L};A={'min':0,'max':100,'value':34};C=_O;return[{_A:f"{type.capitalize()}",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  title=['Gauge3 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  gauge_zones=[0,10,30,80,100],
  title=['Gauge3 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones and labels",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  title=['Gauge3 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom options",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  title=['Gauge3 example'], 
  options={C},
  height=500
)
plot_example"""}]
def sparta_6c0da2b236():type='gauge4';B=_F;D={_G:_J,_H:_K,_I:_L};A=_N;C=_O;return[{_A:f"{type.capitalize()}",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  title=['Gauge4 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  gauge_zones=[0,10,30,80,100],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones and labels",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones, labels and heights",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  gauge_zones_height=[2,6,10,14,18],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom options",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  title=['Gauge4 example'], 
  options={C},
  height=500
)
plot_example"""}]