from django.apps import AppConfig


class SocialnetworkingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'socialNetworking'

    def ready(self):
        import socialNetworking.signals