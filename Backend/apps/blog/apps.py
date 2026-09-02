from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'apps.blog'
    label = 'blog'

    def ready(self):
        from apps.blog import signals  # noqa: F401
