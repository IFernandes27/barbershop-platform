from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    # URL para mudar idioma
    path("i18n/", include("django.conf.urls.i18n")),
]

# URLs traduzíveis
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),

    # Accounts — com namespace correto
    path(
        "accounts/",
        include(("accounts.urls", "accounts"), namespace="accounts")
    ),

    # Bookings (landing page, serviços, etc.)
    path(
        "",
        include(("bookings.urls", "bookings"), namespace="bookings")
    ),

    prefix_default_language=False,
)

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
