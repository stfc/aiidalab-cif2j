"""Central visual theme for the AiiDAlab CIF2J application.

This module provides a single stylesheet, injected once at the application root,
that gives the app a consistent modern look. It is built on CSS custom
properties (design tokens) so the whole app can be retuned from one place, and
so that dark mode is a matter of overriding a handful of variables.

Usage
-----
Add :data:`APP_ROOT_CLASS` to the top-level application container and include the
widget returned by :func:`cif2j_theme` once among its children::

    view = ipw.VBox(children=[cif2j_theme(), header, body, footer])
    view.add_class(APP_ROOT_CLASS)

All rules are scoped under ``.{APP_ROOT_CLASS}`` so the theme does not leak into
other AiiDAlab apps sharing the same page. The design tokens live on ``:root``
(they are inert until referenced by a scoped rule).
"""

import ipywidgets as ipw

from aiidalab_cif2j.common.utils import CIF2J_BUTTON_CLASS

#: CSS class applied to the top-level application container. All theme rules are
#: scoped under this class.
APP_ROOT_CLASS = "cif2j-app"

#: CSS class applied to the header "app bar" (logo, subtitle and quick-access
#: buttons). See :func:`cif2j_appbar`.
APPBAR_CLASS = "cif2j-appbar"

#: Design tokens. Tweak these to retune the whole app.
#:
#: Dark mode is handled in two layers (see :data:`_DARK`):
#:
#: 1. *Primary* — the neutral palette tokens inherit JupyterLab/Voila's own
#:    ``--jp-*`` theme variables. Jupyter swaps those values when the user
#:    changes theme, so the app automatically tracks the active Jupyter theme
#:    (light, dark, or custom) with no extra work.
#: 2. *Fallback* — each neutral references a ``*-fallback`` variable as the
#:    second ``var()`` argument, used only when Jupyter's tokens are absent.
#:    Those fallbacks are light by default and switched to dark by the OS
#:    ``prefers-color-scheme`` block in :data:`_DARK`.
#:
#: The CIF2J blue accent is kept as a brand colour (not inherited from
#: Jupyter's brand blue); it and the shadows get dark-mode variants in both the
#: Jupyter-dark and OS-dark blocks.
_TOKENS = """
:root {
    /* Radii */
    --cj-radius: 10px;
    --cj-radius-lg: 16px;

    /* Elevation */
    --cj-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.15);
    --cj-shadow-md: 0 3px 8px rgba(0, 0, 0, 0.22);

    /* Spacing rhythm */
    --cj-gap: 12px;
    --cj-pad: 20px;
    /* Vertical gap between wizard step cards. */
    --cj-step-gap: 4px;

    /* Typography. A native system-font stack: always available offline (no
       web font to download), using whatever high-quality UI font the user's
       OS already ships. */
    --cj-font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
        Ubuntu, Cantarell, "Helvetica Neue", Arial, sans-serif;

    /* Brand accent (kept, not inherited from Jupyter). */
    --cj-accent: #1565c0;
    --cj-accent-contrast: var(--jp-ui-inverse-font-color1, #ffffff);

    /* Neutral palette: inherit Jupyter's theme tokens, falling back to our own
       light values (which the OS-dark block flips to dark) when absent. */
    --cj-surface: var(--jp-layout-color1, var(--cj-surface-fallback));
    --cj-surface-muted: var(--jp-layout-color2, var(--cj-surface-muted-fallback));
    --cj-border: var(--jp-border-color1, var(--cj-border-fallback));
    --cj-text: var(--jp-ui-font-color1, var(--cj-text-fallback));
    --cj-text-muted: var(--jp-ui-font-color2, var(--cj-text-muted-fallback));

    /* Light fallbacks (used only when the --jp-* tokens above are undefined). */
    --cj-surface-fallback: #ffffff;
    --cj-surface-muted-fallback: #f5f6f8;
    --cj-border-fallback: #e2e5ea;
    --cj-text-fallback: #1f2933;
    --cj-text-muted-fallback: #6b7280;
}
"""

#: Sleek button styling, driven by the shared design tokens. ``!important`` is
#: required to win over the default ipywidgets/Jupyter button rules.
#:
#: The generic ``.jupyter-button`` selector styles *every* button rendered
#: inside the app — including those from imported widgets (aiidalab-widgets-base,
#: alc-aiidalab-widgets) — so the look is consistent without having to tag each
#: one. ``.{CIF2J_BUTTON_CLASS}`` is kept so buttons rendered standalone
#: (outside the app root, via the unscoped stylesheet in utils) match too.
_BUTTONS = f"""
.{APP_ROOT_CLASS} .jupyter-button,
.{APP_ROOT_CLASS} .{CIF2J_BUTTON_CLASS} {{
    box-sizing: border-box !important;
    border-radius: var(--cj-radius) !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: var(--cj-shadow-sm);
    transition: transform 0.08s ease, box-shadow 0.15s ease;
}}
.{APP_ROOT_CLASS} .jupyter-button:hover,
.{APP_ROOT_CLASS} .{CIF2J_BUTTON_CLASS}:hover {{
    transform: translateY(-1px);
    box-shadow: var(--cj-shadow-md);
}}
.{APP_ROOT_CLASS} .jupyter-button:active,
.{APP_ROOT_CLASS} .{CIF2J_BUTTON_CLASS}:active {{
    transform: translateY(0);
    box-shadow: var(--cj-shadow-sm);
}}
"""

#: Card treatment for the wizard steps. ``WizardAppWidget`` renders as an
#: accordion, so each step panel is styled as an elevated surface. Selectors
#: cover both the classic-notebook/Voila (``.widget-accordion``) and JupyterLab
#: (``.jupyter-widget-Accordion``) class names.
_CARDS = f"""
.{APP_ROOT_CLASS} .widget-accordion .p-Accordion-child,
.{APP_ROOT_CLASS} .widget-accordion .lm-Accordion-child,
.{APP_ROOT_CLASS} .jupyter-widget-Accordion .lm-Accordion-child {{
    background: var(--cj-surface);
    border: 1px solid var(--cj-border);
    border-radius: var(--cj-radius-lg);
    box-shadow: var(--cj-shadow-sm);
    margin-bottom: var(--cj-step-gap);
    overflow: hidden;
}}
.{APP_ROOT_CLASS} .widget-accordion .p-Accordion-child .p-Collapse-contents,
.{APP_ROOT_CLASS} .widget-accordion .lm-Accordion-child .lm-Collapse-contents,
.{APP_ROOT_CLASS} .jupyter-widget-Accordion .lm-Accordion-child .lm-Collapse-contents {{
    padding: var(--cj-pad);
}}
"""

#: Header "app bar": logo, subtitle and quick-access buttons on a muted surface
#: band, matching the wizard-step card treatment so the page top reads as a
#: distinct region.
_APPBAR = f"""
.{APP_ROOT_CLASS} .{APPBAR_CLASS} {{
    background: var(--cj-surface-muted);
    border: 1px solid var(--cj-border);
    border-radius: var(--cj-radius-lg);
    box-shadow: var(--cj-shadow-sm);
    padding: var(--cj-pad);
    margin-bottom: var(--cj-gap);
    align-items: center;
}}
"""

#: Consistent form-control styling with a visible focus ring for accessibility.
_INPUTS = f"""
.{APP_ROOT_CLASS} .widget-dropdown select,
.{APP_ROOT_CLASS} .widget-text input,
.{APP_ROOT_CLASS} .widget-text input[type="number"],
.{APP_ROOT_CLASS} .widget-int-text input,
.{APP_ROOT_CLASS} .widget-float-text input {{
    /* border-box keeps the added border/padding inside the fixed height and
       width ipywidgets assigns, so controls neither clip their text nor
       overflow fixed-size parents. */
    box-sizing: border-box !important;
    /* Pin every single-line control to the framework's standard inline height
       so text inputs match the dropdowns rather than collapsing to the
       browser's (thinner) default input height. */
    min-height: var(--jp-widgets-inline-height, 28px) !important;
    height: var(--jp-widgets-inline-height, 28px) !important;
    border-radius: var(--cj-radius) !important;
    border: 1px solid var(--cj-border) !important;
    padding: 0 8px !important;
    transition: border-color 0.12s ease, box-shadow 0.12s ease;
}}
.{APP_ROOT_CLASS} .widget-textarea textarea {{
    /* Multi-line control: fill the height set via the widget's Layout (falling
       back to the inline height) and stay user-resizable, rather than being
       pinned to a single line like the inputs above. */
    box-sizing: border-box !important;
    height: 100% !important;
    min-height: var(--jp-widgets-inline-height, 28px) !important;
    border-radius: var(--cj-radius) !important;
    border: 1px solid var(--cj-border) !important;
    padding: 6px 8px !important;
    resize: vertical;
    transition: border-color 0.12s ease, box-shadow 0.12s ease;
}}
.{APP_ROOT_CLASS} .widget-dropdown select:focus,
.{APP_ROOT_CLASS} .widget-text input:focus,
.{APP_ROOT_CLASS} .widget-textarea textarea:focus,
.{APP_ROOT_CLASS} .widget-int-text input:focus,
.{APP_ROOT_CLASS} .widget-float-text input:focus {{
    border-color: var(--cj-accent) !important;
    box-shadow: 0 0 0 2px rgba(21, 101, 192, 0.25) !important;
    outline: none !important;
}}
"""

#: Typography, header and footer polish.
_CHROME = f"""
.{APP_ROOT_CLASS} {{
    font-family: var(--cj-font);
    color: var(--cj-text);
}}
.{APP_ROOT_CLASS} .logo img {{
    max-width: 100%;
    height: auto;
}}
.{APP_ROOT_CLASS} #subtitle {{
    font-weight: 600;
    letter-spacing: 0.2px;
    margin: 20px 0 16px;
}}
.{APP_ROOT_CLASS} footer {{
    margin-top: var(--cj-pad);
    padding-top: var(--cj-gap);
    border-top: 1px solid var(--cj-border);
    color: var(--cj-text-muted);
    font-size: 0.85em;
    text-align: center;
}}
"""

#: Dark-mode overrides, layered.
#:
#: The neutral palette needs no override here: it inherits Jupyter's ``--jp-*``
#: tokens, which Jupyter itself flips to dark. These blocks only adjust the
#: things Jupyter does not provide — the brand accent (to a lighter, more
#: legible blue on dark) and the shadows (deepened).
#:
#: * ``body[data-jp-theme-light="false"]`` fires when a Jupyter dark theme is
#:   active (primary trigger).
#: * ``@media (prefers-color-scheme: dark)`` additionally switches the neutral
#:   *fallbacks* to dark so the app still looks right when Jupyter's tokens are
#:   absent and the OS prefers dark (fallback trigger).
_DARK = """
body[data-jp-theme-light="false"] {
    --cj-accent: #64b5f6;
    --cj-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.5);
    --cj-shadow-md: 0 3px 8px rgba(0, 0, 0, 0.6);
}
@media (prefers-color-scheme: dark) {
    :root {
        --cj-accent: #64b5f6;
        --cj-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.5);
        --cj-shadow-md: 0 3px 8px rgba(0, 0, 0, 0.6);

        --cj-surface-fallback: #1e2228;
        --cj-surface-muted-fallback: #171a1f;
        --cj-border-fallback: #333a44;
        --cj-text-fallback: #e6e8eb;
        --cj-text-muted-fallback: #9aa3af;
    }
}
"""

_THEME = f"""
<style>
{_TOKENS}
{_BUTTONS}
{_CARDS}
{_APPBAR}
{_INPUTS}
{_CHROME}
{_DARK}
</style>
"""


def cif2j_appbar(children):
    """Return a header "app bar" ``VBox`` wrapping the given children.

    The returned box carries :data:`APPBAR_CLASS` and is styled as a muted
    surface band. Intended to hold the logo, subtitle and quick-access buttons
    at the top of a page.

    Parameters
    ----------
    children : list of ipywidgets.Widget
        Widgets to place inside the app bar (e.g. logo, subtitle, nav buttons).

    Returns
    -------
    ipywidgets.VBox
        The styled app-bar container.
    """
    bar = ipw.VBox(children=children, layout=ipw.Layout(margin="auto"))
    bar.add_class(APPBAR_CLASS)
    return bar


def cif2j_theme():
    """Return an ``HTML`` widget carrying the application theme stylesheet.

    Include the returned widget once among the children of the top-level
    application container, and apply :data:`APP_ROOT_CLASS` to that container.
    The ``<style>`` block is global to the page, so a single instance suffices.

    Returns
    -------
    ipywidgets.HTML
        A hidden widget holding the stylesheet.
    """
    return ipw.HTML(value=_THEME, layout=ipw.Layout(display="none"))
