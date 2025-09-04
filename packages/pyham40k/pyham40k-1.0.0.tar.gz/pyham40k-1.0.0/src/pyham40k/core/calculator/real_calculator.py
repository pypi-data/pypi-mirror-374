from .base_calculator_strategy import Base_Calculator_Strategy


# Real as in operating with reals (not just integers).
# I.e. 0.5 wounds make sense
class Real_Calculator(Base_Calculator_Strategy):

    VERBOSE_NAME = "Real calculator"
    QUICK_REF = "Fraction of a wound is significant"
    
    def get_attacks(self) -> float:
        return self.attacker.attacks.expected_value()

    def get_hit_proportion(self) -> float:
        skill = self.attacker.skill

        # For torrent-like weapons that auto hit
        if not skill:
            return 1.0

        # The value that must be exceeded or equaled with the die roll to pass
        # Negative modifier reflects the rules: lower values grant more 
        # outcomes (die sides) that pass.
        to_pass = skill.value - \
            Base_Calculator_Strategy._clamp_modifier(skill.modifier)
        
        return Base_Calculator_Strategy._clamp_and_get_proportion_rerolled(
            to_pass,
            skill.reroll
        )

    def get_wound_proportion(self) -> float:
        strength = self.attacker.strength.value
        toughness = self.defender.toughness.value

        to_pass_base = None
        if 2 * strength <= toughness:
            to_pass_base = 6

        elif strength < toughness:
            to_pass_base = 5

        elif strength == toughness:
            to_pass_base = 4

        elif (strength > toughness) and not (strength >= 2 * toughness):
            to_pass_base = 3

        else:
            to_pass_base = 2

        to_wound = self.attacker.strength

        # The value that must be exceeded or equaled with the die roll to pass
        # Negative modifier reflects the rules: lower values grant more 
        # outcomes (die sides) that pass.
        to_pass = to_pass_base - \
            Base_Calculator_Strategy._clamp_modifier(to_wound.modifier)
        
        return Base_Calculator_Strategy._clamp_and_get_proportion_rerolled(
            to_pass,
            to_wound.reroll
        )

    def get_unsaved_proportion(self) -> float:
        pen = self.attacker.penetration
        sav = self.defender.save
        inv = self.defender.invulnerable

        # Negative modifier to pen will "worsen" it
        pen_mod = pen.value - Base_Calculator_Strategy._clamp_modifier(pen.modifier)
        sav_mod = sav.value - Base_Calculator_Strategy._clamp_modifier(sav.modifier)
        inv_mod = None
        if inv:
            inv_mod = inv.value - Base_Calculator_Strategy._clamp_modifier(
                inv.modifier
            )

        # Pen cannot become positive
        pen_clamp = min(pen_mod, 0)

        # Save cannot be improved better that 3+ against pen 0
        sav_clamp = sav_mod
        if (pen_clamp == 0) and (sav.value == 3) and (sav_mod < 3):
            sav_clamp = sav
        sav_clamp = max(sav_clamp, 2)

        # IDK how we can even get there, but for the sake of generality
        inv_clamp = None
        if inv:
            inv_clamp = Base_Calculator_Strategy._clamp_passing_value(inv_mod)

        sav_pass = sav_clamp - pen_clamp # pen_clamp is non-positive

        # Decide to use inv or sav
        if inv and (sav_pass > inv_clamp):
            # Use inv
            inv_prop = Base_Calculator_Strategy._proportion_passed(inv_clamp)
            inv_pro_reroll = Base_Calculator_Strategy._proportion_rerolled(
                inv_prop,
                inv.reroll
            )

            return 1.0 - inv_pro_reroll
        
        else:
            # Use sav
            sav_prop = Base_Calculator_Strategy._proportion_passed(sav_pass)
            sav_prop_reroll = Base_Calculator_Strategy._proportion_rerolled(
                sav_prop,
                sav.reroll
            )

            return 1.0 - sav_prop_reroll

    def get_damage(self) -> float:
        return self.attacker.damage.expected_value()

    def get_felt_proprtion(self) -> float:
        fnp = self.defender.feel_no_pain

        if not fnp:
            return 1.0
        
        # IDK about modifiers here, but for the sake of generality
        to_pass = fnp.value - \
            Base_Calculator_Strategy._clamp_modifier(fnp.modifier)
        
        # Here I assume we will never have FNP 1+ (that would be unplayable)
        return Base_Calculator_Strategy._clamp_and_get_proportion_rerolled(
            to_pass,
            fnp.reroll
        )
