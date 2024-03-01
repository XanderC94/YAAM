# Yet Another Addon Manager (YAAM)

<a href="https://scan.coverity.com/projects/xanderc94-yaam">
  <img alt="Coverity Scan Build Status"
       src="https://scan.coverity.com/projects/24847/badge.svg"/>
</a>

## Premise

Since this whole little project of mine was born to foremost play with Python and also to ease my laziness managing Guild Wars 2 addons, the software currently supports only such game and its supported addon "types": Dynamic-link Libraries (.dll), executables (.exe), installers (.msi) and plain data files of any kind.

Depepending on my free time, I would like to add support for other games and kind of addons "types" (ex.: scripts).

Moreover, YAAM is currently distributed as a CLI software; a GUI version is still far in the horizon.

## About

YAAM wants to be a generic and configurable addon manager for games which aims to automate *most* of the routines of installation, update, enable and disable of any kind of addon (.dll, .exe, ...). In order to maintain genericity and configurability, some addons might require the user follow-up during either their installation or update phase.  

## Features

The main features currently supported by YAAM are:

* Manage command-line arguments for the game (for example: [Guild Wars 2 CLI](https://wiki.guildwars2.com/wiki/Command_line_arguments))
* Addon installation for any supported type which expose a "latest release" URI
* Addon update for any supported type which expose a "latest release" URI
* Addon enable and disable for any supported addon type
* Automated execution of executables and installers
* Customizable addon extraction from zipped archives
* Addon renaming (only upon installation / updating)
* Local addon versioning tracking
* Optimized remote addon versioning checking
* All operations support the following data types .exe, .dll, .msi and plain data file
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
   -r, --run, --run-stack,--run_stack
                        Only run the game without updating the addons
  -u, --update, --update-addons, --update_addons
                        Only update addons without running the game
  -x, --export          Export YAAM settings # Unsupported / WIP
  --force               Force any specified action
  -e, --edit            Run YAAM edit repl (DEPRECATED)
  --github-user GITHUB_USER, --github_-_user GITHUB_USER
                        Set github user
  --github-api-token GITHUB_API_TOKEN, --github_api_token GITHUB_API_TOKEN
                        Set github API token
```

All these parameters can be defaulted to a physical .INI file under %localappdata%/yaam/yaam.ini.

```[INI]
[yaam]
github_user=User123
github_api_token=ghp_000000000000000000000000000000000000
```

If a parameter is specified from command-line, it will override the configuration one.

Since many GW2 addons are distributed through GitHub, YAAM supports addons update from GitHub API [https://api.github.com/repos/project/repository/releases/latest](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting). Since anonymous users only gets 60 API calls per hour, I added the possibility to specify each its own access token which further increase such number to 5000 API call per hour (requires a GitHub account).

## Game configuration

There are five configuration files:

### Init

Path: %localappdata%/yaam/res/\<game-name>/init.json

This configuration file stores the game initialization data such as the name and the path to the game "configuration" file. YAAM expects that the file stores the game root directory and the game executable name.

```[JSON]
{
    "name": "Game Name",
    "config_path": "path/to/the/game/configuration/file.bar"
}
```

If this information aren't available or the game isn't supported out-of-the-box, you can write your own initialization file with the necessary informations. You can also reflect on the init.json file itself.

```[JSON]
{
    "root": "path/to/the/game/root/directory",
    "exe": "game.exe",
    "native_binding": "dx9"
}
```

The currently looked-up informations are:

* the game root directory path
* the game executable name
* the game native (default) binding type

### Arguments

Path: %localappdata%/yaam/res/\<game-name>/arguments.json

This configuration file should store all the supported CLI arguments for a game. **All GW2 arguments are already deployed with the software** but can modified however the user desires.

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

### Addons

Path: %localappdata%/yaam/res/\<game-name>/addons.json

This configuration file stores a list of all the addons along their update uri, a description and other useful metadata. A list of GW2 addons is already provided with the software.

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

### Settings

Path: %localappdata%/yaam/res/\<game-name>/settings.json

This configuration file stores the current state of both chosen arguments and addons. For addons are recorded name and value (if any) while addons specify the path of deployment, activation, updating and binding type (exe, dx9, dx11, agnostic, ...)

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
                "path": "path/to/addon/deployment/space/megan123.exe",
                "enabled": true | false,
                "update": true | false
            }
        ],
        "dx11": [
            {
                "name": "bob",
                "path": "path/to/addon/deployment/space/bob456.dll",
                "enabled": true | false,
                "update": true | false
            }
        ],
        "file": [
            {
                "name": "zoe",
                "path": "path/to/addon/deployment/space/bob789.txt",
                "enabled": true,
                "update": false
            }
        ],
        "any": [
            {
                "name": "alice",
                "path": "path/to/addon/deploament/space/alice0.dll",
                "enabled": true | false,
                "update": true | false
            }
        ]
}
```

Among the binding types (exe, dx9, dx10, dx11, dx12, vulkan, agnostic), "exe"s" and "agnostic" are always loaded despite the specified graphic API bindings (dx or vulkan) from the game.

The binding types "dx9", "dx10", "dx11", "dx12" and "vulkan" are mutually exclusive.

#### Notes

The "run-time" binding type can be specified as an CLI argument of the game settings.
For example, a command-line argument like

```[JSON]
{
    "arguments": [
        {
            "name": "d3d11"
        }
    ]
}
```

will set and load the DX11 bindings among the mutually exclusive ones.

### Namings

Path: %localappdata%/yaam/res/\<game-name>/namings.json

This "configuration" file stores custom deployment settings for each addons. Currently, only renaming, squashing (path flattening) and unsquashing (path inflating) are supported and should be done programmatically.

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

### How do I deploy a game?

If the game is supported out-of-the-box then just download the latest version of YAAM, unpack it in a folder of your choice and run it from Windows Powershell or Command.

On the first deployment YAAM will create its own execution environment under the %LOCALAPPDATA% folder and copy all the (default) game settings, addons, etc embedded into the distribution.

At the start of the YAAM executable it will list the available games and ask the user which game it desire to run.

That's it. That all.

### How do I user YAAM with my own game?

Create one each of the configuration file specified above inside the YAAM game folder.

### Why explicitly specify the graphics API bindings for each addon?

Good question, it is both a fail safe and also permits to store and keep multiple DirectX configurations while loading only the chosen one (the other will be disabled). It became necessary when GW2 added support to DX11. The "agnostic" is for all those addons that don't care about such distinction.
