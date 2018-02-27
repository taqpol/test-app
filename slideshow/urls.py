from rest_framework_jwt.views import obtain_jwt_token

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

import files.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^files/', include('files.urls')),
    # url(r'^api-token-auth/', obtain_jwt_token),
    # url(r'^api-token-refresh/', refresh_jwt_token),
]
