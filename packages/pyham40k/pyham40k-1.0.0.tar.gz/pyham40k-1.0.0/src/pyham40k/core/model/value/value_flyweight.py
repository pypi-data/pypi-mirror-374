from .base_value import Base_Value
from .not_assigned_value import Not_Assigned_Value
from .non_positive_value import Non_Positive_Value
from .random_value import Random_Value
from .positive_value import Positive_Value

from pyham40k.core.model.reroll import Reroll


# Serves as a singleton when imported from its module
class Value_Flyweight:

    na: Not_Assigned_Value = Not_Assigned_Value()
    randoms: dict[int, Random_Value] = {}
    simples: dict[int, Positive_Value] = {}

    @staticmethod
    def get_not_assigned_value() -> Not_Assigned_Value:
        return Value_Flyweight.na

    @staticmethod
    def get_non_positive_value(
        in_value: int,
        in_modifier: int = 0,
        in_reroll: Reroll = Reroll.NO
    ) -> Non_Positive_Value:
        key = hash((in_value, in_modifier, in_reroll))

        return Value_Flyweight.__get_or_create_value(
            Value_Flyweight.simples,
            key,
            Non_Positive_Value,
            in_value = in_value,
            in_modifier = in_modifier,
            in_reroll = in_reroll
        )
        
    @staticmethod
    def get_positive_value(
        in_value: int,
        in_modifier: int = 0,
        in_reroll: Reroll = Reroll.NO
    ) -> Positive_Value:
        key = hash((in_value, in_modifier, in_reroll))

        return Value_Flyweight.__get_or_create_value(
            Value_Flyweight.simples,
            key,
            Positive_Value,
            in_value = in_value,
            in_modifier = in_modifier,
            in_reroll = in_reroll
        )

    @staticmethod
    def get_random_value(
        in_die_size: int,
        in_modifier: int = 0,
        in_reroll: Reroll = Reroll.NO,
        in_multiplier: int = 1
    ) -> Random_Value:
        key = hash((in_die_size, in_modifier, in_reroll, in_multiplier))

        return Value_Flyweight.__get_or_create_value(
            Value_Flyweight.randoms,
            key,
            Random_Value,
            in_die_size = in_die_size,
            in_multiplier = in_multiplier,
            in_modifier = in_modifier,
            in_reroll = in_reroll
        )
    
    @staticmethod
    def __get_or_create_value(
        lookup_dict: dict,
        lookup_obj: int,
        obj_class: type[Base_Value],
        **kw_args
    ) -> Base_Value:
        "Helper for object lookup. kw_args are passed to constructor"

        cached = lookup_dict.get(lookup_obj)

        if cached:
            return cached
        
        else:
            new_object = obj_class(**kw_args)
            lookup_dict[lookup_obj] = new_object

            return new_object
