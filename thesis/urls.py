from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# ADDED TO REGISTER DJANGO ADMIN
from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'KIDENGE.1185424@student.egerton.ac.ke', 'admin123')
        return HttpResponse("Admin created! Go to /admin")
    return HttpResponse("Admin already exists")
 # then visit this once: https://msc-thesis-project.onrender.com/createadmin/

urlpatterns = [
	path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Include all core app URLs
	# ... your existing URLs to register an admin...
    path('createadmin/', create_admin, name='create_admin'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
