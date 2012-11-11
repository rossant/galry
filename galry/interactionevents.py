from tools import enum

__all__ = ['InteractionEvents']

# Default interaction events, may be custom with `extend_enum`.
InteractionEvents = enum(
    "SwitchInteractionModeEvent",    
    "PanEvent",
    "ZoomEvent",
    "ZoomBoxEvent",
    "RotationEvent",
    "ResetEvent",
    "ResetZoomEvent",
    )
