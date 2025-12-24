"""
Main URL Configuration for Celery Test Project
==============================================

This module defines the main URL routing for the entire Django project.

URL Patterns:
    - /admin/          : Django admin interface
    - /api/            : RESTful API endpoints for task management
    - /static/         : Static files (CSS, JS, images)
    - /media/          : User-uploaded media files

For more information on URL routing:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from celerytest import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

# Main URL patterns
urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # Include app URLs (all API endpoints)
    path('', include('app.urls')),
]

# Serve media files in development
# In production, use a web server (nginx/apache) to serve these
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Alternative static/media serving configuration
# Useful for production if web server is not configured
urlpatterns += [
    # Serve media files
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    
    # Serve static files
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]