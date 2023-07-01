{ "version": [1, 0, 10] }

<p align="center">
    <a href="https://patreon.com/ohkthx" title="Donate to this project using Patreon">
        <img src="https://img.shields.io/badge/patreon-donate-red.svg?style=for-the-badge&color=f38ba8&label=PATREON&logo=patreon&logoColor=f38ba8&labelColor=11111b"
            alt="Patreon donate button"></a>
    <a href="https://ko-fi.com/G2G0J79MY" title="Donate to this project using Ko-fi">
        <img src="https://img.shields.io/badge/kofi-donate-ffffff.svg?style=for-the-badge&color=fab387&label=KOFI&logo=kofi&logoColor=fab387&labelColor=11111b"
            alt="Buy me a coffee! Ko-fi"></a>
<br>
   <a href="https://github.com/ohkthx/uopatcher" title="Required Python Version.">
        <img src="https://img.shields.io/badge/python-3.9.1+-11111b.svg?style=for-the-badge&color=f9e2af&label=PYTHON&logo=python&logoColor=f9e2af&labelColor=11111b"
            alt="Required Python Version."></a>
    <a href="https://github.com/ohkthx/uopatcher" title="Size of the repo!">
        <img src="https://img.shields.io/github/repo-size/ohkthx/uopatcher?style=for-the-badge&color=cba6f7&label=SIZE&logo=codesandbox&logoColor=cba6f7&labelColor=11111b"
            alt="No data."></a>
<br>
   <a href="https://discord.gg/HP3fGNtzfs" title="Connect to the community!">
        <img src="https://img.shields.io/badge/discord-accept%20invite-11111b.svg?style=for-the-badge&color=89B4FA&label=DISCORD&logo=discord&logoColor=89b4fa&labelColor=11111b"
            alt="Discord connect button."></a>
</p>

# Ultima Online Manifest Patcher

This application is used to provide cross-platform support to shards/servers that utilize a **Manifest**-based patching technique. The original patching concept is accredited to [Voxpire](https://github.com/Voxpire) with his [ServUO/IPL](https://www.servuo.com/archive/all-in-one-installer-patcher-launcher-ipl.1724/) used for installing, patching, and launching custom Ultima Online shards clients. To get this project up and running, you will need to know the **root url** and **port** required to access that data. 

<ins>Feel free to join the **Ultima Online: Linux and MacOS** community by clicking **ACCEPT INVITE** button above.</ins>

If you are interested in an open-sourced **cross-platform (x) installer, patcher, and launcher (IPL)**... then check out my other project @[Ohkthx/xIPL](https://github.com/Ohkthx/xIPL) that utilizes this and implements similar functionality as Voxpire's IPL mentioned above. The **xIPL** extends this patcher further with the other elements an **IPL** must contain beyond just patching.


### Requirements

Current requirements are at least **Python Version 3.9.1**, however with slight tweaking by removing the typing/type safety can make it on earlier Python3 versions. All external package requirements have been removed to allow for easier installation. You can check your python version with the following commands:
```bash
# One of these should work.
python --version
python3 --version
```

## Configuration

Configuration file is located in the root directory, named **config.ini**, and generated after the first launch of the application. You will need to change the defaults for the patching to work. Defaults are below.
```ini
[DEFAULT]
debug = False
skip_prompt = False
verbose = True
local_root = client
remote_root = patch.example.com
remote_port = 8080
```

- **debug** - Shows additional output used for troubleshooting.
- **skip_prompt** - Skips prompting the user about the installation directory, useful for automation.
- **verbose** - Shows additional text including progress on downloading a file.
- **local_root** - Root directory to save the patch files in.
- **remote_root** - Root URL/URI to obtain the Manifest, Hashes, and additional patch files.
- **remote_port** - Port used to access the resources. 

## Arguments / Flags

These are optional arguments that can be passed to `core.py` at start to modify the application at run-time. These **OVERRIDE** the configuration file in the even two options are the same.
```
usage: core.py [-h] [--has-update] [--config CONFIG] [--version] [--verbose]

Install and Patch UO.

optional arguments:
  -h, --help       show this help message and exit
  --has-update     Checks if an update is available or not.
  --config CONFIG  Pass the 'config.ini' to use.
  --version        Returns the version of the script.
  --verbose        Overrides VERBOSE in config.ini.
```

## Running

Use the command below to start the patcher, remember that upon first time execution, it will generate the **config.ini** file that must be updated with the correct remote resources to pull patches.
```bash
python3 uopatcher/core.py

# OR, this is optional way to start it.
make start
```

