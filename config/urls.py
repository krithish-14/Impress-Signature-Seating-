from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from catalog.admin import site as admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("", include("catalog.urls")),
]

urlpatterns += static("/brand-images/", document_root=settings.BRAND_IMAGES_ROOT)
