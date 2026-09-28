"""The name on a resource's view tab, in the language being read.

A view's title is written into its record once, when the view is created, and
never looked at again — so it is frozen in whatever locale was active then.
`ckan views create` run from the CLI has no request to take a language from and
falls back to ckan.locale_default; a view made through the web has the
language of whoever made it. This portal ended up holding three at once:
`Tabilao` on every datatables_view, `Statistiques et modèles` on most ml_views
and `Statistics & models` on one.

So a tab shows the view type's own title, translated now, whenever the stored
one is a title the type would have given itself in some language. A title
somebody actually chose is left alone — that is the only case where the stored
string is worth more than the current translation."""
from __future__ import annotations

import logging

import ckan.plugins.toolkit as tk
from ckan.lib import datapreview

log = logging.getLogger(__name__)

# One set per view type: every default name that type answers to, across the
# locales this portal offers. Built once — the catalogs do not change under a
# running process.
_defaults: dict = {}


def _known(view_type):
    if view_type in _defaults:
        return _defaults[view_type]

    plugin = datapreview.get_view_plugin(view_type)
    names = set()
    if plugin is not None:
        from flask_babel import force_locale
        locales = list(tk.config.get("ckan.locales_offered") or [])
        default = tk.config.get("ckan.locale_default")
        if default and default not in locales:
            locales.append(default)
        for locale in locales + ["en"]:
            try:
                with force_locale(locale):
                    info = plugin.info()
                    names.add(info.get("default_title"))
                    names.add(info.get("title"))
            except Exception:
                log.exception("could not read %s's title under %s", view_type, locale)
    _defaults[view_type] = {n for n in names if n}
    return _defaults[view_type]


def view_title(view):
    """What the tab should say."""
    try:
        stored = (view or {}).get("title")
        view_type = (view or {}).get("view_type")
        if not view_type:
            return stored
        if stored and stored not in _known(view_type):
            # Someone named this view themselves; that beats any default.
            return stored
        plugin = datapreview.get_view_plugin(view_type)
        if plugin is None:
            return stored
        return plugin.info().get("default_title") or stored
    except Exception:
        log.exception("could not settle the title of a %s view",
                      (view or {}).get("view_type"))
        return (view or {}).get("title")
