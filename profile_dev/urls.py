from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from api.v1.views import helth_check_url_view


urlpatterns = [
    path("v1/", include("api.v1.urls")),
    path("", helth_check_url_view.HelthView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
