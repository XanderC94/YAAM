'''
Game property validator
'''

from pathlib import Path
from typing import Any
from yaam.model.game.base import Game
from yaam.model.type.binding import BindingType
import yaam.utils.validators.url as validator

class PropertyValidator(object):
    '''
    Static property validator
    '''

    def __init__(self) -> None:
        self._error : str = ""

    def __call__(self, game: Game, property_value: Any) -> bool:
        return self.validate(game, property_value)

    def validate(self, game: Game, property_value: Any) -> bool:
        '''
        Validate implemented property
        '''
        return game is not None and property_value is not None

    @property
    def error_msg(self) -> str:
        '''
        Returns the related string error
        '''
        return self._error if self._error[-1] == '\n' else f"{self._error}\n"

class YesValidator(PropertyValidator):
    '''
    Always return true
    '''

    def validate(self, game: Game, property_value: Any) -> bool:
        return True

class AddonNameValidator(PropertyValidator):
    '''
    Addon base name validator
    '''

    def validate(self, game: Game, property_value: Any) -> bool:
        is_valid = False
        if isinstance(property_value, str):
            if len(property_value) > 0:
                if property_value not in game.settings.bases:
                    is_valid = True
                else:
                    self._error = f"Addon named {property_value} already exists!\n"
            else:
                self._error = "Addon name is empty!\n"
        else:
            self._error = "Specified property not of the required type.\n"

        return is_valid

class AddonURIValidator(PropertyValidator):
    '''
    Addon base uri validator
    '''

    def validate(self, game: Game, property_value: Any) -> bool:
        is_valid = False
        if isinstance(property_value, str):
            if len(property_value) > 0 and validator.url(property_value):
                is_valid = True
            else:
                self._error = "Addon URI is either empty or an invalid URI!\n"
        else:
            self._error = "Specified property not of the required type.\n"

        return is_valid

class BindingNameValidator(PropertyValidator):
    '''
    Binding name validator
    '''

    def validate(self, game: Game, property_value: Any) -> bool:
        is_valid = False
        if isinstance(property_value, str):
            if len(property_value) > 0:
                if property_value in game.settings.bases:
                    is_valid = True
                else:
                    self._error = f"No addon named {property_value} exists among the bases.\n"
            else:
                self._error = "Addon name is empty.\n"
        else:
            self._error = "Specified property not of the required type.\n"

        return is_valid

class BindingPathValidator(PropertyValidator):
    '''
    Binding path validator
    '''

    def validate(self, game: Game, property_value: Any) -> bool:
        is_valid = False
        if isinstance(property_value, str):
            if len(property_value) > 0:
                is_valid = True
            else:
                self._error = "Binding path is empty!\n"
        else:
            self._error = "Specified property not of the required type.\n"

        return is_valid

class BindingTypeValidator(PropertyValidator):
    '''
    Binding type validator
    '''

    def validate(self, game: Game, property_value: Any) -> bool:
        is_valid = False
        if isinstance(property_value, str):
            if BindingType.from_string(property_value) is not BindingType.NONE:
                is_valid = True
            else:
                self._error = "Binding type is not valid!\n"
        else:
            self._error = "Specified property not of the required type.\n"

        return is_valid
