## Build and Runtime Environments

These environment variables are exported into the build process for all commands. They can be overridden in three ways:

1. By setting environment variables (`env`)
2. By specifying values in the `defaults:` node of the config file (`YAML` or `JSON`)
3. By passing explicit CLI arguments, e.g.

```bash
   container_craft build --ssh-key=/some/path/id_rsa myconfig.yml
```

---

## Environment Variables

---

### `MC_VERSION`

The Minecraft version to build against.
Default: the branch name currently checked out (e.g., `1.21.2`).
Note: If no valid parent is available for this type of server, it may fail. Stick with branch-aligned versions when possible.

---

### `MC_MEMORY`

The amount of memory allocated to the server.
Example: `4G`

---

### `MC_BASE`

The path where Minecraft is or will be installed.
Default: `/home/mc`

---

### `MC_PORT`

The exposed port for a single Minecraft container.
Default: `25565`
Note: In most cases, port configuration is handled by the `network` node of the server configuration.

---

### `MC_WORK_DIR`

The working directory for Container Craft.
Default: the current working directory (`$PWD`).
This directory must exist if set.

Can also be specified in the config file under:

```yaml
defaults:
  work_dir: /path/to/dir
```

---

### `MC_CONFIG`

The path to the default YAML or JSON config file when no configs are passed via the CLI.
Used by the TUI (e.g., `menuconfig`) to persist selections.

Default: `${MC_WORK_DIR}/.config.yml`
Useful for embedding a default build type inside a repository.

Note: This can be overridden by passing in a config file via CLI.

---

### `MC_LOADER`
Should be an enum type (string). Acceptable values:

- `vanilla`
- `fabric`
- `forge`
- `neoforge`
- `paper`
- `velocity`

---

### `MC_BUILD_DIR`

Where built files are staged.
Default: `${MC_WORK_DIR}/build`
This directory must exist if set.

Can also be specified in the config file:

```yaml
defaults:
  build_dir: /path/to/build
```

---

### `MC_DOWNLOADS_DIR`

Where downloads (e.g., mods, installers) are cached.
Default: `${MC_WORK_DIR}/downloads`

---

### `MC_CACHE_DIR`

Another location for general build cache artifacts.
Default: `${MC_WORK_DIR}/cache`

---

### `MC_LAYERS_DIR`

The directory where additional layers (Git repos) are cloned.
Default: `${MC_BUILD_DIR}/layers`

---

### `SSH_PRIVATE_KEY`

The path to a private key file used in CI environments.
It will be added to a temporary `ssh-agent` inside Container Craft.

Note:

* The key **must not** be password-protected.
* This is useful for CI builds or local dev where a headless environment is used.
* On developer machines with a running `ssh-agent`, this is typically not needed.

---

### `VELOCITY_FILES`

Comma-separated list of:

* The `forward.secrets` file
* All attached Velocity server configuration files

Used for Velocity proxy integration. Example:

```bash
VELOCITY_FILES=forward.secrets,proxy1.toml,proxy2.toml
```


### `MC_REPO_DIR`
Points to your local cached repository.

Default:
```
${MC_CACHE_DIR}/${MC_LOADER}/${MC_VERSION}/my_server_name
```

This directory should be unique per version and loader to avoid cross-version conflicts.

Suggested values: `/srv/minecraft`, `/var/www`, etc.

### `MC_REPO_URL`
Defines the URL used inside Docker to access the mod repository.

Default:
```
${REPO_URL}/${MC_LOADER}/${MC_VERSION}/my_server_name
```

Example:
```
MC_REPO_URL=127.0.0.1:8080/fabric/1.21.7/my_server_name
```

