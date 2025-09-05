import importlib.metadata
from channels.routing import ProtocolTypeRouter,URLRouter
from django.urls import re_path as url
from django.conf import settings
from project.sparta_31081a7413.sparta_bcd7c2816d import qube_22004dbe58,qube_f0f4305bc8,qube_a7bff60388,qube_165eed554d,qube_e44434504c,qube_3799c49304,qube_c7cde17cc3,qube_cdf6a3ed84,qube_2b6d02d76e,qube_03533ac8a1
from channels.auth import AuthMiddlewareStack
import channels
channels_ver=importlib.metadata.version('channels')
channels_major=int(channels_ver.split('.')[0])
def sparta_b16208fbd5(this_class):
	A=this_class
	if channels_major<=2:return A
	else:return A.as_asgi()
urlpatterns=[url('ws/statusWS',sparta_b16208fbd5(qube_22004dbe58.StatusWS)),url('ws/notebookWS',sparta_b16208fbd5(qube_f0f4305bc8.NotebookWS)),url('ws/wssConnectorWS',sparta_b16208fbd5(qube_a7bff60388.WssConnectorWS)),url('ws/pipInstallWS',sparta_b16208fbd5(qube_165eed554d.PipInstallWS)),url('ws/gitNotebookWS',sparta_b16208fbd5(qube_e44434504c.GitNotebookWS)),url('ws/xtermGitWS',sparta_b16208fbd5(qube_3799c49304.XtermGitWS)),url('ws/hotReloadLivePreviewWS',sparta_b16208fbd5(qube_c7cde17cc3.HotReloadLivePreviewWS)),url('ws/apiWebserviceWS',sparta_b16208fbd5(qube_cdf6a3ed84.ApiWebserviceWS)),url('ws/apiWebsocketWS',sparta_b16208fbd5(qube_2b6d02d76e.ApiWebsocketWS)),url('ws/chatbotWS',sparta_b16208fbd5(qube_03533ac8a1.ChatbotWS))]
application=ProtocolTypeRouter({'websocket':AuthMiddlewareStack(URLRouter(urlpatterns))})
for thisUrlPattern in urlpatterns:
	try:
		if len(settings.DAPHNE_PREFIX)>0:thisUrlPattern.pattern._regex='^'+settings.DAPHNE_PREFIX+'/'+thisUrlPattern.pattern._regex
	except Exception as e:print(e)