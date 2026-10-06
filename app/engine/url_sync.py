import reflex as rx

def url_sync_engine() -> rx.Component:
    return rx.script("""
        window.__getPresetFromURL = function() {
            const params = new URLSearchParams(window.location.search);
            return params.get('preset');
        };

        window.__updatePresetURL = function(seed, push = true) {
            if (!seed) return;
            const url = new URL(window.location);
            if (url.searchParams.get('preset') === seed) return;
            
            url.searchParams.set('preset', seed);
            try {
                if (push) {
                    window.history.pushState({ preset: seed }, '', url);
                } else {
                    window.history.replaceState({ preset: seed }, '', url);
                }
            } catch (e) {
                console.error("Failed to update URL:", e);
            }
        };

        window.__syncSidebar = function(config) {
            if (!config || !window.refs) return;
            
            const refs = window.refs;
            const _BASE_THEMES = window.__BASE_THEMES;
            const _COLOR_THEMES = window.__COLOR_THEMES;
            const _RADIUS_OPTIONS = window.__RADIUS_OPTIONS;

            if (!_BASE_THEMES || !_COLOR_THEMES || !_RADIUS_OPTIONS) return;

            const _base = _BASE_THEMES.find(b => b.id === config['__base_id']);
            if (_base) {
                const _ring = (_base.light || {})['ring'] || '';
                if (refs['_client_state_setBase_theme_color']) refs['_client_state_setBase_theme_color'](_ring);
                if (refs['_client_state_setSelected_base_color_cs']) refs['_client_state_setSelected_base_color_cs'](_base.label);
            }

            const _colorId = config['__color_id'];
            if (_colorId) {
                const _col = _COLOR_THEMES.find(c => c.id === _colorId);
                if (refs['_client_state_setTheme_color']) refs['_client_state_setTheme_color'](_col ? (_col.light || {})['primary'] || '' : '');
                if (_col && refs['_client_state_setSelected_theme_cs']) refs['_client_state_setSelected_theme_cs'](_col.label);
            } else {
                if (refs['_client_state_setTheme_color']) refs['_client_state_setTheme_color']('');
                if (refs['_client_state_setSelected_theme_cs']) refs['_client_state_setSelected_theme_cs'](refs['_client_state_selected_base_color_cs']);
            }

            const _chartId = config['__chart_id'];
            if (_chartId) {
                const _ch = _COLOR_THEMES.find(c => c.id === _chartId);
                if (refs['_client_state_setChart_color']) refs['_client_state_setChart_color'](_ch ? (_ch.light || {})['primary'] || '' : '');
                if (_ch && refs['_client_state_setSelected_chart_cs']) refs['_client_state_setSelected_chart_cs'](_ch.label);
            } else {
                if (refs['_client_state_setChart_color']) refs['_client_state_setChart_color']('');
                if (refs['_client_state_setSelected_chart_cs']) refs['_client_state_setSelected_chart_cs'](refs['_client_state_selected_base_color_cs']);
            }

            if (config['__style_label'] && refs['_client_state_setSelected_style_cs']) refs['_client_state_setSelected_style_cs'](config['__style_label']);
            if (config['__font_label'] && refs['_client_state_setSelected_font_cs']) refs['_client_state_setSelected_font_cs'](config['__font_label']);

            const _radius = config['--radius'];
            if (_radius) {
                const _radOption = _RADIUS_OPTIONS.find(r => r[1] === _radius);
                if (_radOption && refs['_client_state_setSelected_radius_cs']) refs['_client_state_setSelected_radius_cs'](_radOption[0]);
            }
        };

        window.addEventListener('popstate', (event) => {
            const seed = (event.state && event.state.preset) || window.__getPresetFromURL();
            if (seed && window.refs) {
                const dark = window.refs['_client_state_darkmode'] || false;
                if (window.__generateFromSeed) {
                    const config = window.__generateFromSeed(seed, dark);
                    // Use the canonical seed so a Back-traversal to a stale
                    // `caaaoAgaa` history entry normalises it to `b0` in state,
                    // and replaceState the URL so the next no-op's dedup guard
                    // short-circuits instead of pushing a fresh `b0` entry.
                    const cs = config['__seed'] || seed;
                    // State + URL canonicalisation MUST run before the UI sync
                    // below: `_client_state_setTheme` is not a registered
                    // ClientStateVar in app/hooks.py at HEAD (a pre-existing
                    // defect), so calling it throws and would otherwise leave
                    // the canonicalisation lines unreachable in production —
                    // reintroducing the Back-button `caaaoAgaa` ↔ `b0` churn.
                    window.refs['_client_state_setSeed'](cs);
                    if (window.__updatePresetURL) window.__updatePresetURL(cs, false);
                    window.__syncSidebar(config);
                    try { window.refs['_client_state_setTheme'](config); }
                    catch (e) { /* setTheme unregistered at HEAD; UI sync is best-effort. */ }
                } else if (window._generateFromSeed) { // Check both global and engine scopes
                    const config = window._generateFromSeed(seed, dark);
                    const cs = config['__seed'] || seed;
                    window.refs['_client_state_setSeed'](cs);
                    if (window.__updatePresetURL) window.__updatePresetURL(cs, false);
                    window.__syncSidebar(config);
                    try { window.refs['_client_state_setTheme'](config); }
                    catch (e) { /* setTheme unregistered at HEAD; UI sync is best-effort. */ }
                }
            }
        });
    """)
