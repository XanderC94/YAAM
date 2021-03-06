'''
Yaam command line options module
'''
from enum import Enum
from collections import namedtuple
from typing import Any, Set, List

from yaam.utils.counter import ForwardCounter

OptionEntry = namedtuple(
    typename='OptionEntry',
    field_names=['index', 'aliases', 'default', 'action', 'descr'],
    defaults=[int(), set(), None, str(), str()]
)

OptionGroupEntry = namedtuple(
    typename='OptionGroupEntry',
    field_names=['index', 'options', 'mutually_exclusive'],
    defaults=[int(), list(), False]
)

counter = ForwardCounter()


class Option(Enum):
    '''
    Yaam command line options
    '''

    DEBUG = OptionEntry(
        index=counter.count(),
        aliases=set(["debug", "d"]),
        default=False,
        descr="Activate debug code",
        action="store_true"
    )

    GAME = OptionEntry(
        index=counter.count(),
        aliases=set(["game", "g"]),
        default=None,
        descr="Specify which game to manage",
        action="store"
    )

    UPDATE_ADDONS = OptionEntry(
        index=counter.count(),
        aliases=set(["update", "update-addons", "update_addons", "u"]),
        default=False,
        descr="Only update addons without running the game",
        action="store_true"
    )

    FORCE_ACTION = OptionEntry(
        index=counter.count(),
        aliases=set(["force", "f"]),
        default=False,
        descr="Force any specified action",
        action="store_true"
    )

    RUN_STACK = OptionEntry(
        index=counter.count(),
        aliases=set(["run", "run-stack", "run_stack", "r"]),
        default=False,
        descr="Only run the game without updating the addons",
        action="store_true"
    )

    EDIT = OptionEntry(
        index=counter.count(),
        aliases=set(["edit", "e"]),
        default=False,
        descr="Run YAAM edit repl",
        action="store_true"
    )

    EXPORT = OptionEntry(
        index=counter.count(),
        aliases=set(["export", "x"]),
        default=False,
        descr="Export YAAM settings",
        action="store_true"
    )

    GITHUB_USER = OptionEntry(
        index=counter.count(),
        aliases=set(["github-user", "github_user"]),
        default="",
        descr="Set github user",
        action="store"
    )

    GITHUB_API_TOKEN = OptionEntry(
        index=counter.count(),
        aliases=set(["github-api-token", "github_api_token"]),
        default="",
        descr="Set github API token",
        action="store"
    )

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Option):
            return self.index == o.index
        elif isinstance(o, str):
            return self.name == o or o in self.aliases
        else:
            return False

    @property
    def aliases(self) -> Set[str]:
        '''
        Return option aliases
        '''
        return self.value.aliases

    @property
    def index(self) -> int:
        '''
        return option index
        '''
        return self.value.index

    @property
    def default(self) -> Any:
        '''
        Return default option value
        '''
        return self.value.default

    @property
    def descr(self) -> str:
        '''
        Return option description (help)
        '''
        return self.value.descr

    @property
    def action(self) -> str:
        '''
        Return the option action upon specification
        '''
        return self.value.action

    @property
    def suppress_missing(self) -> bool:
        '''
        Return if the option should be suppressed from the parser when missing
        '''
        return self.value.suppress_missing

    @staticmethod
    def from_string(str_repr: str):
        '''
        Return the enum representation of the string
        '''
        obj = None

        for _ in Option:
            if _ == str_repr or str_repr in _.aliases:
                obj = _
                break

        return obj


#############################################################


class OptionGroup(Enum):
    '''
    Yaam command line options groups
    '''
    EXECUTION_MODE = OptionGroupEntry(
        index=0,
        options=[Option.RUN_STACK, Option.UPDATE_ADDONS, Option.EXPORT],
        mutually_exclusive=True
    )

    GLOBAL = OptionGroupEntry(
        index=1,
        options=[
            Option.DEBUG, Option.GAME, Option.FORCE_ACTION, Option.EDIT,
            Option.GITHUB_USER, Option.GITHUB_API_TOKEN
        ],
        mutually_exclusive=False
    )

    def __hash__(self) -> int:
        return hash(tuple([self.index, *[hash(_) for _ in self.options]]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Option):
            return self.index == o.index
        else:
            return False

    @property
    def options(self) -> List[Option]:
        '''
        Return options
        '''
        return self.value.options

    @property
    def index(self) -> tuple:
        '''
        return option index
        '''
        return self.value.index

    def is_mutally_exclusive(self) -> bool:
        '''
        Return if the options in the group are mutually exclusive
        '''
        return self.value.mutually_exclusive

    @staticmethod
    def from_string(str_repr: str):
        '''
        Return the enum representation of the string
        '''
        obj = None

        for _ in Option:
            if str_repr == _.name:
                obj = _
                break

        return obj
