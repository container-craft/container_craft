import os
from container_craft.libcore import MINECRAFT_SERVER_JAR
from container_craft.modloaders.fabric import FABRIC_INFO

FORGE_INFO = {
    "1.21.6": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.21.6-56.0.9/forge-1.21.6-56.0.9-installer.jar",
    # Add more mappings as needed
}

def do_fetch():
    version = os.getenv("MINECRAFT_VERSION", "1.21.6")
    url = FORGE_INFO.get(version)
    if not url:
        raise ValueError(f"No Forge URL found for Minecraft version {version}")

    return f"RUN wget {url} -O /home/mc/server.jar"

def do_install():
    return f"RUN java -jar /home/mc/server.jar --installServer"