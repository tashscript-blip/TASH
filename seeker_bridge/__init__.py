"""
The Seeker's Bridge — A Living Pathway from Earth to Andromeda
Built with the Four Elements: Earth, Water, Air, Fire
"""

__all__ = ["walk_bridge", "bridge_status"]


def __getattr__(name):
    """Lazy-load from .walker so walk_bridge doesn't collide with the old module name."""
    if name in ("walk_bridge", "bridge_status"):
        import importlib
        wb = importlib.import_module(".walker", __name__)
        return getattr(wb, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
