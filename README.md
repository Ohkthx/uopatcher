{ "version": [1, 0, 4] }

# Ultima Online Manifest Patcher

This application is used to provide cross-platform support to shards/servers that utilize a **Manifest**-based patching technique. The original patching concept is accredited to [Voxpire](https://github.com/Voxpire) with his [ServUO/IPL](https://www.servuo.com/archive/all-in-one-installer-patcher-launcher-ipl.1724/) used for installing, patching, and launching custom Ultima Online shards clients. To get this project up and running, you will need to know the **root url** and **port** required to access that data. 


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
verbose = False
local_root = temp
remote_root = patch.example.com
remote_port = 8080
```

- **debug** - Shows additional output used for troubleshooting.
- **skip_prompt** - Skips prompting the user about the installation directory, useful for automation.
- **verbose** - Shows additional text including progress on downloading a file.
- **local_root** - Root directory to save the patch files in.
- **remote_root** - Root URL/URI to obtain the Manifest, Hashes, and additional patch files.
- **remote_port** - Port used to access the resources. 

## Running

Use the command below to start the patcher, remember that upon first time execution, it will generate the **config.ini** file that must be updated with the correct remote resources to pull patches.
```bash
python3 uopatcher/core.py

# OR, this is optional way to start it.
make start
```
