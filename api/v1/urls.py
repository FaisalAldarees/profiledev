from django.urls import path

from api.v1.views import registration_views


app_name = 'api'

urlpatterns = [
    path('register/', registration_views.CreateUserView.as_view(), name='create'),
]