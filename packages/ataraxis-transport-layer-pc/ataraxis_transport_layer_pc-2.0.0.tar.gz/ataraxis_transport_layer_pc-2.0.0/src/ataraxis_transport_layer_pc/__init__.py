"""This library provides methods for establishing and maintaining bidirectional communication with Arduino and Teensy
microcontrollers over USB or UART serial interfaces.

See https://github.com/Sun-Lab-NBB/ataraxis-transport-layer-pc for more details.
API documentation: https://ataraxis-transport-layer-pc-api-docs.netlify.app/.
Authors: Ivan Kondratyev (Inkaros), Katlynn Ryu.
"""

from .helper_modules import CRCProcessor, COBSProcessor, CRCStatusCode, COBSStatusCode
from .transport_layer import (
    TransportLayer,
    PacketParsingStatus,
    DataManipulationCodes,
    list_available_ports,
    print_available_ports,
)

__all__ = [
    "COBSProcessor",
    "COBSStatusCode",
    "CRCProcessor",
    "CRCStatusCode",
    "DataManipulationCodes",
    "PacketParsingStatus",
    "TransportLayer",
    "list_available_ports",
    "print_available_ports",
]
