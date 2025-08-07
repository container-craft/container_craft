import os
from container_craft.libcore import MINECRAFT_SERVER_JAR
import logging

logger = logging.getLogger(__name__)

FABRIC_INFO = {
    "1.21.8":{
        "FABRIC_INSTALLER_VERSION": "1.1.0",
        "FABRIC_LOADER_VERSION": "0.16.14",
    },
    "1.21.7": {
        "FABRIC_INSTALLER_VERSION": "1.1.0",
        "FABRIC_LOADER_VERSION": "0.16.14",        
    },
    "1.21.6": {
        "FABRIC_INSTALLER_VERSION": "1.1.0",
        "FABRIC_LOADER_VERSION": "0.16.14",
    },
}   

def do_fetch(mc_version):
    versions = FABRIC_INFO.get(mc_version)
    if not versions:
        raise ValueError(f"No Fabric modloader versions found for Minecraft version {mc_version}")

    fabric_installer_version = versions["FABRIC_INSTALLER_VERSION"]
    fabric_loader_version = versions["FABRIC_LOADER_VERSION"]

    url = f"https://meta.fabricmc.net/v2/versions/loader/{mc_version}/{fabric_loader_version}/{fabric_installer_version}/server/jar"
    logger.debug(f"Fetching server.jar from URL: {url}")

    return f"RUN wget {url} -O /home/mc/server.jar"

def do_install():

    versions = FABRIC_INFO.get(os.getenv("MINECRAFT_VERSION", "1.21.6"))
    if not versions:
        raise ValueError(f"No Fabric modloader versions found for Minecraft version {os.getenv('MINECRAFT_VERSION', '1.21.6')}")

    fabric_loader_version = versions["FABRIC_LOADER_VERSION"]
    mc_base = os.getenv("MINECRAFT_BASE", "/home/mc")
    mc_version = os.getenv("MINECRAFT_VERSION", "1.21.6")
    
    return f"RUN cd {mc_base} && java -jar /home/mc/server.jar server -mcversion {mc_version} -loader {fabric_loader_version} -downloadMinecraft"