from container_craft.libcore import MINECRAFT_SERVER_JAR

PAPER_INFO = {
    "1.21.6": "https://fill-data.papermc.io/v1/objects/35e2dfa66b3491b9d2f0bb033679fa5aca1e1fdf097e7a06a80ce8afeda5c214/paper-1.21.6-48.jar",
    # Add more mappings as needed
}

def do_fetch(mc_version):
    url = PAPER_INFO.get(mc_version)
    if not url:
        raise ValueError(f"No Paper URL found for Minecraft version {mc_version}")

    return f"RUN cd /home/mc && wget {url} -O {MINECRAFT_SERVER_JAR}"

def do_install():
    return f"RUN java -jar {MINECRAFT_SERVER_JAR} --initSettings"

