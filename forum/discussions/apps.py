from django.apps import AppConfig


class DiscussionsConfig(AppConfig):
    name = 'discussions'

    def ready(self):
        import forum.discussions.signals
