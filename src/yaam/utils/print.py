'''
Print stuff to somewhere module
'''

from collections import defaultdict
from typing import List
from tabulate import tabulate
from yaam.model.mutable.addon import Addon


def print_addon_tableau(addons: List[Addon], printer=print):
    '''
    Print addon list as table to the specified printer stream
    '''
    data = defaultdict(list)
    for addon in sorted(addons, key=lambda x: (not x.binding.is_enabled, x.base.name)):
        table = addon.to_table()
        for (key, value) in table.items():
            data[key].append(value)

    if len(data):
        printer("Loaded addons: ")
        table = tabulate(data, headers="keys", tablefmt='rst', colalign=("left",))
        printer(f"\n{table}\n")
