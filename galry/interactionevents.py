from tools import enum

__all__ = ['InteractionEvents']

InteractionEvents = enum(
    "SwitchInteractionModeEvent",
    
    "PanEvent",
    "ZoomEvent",
    "ZoomBoxEvent",
    "ResetEvent",
    "ResetZoomEvent",
    )
