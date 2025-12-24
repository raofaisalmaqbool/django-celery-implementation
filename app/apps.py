"""
Django App Configuration
========================

Configuration for the main application module.
"""

from django.apps import AppConfig


class AppConfig(AppConfig):
    """
    Configuration class for the main application.
    
    This class is automatically discovered by Django and used to configure
    the application. The name attribute must match the app's module name.
    """
    
    # Use BigAutoField for primary keys (Django 3.2+)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Application name - must match the directory name
    name = 'app'
    
    # Human-readable name for the app (shown in admin)
    verbose_name = 'Celery Task Management'
    
    def ready(self):
        """
        Perform initialization once the app is ready.
        
        This method is called when Django starts. Use it to import
        signal handlers or perform other startup tasks.
        """
        # Import signal handlers if needed
        # import app.signals
        pass
