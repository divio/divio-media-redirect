from django.conf import settings

from django_storage_url import dsn_configured_storage


urlpatterns = [
    dsn_configured_storage(dsn_setting).make_redirect_url_entry()
    for dsn_setting, prefix in getattr(
        settings, "REDIRECTED_STORAGES", {}
    ).items()
]
