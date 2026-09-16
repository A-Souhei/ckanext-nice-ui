# ckanext-nice-ui

A branded, modern look for CKAN, in Sahan'Aina's colours: a teal masthead with
the logo and site title, a home page with a large search, site statistics and
the newest datasets, dataset cards, a restyled sidebar, buttons and forms, and a
matching footer.

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
ckan.plugins = … nice_ui …
```

Install it **editable** (`-e`): a regular wheel lands in
`site-packages/ckanext`, which CKAN's pre-seeded `ckanext` namespace never
searches. The compiled CSS is committed, so installing needs no Node or Tailwind.

If you also run a translation extension that harvests template strings (such as
[ckanext-tomalagasy](https://github.com/A-Souhei/ckanext-tomalagasy)), install
this one first. Every label the templates add is an existing CKAN string, so
existing translations already cover them.

## Configuration

| Setting | Effect |
|---|---|
| `ckan.site_title`, `ckan.site_description` | Header, home page hero and footer |
| `ckan.site_logo`, `ckan.favicon` | Left alone if set; CKAN's stock defaults are replaced by the Sahan'Aina logo and icon |
| `ckan.featured_groups`, `ckan.featured_orgs` | Featured cards under the newest datasets |

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

The Sahan'Aina logos under `ckanext/nice_ui/public/nice-ui/` are brand assets and
are not covered by this license.
