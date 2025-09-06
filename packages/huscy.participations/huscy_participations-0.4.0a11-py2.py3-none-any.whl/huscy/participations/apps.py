from django.apps import AppConfig


class HuscyApp(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'huscy.participations'

    class HuscyAppMeta:
        pass
