from django.contrib import admin
from django.urls import path, include
from . import views
from forum import views as user_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index , name='index'),
    path('forum/', include('forum.urls'), name ="forum"),
    path('my/', user_view.profile , name ="my_profile"),
    path('privacy/', views.privacy , name ="agreement"),
]

if settings.DEBUG:
    urlpatterns += static(settings.RANDOM_IMAGE_DIR,document_root=settings.RANDOM_IMAGE_DIR)