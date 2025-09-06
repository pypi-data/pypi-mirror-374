#!/usr/bin/env python
"""
Stub-File for CoolProp.
"""
iDmass: int
iHmass: int
ispeed_sound: int
iviscosity: int


def PropsSI(
    out: str,
    in1: str, val1: str | None = None,
    in2: str | None = None, val2: str | None = None,
    fluid: str | None = None) -> float: ...


class AbstractState:
    """The class contains various information about an abstract state of a
    fluid. It encompasses the equation of state (EOS)"""

    def __init__(self, backend: str, fluid: str) -> None: ...

    def set_mole_fractions(
        self, fractions: list[float] | tuple[float, ...]) -> None: ...

    def update(
        self, input_type: int, input1: float, input2: float) -> None: ...

    def keyed_output(self, output_type: int) -> float: ...

    def hmass(self) -> float: ...

    def smass(self) -> float: ...
