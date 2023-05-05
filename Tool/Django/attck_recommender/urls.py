from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload, name='upload'),
    path('upload', views.upload, name='upload'),
    path('visualize', views.visualize, name='visualize'),
    path('search_siem', views.search_siem, name='search_siem'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)