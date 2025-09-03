
"""
URL Configuration for University Voting System
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from voting import views

# Main project URLs (university_voting/urls.py)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('voting.urls')),
    path('health/', views.health_check, name='health_check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
