import functools
import json
import math
import re
import unicodedata
from pathlib import Path

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.lib.plugins import DefaultTranslation

# CKAN's shipped defaults. Brand assets only replace these, so a logo or favicon
# configured in the ini or by a sysadmin still wins.
CKAN_DEFAULT_LOGO = "/base/images/ckan-logo.png"
CKAN_DEFAULT_FAVICON = "/base/images/ckan.ico"

MAP_DATA = Path(__file__).parent / "data" / "madagascar_regions.json"
MAP_LEVELS = 4


def new_datasets(limit=3):
    """The most recently created public datasets, for the home page."""
    result = tk.get_action("package_search")(
        {}, {"rows": limit, "sort": "metadata_created desc", "include_private": False}
    )
    return result["results"]


@functools.lru_cache(maxsize=1)
def _region_shapes():
    return json.loads(MAP_DATA.read_text(encoding="utf-8"))


def _match_key(text):
    """'Amoron'i Mania', 'amoron-i-mania' and 'Amoron I Mania' all match."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", ascii_text.lower())


def madagascar_map():
    """Region shapes with the number of public datasets tagged with each region.

    A dataset belongs to a region when one of its tags is the region's name, in
    Malagasy or French spelling; one facet query covers every region.
    """
    shapes = _region_shapes()
    facets = tk.get_action("package_search")(
        {}, {"rows": 0, "facet.field": ["tags"], "facet.limit": -1, "include_private": False}
    )["search_facets"]
    tags_by_key = {}
    for tag in facets.get("tags", {}).get("items", []):
        tags_by_key.setdefault(_match_key(tag["name"]), []).append(tag)

    regions = []
    for region in shapes["regions"]:
        keys = {_match_key(alias) for alias in region["aliases"]}
        tags = [tag for key in keys for tag in tags_by_key.get(key, [])]
        regions.append(dict(
            region,
            count=sum(tag["count"] for tag in tags),
            tag=max(tags, key=lambda t: t["count"])["name"] if tags else None,
        ))

    most = max((r["count"] for r in regions), default=0)
    for region in regions:
        region["level"] = math.ceil(MAP_LEVELS * region["count"] / most) if region["count"] else 0

    return {
        "view_box": shapes["viewBox"],
        "attribution": shapes["attribution"],
        "regions": regions,
        "most": most,
        "top": sorted((r for r in regions if r["count"]), key=lambda r: -r["count"])[:6],
    }


class NiceUiPlugin(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)
    p.implements(p.ITranslation)

    def update_config(self, config):
        tk.add_template_directory(config, "templates")
        tk.add_public_directory(config, "public")
        tk.add_resource("assets", "nice-ui")

        if config.get("ckan.site_logo") == CKAN_DEFAULT_LOGO:
            config["ckan.site_logo"] = "/nice-ui/logo-white.png"
        if config.get("ckan.favicon") == CKAN_DEFAULT_FAVICON:
            config["ckan.favicon"] = "/nice-ui/favicon.png"

    def get_helpers(self):
        return {
            "nice_ui_new_datasets": new_datasets,
            "nice_ui_madagascar_map": madagascar_map,
        }
