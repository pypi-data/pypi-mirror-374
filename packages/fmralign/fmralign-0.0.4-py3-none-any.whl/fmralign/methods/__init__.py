from .identity import Identity
from .ot import OptimalTransport, SparseUOT
from .procrustes import Procrustes
from .ridge import RidgeAlignment
from .srm import DetSRM

__all__ = [
    "Identity",
    "OptimalTransport",
    "SparseUOT",
    "Procrustes",
    "RidgeAlignment",
    "DetSRM",
]
