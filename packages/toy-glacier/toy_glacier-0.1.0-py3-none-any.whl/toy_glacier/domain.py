# **QUESTION** are these examples of over-building?
# @dataclass
# class IceMass:
#    qty: int

# @dataclass
# class AccumEvent:
#    qty: int

# @dataclass
# class AblationEvent:
#    qty: int


class Glacier:
    """A single glacier. Has a name and mass.
    Can gain mass through accumulation and los mass through ablation."""

    # def __init__(self, name: str, mass:IceMass):
    def __init__(self, name: str, mass: int):
        self.name = name
        self.mass = mass

    # def can_ablate(self, ablate_amount:AblationEvent) ->bool:
    def can_ablate(self, ablate_amount: int) -> bool:
        """Function checks if the specified ablation amount would cause glacier to disappear."""
        return self.mass >= ablate_amount  # .qty

    # def accumulate(self, accum_amount: AccumEvent):
    def accumulate(self, accum_amount: int):
        """Function to simulate accumulation. Increases mass by specified amount"""
        self.mass += accum_amount  # .qty

    # def ablate(self, ablate_amount:AblationEvent):
    def ablate(self, ablate_amount: int):
        """Function to simulate ablation. Decreases mass by specified amount."""
        if self.can_ablate(ablate_amount):
            self.mass -= ablate_amount  # .qtz
        else:
            raise ValueError("Glacier has disappeared, no more mass to lose.")


def make_glacier(name: str, glacier_mass: int):
    """Function to create a glacier object"""

    glacier = Glacier(name=name, mass=glacier_mass)
    return glacier
