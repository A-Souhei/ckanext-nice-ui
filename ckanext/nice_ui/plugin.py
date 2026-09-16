import ckan.plugins as p
import ckan.plugins.toolkit as tk

# CKAN's shipped defaults. Brand assets only replace these, so a logo or favicon
# configured in the ini or by a sysadmin still wins.
CKAN_DEFAULT_LOGO = "/base/images/ckan-logo.png"
CKAN_DEFAULT_FAVICON = "/base/images/ckan.ico"


def new_datasets(limit=3):
    """The most recently created public datasets, for the home page."""
    result = tk.get_action("package_search")(
        {}, {"rows": limit, "sort": "metadata_created desc", "include_private": False}
    )
    return result["results"]


class NiceUiPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

    def update_config(self, config):
        tk.add_template_directory(config, "templates")
        tk.add_public_directory(config, "public")
        tk.add_resource("assets", "nice-ui")

        if config.get("ckan.site_logo") == CKAN_DEFAULT_LOGO:
            config["ckan.site_logo"] = "/nice-ui/logo-white.png"
        if config.get("ckan.favicon") == CKAN_DEFAULT_FAVICON:
            config["ckan.favicon"] = "/nice-ui/favicon.png"

    def get_helpers(self):
        return {"nice_ui_new_datasets": new_datasets}
