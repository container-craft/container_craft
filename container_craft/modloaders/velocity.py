from container_craft.libcore import MINECRAFT_SERVER_JAR

def install_velocity():
    return "# Placeholder: parent_image should handle velocity installer\n"

def generate_dockerfile():
    return "# Placeholder: parent_image should handle velocity installer\n"

VELOCITY_INFO = {
    "1.21.6": "https://fill-data.papermc.io/v1/objects/f82780ce33035ebe3d6ea7981f0e6e8a3e41a64f2080ef5c0f1266fada03cbee/velocity-3.4.0-SNAPSHOT-522.jar",
    # Add more mappings as needed
}

def do_fetch(mc_version):
    url = VELOCITY_INFO.get(mc_version)
    if not url:
        raise ValueError(f"No Velocity URL found for Minecraft version {mc_version}")

    return f"RUN cd /home/mc && wget {url} -O {MINECRAFT_SERVER_JAR}"

def do_install():
    return "RUN echo 'Velocity does not require installation.'"