# Yet Another Addon Manager (YAAM)

## Premise

Since this whole little project of mine was born to foremost play with Python and also to ease my laziness managing Guild Wars 2 addons, the software currently supports only such game and its supported addon "type" (.dll), plus executables and installers. Depepending on my free time, I would like to add support for other games and kind of addons "types" (ex.: scripts).
Moreover is currently distributed as a CLI software, a GUI version is still far in the horizon.

## About

YAAM wants to be a generic and configurable addon manager for games which aims to automate *most* of the routines of installation, update, enabe and disable of any kind of addon (.dll, .exe, ...). In order to maintain genericity and configurability, some addons might require the user follow-up during either their installation or update phase.  

## Features

The main features currently supported by YAAM are:

* Manage command-line arguments for the game (for example: [Guild Wars 2 CLI](https://wiki.guildwars2.com/wiki/Command_line_arguments))
* Addon installation for any supported type (currently .dll and .exe) which expose a "latest release" URI
* Addon update for any supported type (currently .dll and .exe) which expose a "latest release" URI
* Addon enable and disable for any supported type (currently .dll and .exe)
* Customizable addon extraction from zipped archives
* Addon renaming (only upon installation / updating)
* Local addon versioning tracking
* Optimized remote addon versioning checking
* Support GitHub API access tokens
* Support GitHub API latest release links
* User follow-up for those addons which are deployed through installers or have multiple download artifacts

## YAAM Configuration

Since YAAM is a CLI software it has some command-line arguments:

```[CLI]
usage: YAAM [-h] [--run_stack | -u | --export] [--force] [-e] [--github_user GITHUB_USER] [--github-api-token GITHUB_API_TOKEN]

Yet Another Addon Manager

optional arguments:
  -h, --help            show this help message and exit
  --run_stack, -r, --run-stack, --run
                        Only run the game without updating the addons
  -u, --update, --update-addons, --update_addons
                        Only update addons without running the game
  --export, -x          Export YAAM settings # Unsupported / WIP
  --force               Force any specified action
  -e, --edit            Run YAAM edit repl
  --github_user GITHUB_USER, --github-user GITHUB_USER
                        Set github user
  --github-api-token GITHUB_API_TOKEN, --github_api_token GITHUB_API_TOKEN
                        Set github API token
```

All these parameters can be defaulted to a physical .INI file under %APPDATA%/yaam/yaam.ini.

```[INI]
[yaam]
github_user=User123
github_api_token=ghp_000000000000000000000000000000000000
```

If a parameter is specified from command-line, it will override the configuration one.

Since many GW2 addons are distributed through GitHub, YAAM supports addons update from GitHub API [https://api.github.com/repos/project/repository/releases/latest](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting). Since anonymous users only gets 60 API calls per hour, I added the possibility to specify each its own access token which further increase such number to 5000 API call per hour (requires a GitHub account).

## Game configuration

There are four configuration files:

* **Arguments** (%appdata%yaam/res/game/arguments.json): this configuration file stores or should store all the supported CLI arguments for a game. **All GW2 arguments are already deployed with the software** but are there so you can tamper with them however you like.

```[JSON]
{
    "name": "foo",
    "values": [],
    "value_type": "ip | numeric | boolean | path | none",
    "description": "Short description of what this arguemnt does",
    "deprecated": true | false,
    "user_defined": true | false
}
```

* **Addons** (%appdata%yaam/res/game/addons.json): this configuration file stores a list of all the addons along their update uri, a description and other useful metadata. A list of GW2 addons is already provided with the software.

```[JSON]
{
    "name": "bob",
    "uri": "https://link/to/bob/latest/release",
    "description": "A short description of what this addon does",
    "contribs": [ "Bob", "Alice", "Megan" ],
    "dependencies": [ "alice" ],
    "is_shader": true | false,
    "is_installer": true | false
}
```

* **Settings** (%appdata%yaam/res/game/settings.json): this configuration file stores the current state of both chosen arguments and addons. For addons are recorded name and value (if any) while addons specify the path of deployment, activation, updating and binding type (exe, dx9, dx11, agnostic, ...)

```[JSON]
{
    "arguments": [
        {
            "name": "foo"
        },
        {
            "name": "bar",
            "value": 42
        }
    ],
    "bindings": {
        "exe": [
            {
                "name": "megan",
                "path": "path/to/addon/deploayment/space/megan123.exe",
                "enabled": true | false,
                "update": true | false
            }
        ],
        "dx11": [
            {
                "name": "bob",
                "path": "path/to/addon/deploayment/space/bob456.dll",
                "enabled": true | false,
                "update": true | false
            }
        ],
        "agnostic": [
            {
                "name": "alice",
                "path": "path/to/addon/deploayment/space/",
                "enabled": true | false,
                "update": true | false
            }
        ]
}
```

Among the binding types (exe, dx9, dx10, dx11, dx12, vulkan, agnostic), "exe"s" and "agnostic" are always loaded despite the specified graphic API bindings (dx or vulkan) from the game.

NOTE: In the case of Guild Wars 2 the command-line argument "-dx11" is checked since it can't be asserted programmatically in any other way (no entry in the XML file either).

* Namings (%appdata%yaam/res/game/namings.json): This "configuration" file stores custom deployment settings for each addons. Currently, only renaming, squashing (path flattening) and unsquashing (path inflating) are supported and should be done programmatically.

```[JSON]
"namings": [      
    {
        "addon": "bob",
        "naming": {
            "bob_dir/bob.config": "bob_dir/bob.config", # does nothing but tracks the name inside the addon metadata
            "bin/bob.dll": "bob_addon.dll", # renaming + squashing
            "bin/bob.pdb": "bob_addon.pdb", # renaming + squashing
        }
    }
]
```

Usually this is necessary for addons distributed in zipped archives and contains multiple files, since YAAM needs to keep track of the names of each addon in order to unambiguously update, enable or disable them. There is no need to track all the files, only the addon file is sufficient (and its dependencies, like pdb files, in order to be renamed accordingly).

Squashing is used to trim the directory tree of the unzipped file and move it in the desired folder hierarchy.

## Q&A

### Why explicitly specify the graphics API bindings for each addon?

Good question, it is both a fail safe and also permits to store and keep multiple DirectX configurations while loading only the chosen one (the other will be disabled). It became necessary when GW2 added support to DX11. The "agnostic" is for all those addons that don't care about such distinction.
