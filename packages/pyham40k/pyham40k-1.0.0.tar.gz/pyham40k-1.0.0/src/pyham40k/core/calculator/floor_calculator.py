from math import floor

from .real_calculator import Real_Calculator


# When non integer solutions are rounded down
# I.e. 0.5 wounds is just 0 wounds. You don't have 0.5 side on a die
class Floor_Calculator(Real_Calculator):
    
    VERBOSE_NAME = "Floor calculator"
    QUICK_REF = "Wounds are always integer"

    def get_attacks(self):
        return floor(
            super().get_attacks()
        )
    
    def get_damage(self):
        return floor(
            super().get_damage()
        )

    def calculate_total_unsvaed_wounds(self):
        return floor(
            super().calculate_total_unsvaed_wounds()
        )
