from files.views import file_policy_view, file_upload_complete_view

from django.config.urls import url

urlpatterns = [
    url(r'^policy-request/', file_upload_view),
    url(r'^upload-complete/', file_upload_complete_view),
]
