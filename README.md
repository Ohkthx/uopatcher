# Ultima Online Manifest Patcher

This application is used to provide cross-platform support to shards/servers that utilize a **Manifest**-based patching technique. You will need to know the **root url**  and **port** required to access that data. 


## Configuration

Configuration file is located in the root directory, named **config.ini**, and generated after the first launch of the application. You will need to change the defaults for the patching to work. Defaults are below.
```ini
[DEFAULT]
debug = False
skip_prompt = False
local_root = temp
remote_root = patch.example.com
remote_port = 8080
```

- **debug** - Shows additional output used for troubleshooting.
- **skip_prompt** - Skips prompting the user about the installation directory, useful for automation.
- **local_root** - Root directory to save the patch files in.
- **remote_root** - Root URL/URI to obtain the Manifest, Hashes, and additional patch files.
- **remote_port** - Port used to access the resources. 

## Installation and Running

**Installation**: Use the command below to automatically install the dependencies and set up a virtual environment to run the application in.
```bash
make install
```
**Running**: Use the command below to start the patcher, remember that upon first time execution, it will generate the **config.ini** file that must be updated with the correct remote resources to pull patches.
```bash
make start
```
