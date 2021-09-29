from pathlib import Path
from furl import furl
from objects.binding import Binding

class AddonBase(object):

    def __init__(self, name: str, update_url: furl):
        self._name = name
        self._update_url = update_url

    @property
    def name(self) -> str:
        return self._name

    @property
    def update_url(self) -> furl:
        return self._update_url

    @staticmethod
    def from_dict(json: dict):
        return AddonBase(json['name'], furl(json['uri'] if 'uri' in json else ""))

class Addon(AddonBase, Binding):

    def __init__(self, base: AddonBase, binding: Binding):
        self._name = base.name
        self._update_url = base.update_url
        self._path = binding.path
        self._enabled = binding.is_enabled
        self._update = binding.is_updateable
        self._binding_type = binding.typing

    def set_enabled(self, enabled: bool):
        self._enabled = enabled

    def to_table(self) -> dict:
        table : dict = {}

        table['name'] = self.name
        table['path'] = self.path.name
        table['update'] = self.is_updateable
        table['enabled'] = self.is_enabled

        return table
        