# Container Craft: Mod Management Design

## Introduction

We like to treat mods like packages in a Linux distribution.
Inspired by package managers like `ipk`/`opkg`  

Note: The server name `my_server_name` is used consistently in the examples below. If changed, the group names and paths must match accordingly.

## Server Mod Configuration Format

```yaml
default:
  env: 
    MC_VERSION: 1.21.7
servers:
  my_server_name:                   ## The name used throughout the config. Referenced below as 'my_server_name'.
    mcpkg:                          ## Declare that we are using mcpkg save schema as └── mcpkg/schema.py 
      local:                        ## Defines the package group name, similar to Yocto's packagegroups. Used in the env below.
        - mods/mylocal_mod.jar      ## Relative to MC_WORK_DIR. Local JARs go here.
      modrith:
        - fabric-api:               ## This "slug" must match upstream in the Modrinth repository.
            version: "snapshotversion"  ## Optional override; defaults to MC_VERSION. See docs/env.md. 
      curse_forge:                  ## Requires user-supplied API key. See docs/env.md.  
        - another_mod               ## Example usage of CurseForge. Not referenced below.
      hangar:                       ## No official API. Use full plugin URLs directly. Not referenced below.
        - https://hangarcdn.papermc.io/plugins/ViaVersion/ViaVersion/versions/5.4.2/PAPER/ViaVersion-5.4.2.jar
```

## ENV


## Workflow

**Alpha and not fully implemented (inspired by `opkg`; licensing still under consideration)**

### 1) Cache Lookup
If `${MC_REPO_DIR}/modname` exists, skip to step 4.

### 2) Download + Register
If missing:
- Download the mod
- Add an entry to `${MC_REPO_DIR}/my_server_name_packagegroup.json`

Each entry describes the mod as a structured record:

- **`name`**: The canonical name of the mod/plugin
- **`sha`**: SHA-256 checksum of the downloaded file
- **`loader`**: Loader type (fabric, forge, etc.)
- **`provider`**: One of the supported systems: `local`, `modrith`, `curse_forge`, or `hangar`
- **`source`**: Source URL or file path
- **`version`**: Version (explicit or inferred)
- **`file_name`**: The stored file name on disk
- **`timestamp`**: Epoch time when downloaded
- **`signed_by`**: GPG signature file name of the packagegroup JSON

Example:
```json
{
    "name": "fabric-api", 
    "sha": "6e1d4547...",
    "loader": "fabric",
    "provider": "modrith",
    "source": "https://cdn.modrinth.com/data/...",
    "version": "0.128.2+1.21.6",
    "file_name": "fabric-api-0.128.2+1.21.6.jar",
    "timestamp": 1754518952,
    "signed_by": "my_server_name_packagegroup.json.sig"
}
```

> **Note**: Signing is applied to the `my_server_name_packagegroup.json` file, not the individual mods. This mirrors Debian and IPK practices where the repository metadata is GPG signed.

### 3) Repo Construction
After collecting mods:
- Compress them into `my_server_name.zip`
- Create `my_server_name.mcpkg` with:
```
127.0.0.1:8080/fabric/1.21.7/my_server_name/my_server_name_packagegroup.json
```

Resulting files:
- `my_server_name.zip`
- `my_server_name_packagegroup.json`
- `my_server_name_packagegroup.json.sig`
- `my_server_name.mcpkg`
- Mod/plugin jars

### 4) Docker COPY
In Dockerfile (via Jinja2):
- Copy `my_server_name.zip`
- Extract to `${MC_BASE}/[mods|plugins]` depending on loader
- Remove zip

### 5) COPY `.mcpkg`
Copy `my_server_name.mcpkg` to `/etc/` inside the container

### 6) Future: Signing
Sign `my_server_name_packagegroup.json` with GPG to produce `.sig`

### 7) Future mcpkg

**Future Tool Name**: `mcpkg` 

will serve as the mod manager backend.

Build Python CLI(mcpkg) to:
- list
- install
- remove
- update
- upgrade
