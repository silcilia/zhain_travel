from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('panel/kelola/', admin.site.urls),
    path('', include('core.urls')),
]

# Menampilkan file media (gambar, brosur, dan bukti pembayaran)
# selama aplikasi berjalan dalam mode development.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )