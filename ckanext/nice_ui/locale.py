"""Remembering which language someone reads the portal in.

CKAN carries the locale in the URL — /fr/dataset — and nowhere else, so the
choice survives exactly as long as every link keeps the prefix. It does not
survive leaving the site and coming back: the SAML round-trip returns to
`ckanext.saml2auth.default_fallback_endpoint`, built with no prefix, so whoever
picked French lands back on the default. On this portal ckanext-tomalagasy
makes that default Malagasy, which is why the language looks like it resets on
login.

The locale a page was served in is remembered in a cookie, and a later request
for a bare path is sent to that language once. This is independent of how
someone signed in, so a bookmark or a link from elsewhere lands in their
language too.

The prefix is never visible from here: CKAN's I18nMiddleware strips it off
PATH_INFO before Flask sees the request, so `request.path` is `/dataset` either
way. What it leaves behind is `CKAN_LANG` and `CKAN_LANG_IS_DEFAULT`, which say
both which language was chosen and whether the URL asked for it — exactly the
two things this needs."""
from __future__ import annotations

import ckan.plugins.toolkit as tk
from flask import redirect, request

COOKIE = "nice_ui_locale"
COOKIE_MAX_AGE = 365 * 24 * 60 * 60

# Requests that are not someone reading a page: sending any of these somewhere
# else would break a call rather than translate it. Kept alongside the endpoint
# test below because these are real views in production — saml2auth's /acs and
# /slo only look like static files on an install where SAML is switched off.
SKIP_PREFIXES = ("/api", "/uploads", "/base", "/webassets", "/util", "/_",
                 "/favicon", "/robots.txt", "/saml2", "/acs", "/slo")


def _offered():
    return tk.config.get("ckan.locales_offered") or []


def _asked_for():
    """The locale the URL carried, or nothing when it fell back to the default.

    Read from the environ rather than the path: by the time Flask runs, the
    prefix has already been stripped."""
    if request.environ.get("CKAN_LANG_IS_DEFAULT", True):
        return None
    locale = request.environ.get("CKAN_LANG")
    return locale if locale in _offered() else None


def _wanted():
    """The language to send a bare path to, or nothing to leave it alone."""
    remembered = request.cookies.get(COOKIE)
    if remembered not in _offered():
        return None
    # The default already renders in that language; a redirect would only cost
    # a round trip.
    if remembered == tk.config.get("ckan.locale_default"):
        return None
    return remembered


def _is_file():
    """A file rather than a page.

    Flask has matched the route by the time a before_request runs, so anything
    served from a public directory says so itself — which listing prefixes
    cannot, since `add_public_directory` gives every extension a root of its
    own and /nice-ui/favicon.png was being redirected because of it. An Accept
    header is no help here: it is the caller's wish, not what the URL is."""
    endpoint = request.endpoint or ""
    return endpoint == "static" or endpoint.endswith(".static")


def _readable():
    return (request.method in ("GET", "HEAD")
            and not _is_file()
            and not request.path.startswith(SKIP_PREFIXES)
            # A path carrying dot segments would go out as
            # "/fr/../../thing", which a browser resolves back past the prefix.
            # It never leaves this origin, but a Location should mean what it says.
            and ".." not in request.path
            and "text/html" in (request.headers.get("Accept") or ""))


def remember(app):
    """Wire both halves onto the Flask app."""

    @app.before_request
    def _restore():
        if not _readable() or _asked_for():
            return None
        locale = _wanted()
        if not locale:
            return None
        target = f"/{locale}{request.path}"
        if request.query_string:
            target += "?" + request.query_string.decode("utf-8", "replace")
        return redirect(target)

    @app.after_request
    def _remember(response):
        try:
            carried = _asked_for()
        except Exception:
            return response
        if carried and request.cookies.get(COOKIE) != carried:
            # A preference, not a credential — but nothing reads it from the
            # browser either, so it is closed to scripts like anything else.
            response.set_cookie(COOKIE, carried, max_age=COOKIE_MAX_AGE,
                                samesite="Lax", secure=request.is_secure,
                                httponly=True)
        return response

    return app
