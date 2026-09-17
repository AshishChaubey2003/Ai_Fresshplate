"""URL routing for the FreshPlate API.

Everything lives under /api/. The frontend is a separate static site, so Django
serves no pages except the admin.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(request):
    """Cheap endpoint for uptime checks (Render pings this)."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),

    # API
    path("api/users/", include("users.urls")),
    path("api/food/", include("food.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/donations/", include("donations.urls")),
    path("api/chatbot/", include("chatbot.urls")),

    # Interactive API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

# Django serves uploaded files only during development. In production this is
# handled by the web server or an object store (S3 / Cloudinary).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)