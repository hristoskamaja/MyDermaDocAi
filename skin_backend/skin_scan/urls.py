"""
Проектско ниво на urls.py - исто како leafscan/leafscan/urls.py.

/api/auth/        -> accounts.urls      (token-based login/register, го користи React admin)
/api/jwt-auth/     -> jwt_auth.urls     (JWT access/refresh, го користи Flutter апп-от)
/api/users/        -> accounts.user_urls (admin управување со корисници)
/api/              -> core.urls        (SkinCondition/Recommendation CRUD за admin панел)
/api/analyses/     -> analyses.urls    (scan-skin + историја на анализи)
/api/              -> analytics.urls   (dashboard/statistics за React admin панел)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("accounts.urls")),
    path("api/users/", include("accounts.user_urls")),

    path("api/jwt-auth/", include("jwt_auth.urls")),

    path("api/", include("core.urls")),

    path("api/analyses/", include("analyses.urls")),

    path("api/", include("analytics.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
