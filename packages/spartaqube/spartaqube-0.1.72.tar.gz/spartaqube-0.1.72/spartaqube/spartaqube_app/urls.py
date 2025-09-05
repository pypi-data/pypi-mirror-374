from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_b91f5600dc.sparta_14bd49e5a9.qube_33c49cb534.sparta_6b4a28dd60'
handler500='project.sparta_b91f5600dc.sparta_14bd49e5a9.qube_33c49cb534.sparta_0464239ef2'
handler403='project.sparta_b91f5600dc.sparta_14bd49e5a9.qube_33c49cb534.sparta_f4229dae48'
handler400='project.sparta_b91f5600dc.sparta_14bd49e5a9.qube_33c49cb534.sparta_fec073e6de'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]