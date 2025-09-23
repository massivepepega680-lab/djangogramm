from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts.views import home_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name="home"),
    path('', include("activities.urls")),
    path('posts/', include("posts.urls")),
    path('users/', include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)