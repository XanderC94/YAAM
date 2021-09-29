from pathlib import Path
from typing import Tuple, Dict, Set

from objects.addon import AddonBase
from objects.binding import Binding
from objects.binding_type import BindingType

def objectify_json_settings(root: Path, json: dict) -> Tuple[Set[str], Dict[str, AddonBase], Dict[BindingType, Dict[str, Binding]]]:

    args : Set[str] = set()
    bases : Dict[str, AddonBase] = dict()
    bindings : Dict[BindingType, Dict[str, Binding]] = dict()

    if "arguments" in json:
        args.update(json['arguments'])

    if "addons" in json:
        for obj in json["addons"]:
            base = AddonBase.from_dict(obj)
            bases[base.name] = base

    if "bindings" in json:
        for (s, v) in json["bindings"].items():
            binding_type = BindingType.from_string(s)

            if binding_type not in bindings:
                bindings[binding_type] = dict()

            for obj in v:
                # remove slashes and make absolute
                if binding_type != BindingType.EXE and "path" in obj:
                    while obj["path"].startswith("../") or obj["path"].startswith("..\\"):
                        obj["path"] = obj["path"][3:]

                    while obj["path"].startswith("."):
                        obj["path"] = obj["path"][1:]
                        
                    if obj["path"].startswith("\\") or obj["path"].startswith("/"):
                        obj["path"] = obj["path"][1:]
                    
                    obj["path"] = root / Path(obj["path"])

                binding = Binding.from_dict(obj, binding_type)
                bindings[binding_type][binding.name] = binding

    return (args, bases, bindings)