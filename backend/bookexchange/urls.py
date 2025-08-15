"""
URL configuration for bookexchange project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

# Initialize the API
api = NinjaAPI(
    title="BookExchange API",
    version="1.0.0",
    description="API for the BookExchange social network platform",
)

# Import API routers
from accounts.api import router as accounts_router
from books.api import router as books_router
from exchanges.api import router as exchanges_router
from friendships.api import router as friendships_router
from messaging.api import router as messaging_router

# Add routers to the main API
api.add_router("/auth/", accounts_router, tags=["Authentication"])
api.add_router("/books/", books_router, tags=["Books"])
api.add_router("/friends/", friendships_router, tags=["Friendships"])
api.add_router("/exchanges/", exchanges_router, tags=["Exchanges"])
api.add_router("/messages/", messaging_router, tags=["Messaging"])

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
