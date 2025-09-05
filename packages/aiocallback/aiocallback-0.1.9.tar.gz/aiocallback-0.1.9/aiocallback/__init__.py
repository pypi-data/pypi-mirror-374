# ruff: noqa: E402,F401
from .events import (
    EventList,
    EventListMetaclass,
    EventWrapper,
    SelfEventWrapper,
    contextevent,
    event,
    subcontextevent,
    subclassevent,
    DefaultEventWrapper,
    DefaultSelfEventWrapper,
    defaultevent
)

__author__ = "Vizonex"

from .__version__ import __version__

__all__ = (
    "EventList",
    "EventListMetaclass",
    "EventWrapper",
    "SelfEventWrapper",
    "contextevent",
    "event",
    "subcontextevent",
    "subclassevent",
    "__version__",
    "__author__",
    "DefaultEventWrapper",
    "DefaultSelfEventWrapper",
    "defaultevent"
)

