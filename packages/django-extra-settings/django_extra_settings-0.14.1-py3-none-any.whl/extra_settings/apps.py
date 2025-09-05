from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


class ExtraSettingsConfig(AppConfig):
    name = "extra_settings"
    verbose_name = settings.EXTRA_SETTINGS_VERBOSE_NAME
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from extra_settings import signals  # noqa: F401
        from extra_settings.models import Setting

        post_migrate.connect(Setting.set_defaults_from_settings, sender=self)
