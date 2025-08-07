#!/bin/bash
set -e

required_env_vars=(
  MINCRAFT_SERVER_NAME
  MINECRAFT_MEMORY
  MINECRAFT_SERVER_JAR
)

for var in "${required_env_vars[@]}"; do
  if [[ -z "${!var}" ]]; then
    echo "[ERROR] Missing required environment variable: $var"
    exit 1
  fi
done

copy_dir_if_exists() {
  local src="$1"
  local dst="$2"
  if [ -d "$src" ]; then
    mkdir -p "$dst"
    cp -r "$src"/* "$dst/" 2>/dev/null || true
  fi
}

symlink_if_exists() {
  local target="$1"
  local link_name="$2"
  if [ -e "$target" ]; then
    ln -sf "$target" "$link_name"
  fi
}


if [ ! -d /home/mc/world ]; then
  echo "[ERROR] You need to mount the world directory at /home/mc/world"
  exit 1
fi


copy_dir_if_exists "/home/mc/datapacks" "/home/mc/world/datapacks"
copy_dir_if_exists "/home/mc/extra-datapacks" "/home/mc/world/datapacks"
copy_dir_if_exists "/home/mc/extra-config" "/home/mc/config"
copy_dir_if_exists "/home/mc/extra-mods" "/home/mc/mods"

if [ -d /home/mc/live ]; then
  echo "[INFO] Linking volatile server files from /home/mc/live"

  for file in server.properties ops.json whitelist.json banned_players.json banned_ips.json usercache.json; do
    symlink_if_exists "/home/mc/live/$file" "/home/mc/$file"
  done

  symlink_if_exists "/home/mc/live/logs" "/home/mc/logs"
fi


JAVA_ARGS=(
  "-Xmx${MINECRAFT_MEMORY}"
  "-Xms${MINECRAFT_MEMORY}"
)

# Aikar flags (optional)
if [[ "${MINECRAFT_TUNING}" == "aikar" ]]; then
  JAVA_ARGS+=(
    "-XX:+UseG1GC"
    "-XX:+ParallelRefProcEnabled"
    "-XX:MaxGCPauseMillis=200"
    "-XX:+UnlockExperimentalVMOptions"
    "-XX:+DisableExplicitGC"
    "-XX:+AlwaysPreTouch"
    "-XX:G1NewSizePercent=30"
    "-XX:G1MaxNewSizePercent=40"
    "-XX:G1HeapRegionSize=8M"
    "-XX:G1ReservePercent=20"
    "-XX:G1HeapWastePercent=5"
    "-XX:G1MixedGCCountTarget=4"
    "-XX:InitiatingHeapOccupancyPercent=15"
    "-XX:G1MixedGCLiveThresholdPercent=90"
    "-XX:G1RSetUpdatingPauseTimePercent=5"
    "-XX:SurvivorRatio=32"
    "-XX:+PerfDisableSharedMem"
  )
fi

if [[ -n "${MINECRAFT_JAVA_OPTS}" ]]; then
  JAVA_ARGS+=(${MINECRAFT_JAVA_OPTS})
fi

taskset_cmd=""
if [[ -n "${MINECRAFT_CORES}" ]]; then
  echo "[INFO] Binding Minecraft server to cores: ${MINECRAFT_CORES}"
  taskset_cmd="taskset -c ${MINECRAFT_CORES}"
fi

if [[ -n "${MINECRAFT_PRIORITY}" ]]; then
  echo "[INFO] Setting process priority to ${MINECRAFT_PRIORITY}"
  renice -n ${MINECRAFT_PRIORITY} -p $$
elif [[ -n "${MINECRAFT_NICE}" ]]; then
  echo "[INFO] Setting process nice level to ${MINECRAFT_NICE}"
  exec nice -n ${MINECRAFT_NICE}
fi


if ! tmux has-session -t mc 2>/dev/null; then
  echo "[INFO] Starting Minecraft server in tmux..."
  ${taskset_cmd} tmux new-session -d -s mc \
    "java ${JAVA_ARGS[*]} -Dfml.queryResult=confirm -jar ${MINECRAFT_SERVER_JAR} nogui"
else
  echo "[INFO] Minecraft server already running."
fi

tail -f /dev/null
