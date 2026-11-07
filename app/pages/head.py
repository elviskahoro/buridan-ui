import reflex as rx


def head_components() -> list[rx.Component]:
    return [
        rx.el.script(src="/fuse/fuse-init.js", type="module"),  # pyright: ignore[reportUnknownMemberType]  # reflex component factories are partially unknown
        rx.el.script(src="/fuse/searchFunction.js"),  # pyright: ignore[reportUnknownMemberType]  # reflex component factories are partially unknown
        rx.el.script("""  # pyright: ignore[reportUnknownMemberType]  # reflex component factories are partially unknown
            var interval = setInterval(function() {
                if (typeof window.Fuse === 'function' && typeof window.initializeFuse === 'function') {
                    clearInterval(interval);
                    fetch('/fuse/searchList.json')
                        .then(function(r) { return r.json(); })
                        .then(function(data) { window.initializeFuse(data); });
                }
            }, 50);
        """),
        rx.el.script(src="/prism/prism.js"),  # pyright: ignore[reportUnknownMemberType]  # reflex component factories are partially unknown
    ]
