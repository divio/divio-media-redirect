import json
import logging

from aldryn_client import forms


logger = logging.getLogger(__name__)


class Form(forms.BaseForm):
    redirected_storages = forms.CharField(
        "Redirected storages",
        required=True,
        initial=json.dumps({"DEFAULT_STORAGE_DSN": "media"}),
        help_text=(
            "A dictionary, in JSON format, of storage DSN setting keys "
            "mapping to a prefix for the redirect view."
        ),
    )

    def to_settings(self, data, settings):
        from divio_media_redirect.storage import (
            WrappingRedirectingStorage,
            UnwrappableStorage,
        )

        WrappingRedirectingStorage.register()

        settings["REDIRECTED_STORAGES"] = json.loads(
            data["redirected_storages"]
        )

        wrapped = False

        for key, prefix in settings["REDIRECTED_STORAGES"].items():
            try:
                settings[key] = WrappingRedirectingStorage.wrap(
                    settings[key], prefix=prefix
                )
            except UnwrappableStorage as e:
                logger.warning(
                    "Ignoring unwrappable storage `%s` with scheme `%s`",
                    key,
                    e.scheme,
                )
                continue
            wrapped = True

        if wrapped:
            settings["ADDON_URLS"].append("divio_media_redirect.urls")

        return settings
