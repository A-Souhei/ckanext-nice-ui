# ckanext-nice-ui

A branded, modern look for CKAN, in Sahan'Aina's colours: a teal masthead with
the logo and site title, dataset cards, a restyled sidebar, buttons and forms,
and a matching footer. The home page has a photo hero with a large search, site
statistics, a map of Madagascar's regions shaded by dataset count, a photo
section from the field, and the newest datasets. The About page presents
Sahan'Aina, users, organizations and groups without an image get initials
avatars in brand colours, and resource formats get file icons. Help texts
(organizations, groups, datasets, profile, sysadmin screens) talk about "the
site" rather than "CKAN"; the footer keeps its CKAN credits.

Built with [Tailwind CSS](https://tailwindcss.com) v4 **on top of** CKAN's
Bootstrap, not instead of it.

## Requirements

| CKAN | Python | Status |
|---|---|---|
| 2.11 | 3.10 | tested with 2.11.6 |
| 2.10, 2.12 | | untested |

## Installation

```sh
pip install -e git+https://github.com/A-Souhei/ckanext-nice-ui.git#egg=ckanext-nice-ui
```

```ini
ckan.plugins = … datastore nice_ui xloader … pages …
```

In CKAN the first plugin to ship a template wins, so list `nice_ui` before the
extensions it restyles (ckanext-xloader, ckanext-pages).

Install it **editable** (`-e`): a regular wheel lands in
`site-packages/ckanext`, which CKAN's pre-seeded `ckanext` namespace never
searches. The compiled CSS is committed, so installing needs no Node or Tailwind.

If you also run a translation extension that harvests template strings (such as
[ckanext-tomalagasy](https://github.com/A-Souhei/ckanext-tomalagasy)), install
this one first.

## Configuration

| Setting | Effect |
|---|---|
| `ckan.site_title`, `ckan.site_description` | Header, home page hero and footer |
| `ckan.site_logo`, `ckan.favicon` | Left alone if set; CKAN's stock defaults are replaced by the Sahan'Aina logo and icon |
| `ckan.featured_groups`, `ckan.featured_orgs` | Featured cards under the newest datasets |
| `ckan.site_about` | Replaces the Sahan'Aina About page, as in core |
| `ckan.gravatar_default = disabled` | Users without a picture get initials avatars instead of Gravatar images (organizations and groups always do) |

With [ckanext-pages](https://github.com/ckan/ckanext-pages) enabled, the main
menu links its page index, and its list, page view and editor are restyled
(the editor's publish date is a native date input). With
[ckanext-xloader](https://github.com/ckan/ckanext-xloader), the DataStore tab of
a resource shows its upload log as a timeline.

## Region map

A public dataset counts towards a region when one of its tags is the region's
name — `Analamanga`, `Matsiatra Ambony` or `Haute Matsiatra`; case, accents,
spaces and hyphens are ignored. Each region links to its datasets, and one facet
query covers all 24.

The outlines in `ckanext/nice_ui/data/madagascar_regions.json` are simplified
from OCHA's [administrative boundaries](https://data.humdata.org/dataset/cod-ab-mdg)
(BNGRC, CC BY-IGO), credited under the map. To rebuild them, or to add a
spelling to a region's aliases, edit `tools/build_madagascar_map.py` and run it
on `mdg_admin1.geojson` from that dataset (standard library only):

```sh
python3 tools/build_madagascar_map.py mdg_admin1.geojson
```

## Translations

The few strings the templates add beyond CKAN's own are in
`ckanext/nice_ui/i18n`, with French shipped here and Malagasy in
ckanext-tomalagasy. After changing template text:

```sh
make i18n-extract   # refresh the .pot and the French .po
make i18n-compile   # after translating
```

Leave a string untranslated and CKAN's own translation still applies, except
for plurals: Babel compiles an empty plural entry as the English text, which
then overrides CKAN's. Translate every plural (`msgstr[0]`, `msgstr[1]`).

Templates format every translation with Python's `%` operator, so a literal
`%` in a translation ("100 %") breaks the page with a 500: write `%%`, or
rephrase.

## Why Tailwind sits on top of Bootstrap

CKAN's 210 core templates, its JavaScript modules (dropdowns, modals, the
collapsing navbar) and most extensions are written against Bootstrap 5.1.3, so
Bootstrap stays. Tailwind is added with three safeguards, set in
`tailwind/input.css`:

- **`prefix(tw)`** — CKAN uses class names that Tailwind also defines
  (`collapse`, `container`, `hidden`, `table`, `block`…). Unprefixed, Tailwind's
  `collapse` (`visibility: collapse`) would hide the mobile menu. Only `tw:`
  classes are generated.
- **no preflight** — Bootstrap's Reboot keeps owning the base styles.
- **`important`** — Tailwind v4 puts utilities in a cascade layer, and
  unlayered Bootstrap rules beat layered ones regardless of specificity.

Most of the restyle is plain CSS on Bootstrap's and CKAN's own classes (built
from the same Tailwind theme tokens), so it reaches every page, including those
of other extensions. `tw:` utilities are only used in the few templates this
extension overrides: the header logo block, the footer, and the home page.

Browsers too old for cascade layers (before 2022) ignore the Tailwind part and
fall back to the stock CKAN look, rather than breaking.

## Changing the design

Edit `tailwind/input.css` or the templates, then rebuild the CSS:

```sh
make css
```

This downloads the Tailwind **standalone CLI** (a single binary, no npm) at a
pinned version, verifies its SHA-256, and runs it in a throwaway container with
no network and only this repository mounted. Commit the regenerated
`ckanext/nice_ui/assets/nice-ui.css` with your change.

### Palette

Sampled from the Sahan'Aina logo, adjusted for WCAG AA contrast:

| Token | Hex | Use |
|---|---|---|
| `teal-900` | `#003228` | Masthead, hero, headings |
| `teal-950` | `#001f19` | Account bar, footer |
| `olive-700` | `#4f6908` | Buttons and links (6.3:1 on white) |
| `olive-600` | `#64820a` | Brand olive, decorative only (4.4:1 fails AA for text) |
| `lime-500` / `lime-300` | `#78a014` / `#b5d56a` | Focus rings, active nav, accents on teal |
| `sand-50` | `#f7f9f4` | Page background |

## License

ckanext-nice-ui — a branded look for CKAN
Copyright (C) 2026 Toavina and contributors

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version — the same license as CKAN itself.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along
with this program (see [LICENSE](LICENSE)). If not, see
<https://www.gnu.org/licenses/>.

The Sahan'Aina logos and photos under `ckanext/nice_ui/public/nice-ui/` are brand
assets and are not covered by this license. The region boundaries are BNGRC /
OCHA data under CC BY-IGO. The Fraunces font files under
`ckanext/nice_ui/public/nice-ui/fonts/` are under the SIL Open Font License
(see `OFL.txt` there).
