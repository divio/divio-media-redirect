import json

from aldryn_client import forms


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
        from divio_media_redirect.storage import WrappingRedirectingStorage

        WrappingRedirectingStorage.register()

        redirected_storages = json.loads(data["redirected_storages"])

        for key, prefix in redirected_storages.items():
            settings[key] = WrappingRedirectingStorage.wrap(
                settings[key], prefix=prefix
            )

        settings["ADDON_URLS"].append("divio_media_redirect.urls")

        return settings
