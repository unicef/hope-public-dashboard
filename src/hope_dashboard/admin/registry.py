from django.contrib import admin

REQUIRED_ADMIN_MODELS = {
    ("constance", "config"),
    ("analysis", "syncdailyaggregatesjob"),
}


def keep_required_admin_models() -> None:
    """Remove admin registrations that the public dashboard does not use."""
    for model in list(admin.site._registry):
        if (model._meta.app_label, model._meta.model_name) not in REQUIRED_ADMIN_MODELS:
            admin.site.unregister(model)
