from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

from catalog.admin import site as admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("", include("catalog.urls")),
    re_path(
        r"^brand-images/(?P<path>.*)$",
        serve,
        {"document_root": settings.BRAND_IMAGES_ROOT},
    ),
]
