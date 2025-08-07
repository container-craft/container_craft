from container_craft.libcore import MINECRAFT_SERVER_JAR

NEOFORGE_INFO = {
    "1.21.6": "https://maven.neoforged.net/releases/net/neoforged/neoforge/21.6.20-beta/neoforge-21.6.20-beta-installer.jar",
    # Add more mappings as needed
}

def do_fetch(mc_version):
    url = NEOFORGE_INFO.get(mc_version)
    if not url:
        raise ValueError(f"No NeoForge URL found for Minecraft version {mc_version}")

    return f"RUN wget {url} -O {MINECRAFT_SERVER_JAR}"

def do_install():
    return f"RUN java -jar {MINECRAFT_SERVER_JAR} --installServer"
