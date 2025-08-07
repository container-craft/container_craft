## Container Craft

Container Craft is a declarative framework for building and managing modular Minecraft server networks using Docker.
The user defines server behavior using layered YAML/JSON files, combining base servers, shared mods, and per-world configs.
It is inspired by systems like Yocto, Kas and OPKG with layered reproducibility and caching as a core principle.

Each server gets a fully deterministic Docker image and isolated runtime.

## Upstream "Meta-Layers"

Each upstream layer is a self-contained set of files used to define and build a Minecraft server base image. These layers are version-controlled and reusable across different server setups.

Here is an example structure for an upstream meta-layer like mc_jimmers_fabric_server/:


mc_jimmers_fabric_server/
├── config/
│   ├── server.properties               # Default Minecraft server properties
├── datapacks/
│   └── datapacks.txt                   # List or index of datapacks to install (optional)
├── entrypoint.sh                       # Entrypoint script that runs inside the container This is not needed most the time
├── mc_jimmers_fabric_server.yml        # 

For general use [see this document](docs/container_craft.md)
For general use with ***mcpkg*** see [see this document](docs/mcpkg.md)


## Container Craft Core

Config handling. 
Before writing or editing Python code, one should review this file carefully to understand how:
* the main context (context.py) is loaded and parsed,
* the JSON Schema (context_schema.py) validates structure and types,
* layers, servers, mods, and networks are structured,
* default behavior is applied across the config.


## Dependencies. 
 
These must be used, not replaced. Do not substitute. We will be porting all this to C  or C++ in the near future once the project is stable.


```
|--------------------------------------------------------------------------|
| Package       | Purpose                                                 |
|---------------|---------------------------------------------------------|
| pyyaml        | Parse the main `.yaml` and any included YAML            |
| jsonschema    | Validate config schema structure                        |
| gitpython     | Clone and track Git-based mod/image layers              |
| httpx         | Call Modrinth and CurseForge and other APIs             |
| docker        | Build images, run containers, attach volumes/networks   |
| kconfiglib    | Render the optional TUI config menu                     |
| jinja2        | Render of Dockerfile and other bits                     |
|-------------------------------------------------------------------------|
```

## Container Craft



