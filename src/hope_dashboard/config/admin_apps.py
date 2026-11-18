from django.contrib.admin.apps import AdminConfig


class HopeAdminConfig(AdminConfig):
    def ready(self) -> None:
        super().ready()

        # Imported lazily: the admin package imports models and Django is not
        # ready to load them while INSTALLED_APPS is still being populated.
        from hope_dashboard.admin.registry import keep_required_admin_models  # noqa: PLC0415

        keep_required_admin_models()
