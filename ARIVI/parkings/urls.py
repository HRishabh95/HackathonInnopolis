from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from .views import *

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

urlpatterns = [
    url(r'^patients/$', PatientListView.as_view(), name='patients-list'),


    url(r'^admins/$', AdminListView.as_view(), name='admin-list'),


]
