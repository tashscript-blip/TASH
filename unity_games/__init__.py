"""
The Unity Games — A Collection of Rituals for Connection
"Let the people play. Let the people unite."
"""

__all__ = ["launch_festival"]


def __getattr__(name):
    """Lazy-load the festival to avoid RuntimeWarning with python -m."""
    if name == "launch_festival":
        import importlib
        fest = importlib.import_module(".festival", __name__)
        return getattr(fest, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
