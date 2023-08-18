import hashlib
from urllib.parse import ParseResult, unquote, urlparse, urlunparse

from django.shortcuts import redirect
from django.urls import path, reverse

import furl
from django_storage_url import get_storage
from django_storage_url.backends import (
    register_storage_class,
)


SCHEME = "redirect"
UNWRAPPABLE_SCHEMES = {SCHEME, "file"}


class UnwrappableStorage(Exception):
    def __init__(self, scheme):
        self.scheme = scheme


class WrappingRedirectingStorage:
    @classmethod
    def register(cls):
        register_storage_class(SCHEME, f"{__name__}.{cls.__name__}")

    @classmethod
    def wrap(cls, dsn, prefix):
        url = furl.furl(dsn)
        if url.scheme in UNWRAPPABLE_SCHEMES:
            raise UnwrappableStorage(url.scheme)
        url.args["original_scheme"] = url.scheme
        url.args["redirect_view_prefix"] = prefix
        url.scheme = SCHEME
        return str(url)

    def __init__(self, dsn):
        dsn.scheme = dsn.args.pop("original_scheme")
        self._view_prefix = dsn.args.pop("redirect_view_prefix")
        self._wrapped = get_storage(dsn)
        self._url_name = self._compute_url_name(dsn)
        self._base = self._compute_base()
        self.base_url = self._wrapped.base_url

    def __getattr__(self, name):
        return getattr(self._wrapped, name)

    def make_redirect_url_entry(self):
        return path(
            f"{self._view_prefix}/<path:path>",
            self._redirect_to_storage_location,
            name=self._url_name,
        )

    def url(self, path):
        url = urlparse(self._wrapped.url(path))

        path = unquote(url.path)
        path = path[len(self._base.path) :]

        new_url = reverse(self._url_name, kwargs={"path": path})
        if url.query:
            new_url = f"{new_url}?{url.query}"
        if url.fragment:
            new_url = f"{new_url}#{url.fragment}"

        return new_url

    def _compute_url_name(self, dsn):
        hash = hashlib.shake_128(str(dsn).encode("utf-8")).hexdigest(6)
        return f"media-redirect-{hash}"

    def _compute_base(self):
        marker = "__MARKER__"
        url = urlparse(self._wrapped.url(marker))
        return ParseResult(
            url.scheme,
            url.netloc,
            url.path[: -len(marker)],
            "",
            "",
            "",
        )

    def _original_url(self, path, query=""):
        return urlunparse(
            (
                self._base.scheme,
                self._base.netloc,
                self._base.path + path,
                "",
                query,
                "",
            )
        )

    def _redirect_to_storage_location(self, request, path):
        return redirect(self._original_url(path, request.GET.urlencode()))
