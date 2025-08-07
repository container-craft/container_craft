import argparse
from container_craft.plugins import build, logs, info, shell, console, menu, runner, checkout
import os

def add_ssh_key_argument(parser):
    """Append SSH key argument to the parser."""
    parser.add_argument(
        "--ssh-key",
        type=str,
        help="Path to the SSH private key for building images",
        default=os.getenv("CONTAINER_CRAFTS_SSH_KEY", None)
    )


def add_last_args(parser):
    parser.add_argument(
        "yaml_files",
        nargs="+",
        help="List of YAML configuration files.",
    )


def override_layers_dir_args(parser: argparse.ArgumentParser):
    default_layers_dir = os.getenv(
        "CONTAINER_CRAFTS_LAYERS_DIR",
        "/srv/minecraft/container_craft/layers"  # note: you had a typo "mincraft"
    )

    parser.add_argument(
        "--layers-dir",
        type=str,
        metavar="DIR",
        help=f"Overrides path to layers directory (default: %(default)s)",
        default=default_layers_dir,
        required=False
    )

# Override build directory argument
def override_build_dir_args(parser: argparse.ArgumentParser):
    default_build_dir = os.getenv(
        "CONTAINER_CRAFTS_BUILD_DIR",
        "/srv/minecraft/container_craft/build" 
    )

    parser.add_argument(
        "--build-dir",
        type=str,
        metavar="DIR",
        help=f"Overrides path to build directory (default: %(default)s)",
        default=default_build_dir,
        required=True
    )

def add_image_name_args(parser):
    """Add image name argument to the parser."""
    parser.add_argument(
        "image_name",
        help="Name of the Docker image to run",
        required=True
    )


# Build command
def parse_build(parser):
    """Build docker images."""
    add_ssh_key_argument(parser)
    override_layers_dir_args(parser)
    override_build_dir_args(parser)
    add_last_args(parser)
    parser.set_defaults(func=build.build_all)


def parse_stop:
    add_image_name_args(parser)
    parser.set_defaults(func=runner.run)

def parse_start:
    add_image_name_args(parser)
    parser.set_defaults(func=runner.stop)


# Run command
def parse_exec(parser):
   print("SOON")


# Logs command
def parse_logs(parser):
    """Tail server logs."""
    add_image_name_args(parser)
    parser.set_defaults(func=logs.tail_logs)

# Info command
def parse_info(parser):
    """Show container info."""
    add_image_name_args(parser)
    parser.set_defaults(func=info.show_info)


# Shell command
def parse_shell(parser):
    """Attach to container shell."""
    add_image_name_args(parser)
    parser.set_defaults(func=shell.attach_shell)

# Console command
def parse_console(parser):
    """Access Minecraft console."""
    add_image_name_args(parser)
    parser.set_defaults(func=console.attach)

# Menu command
def parse_menu(parser):
    kconfig_dir = os.path.abspath(os.getenv("CONTAINER_CRAFT_KCONFIG", os.getcwd()))
    kconfig_file = os.path.join(kconfig_dir, "Kconfig")
    parser.add_argument(
        "--kconfig",
        type=str,
        metavar="FILE",
        help=f"Overrides the Kconfig file for the TUI (default: %(default)s)",
        default=kconfig_file,
        required=False
    )
    parser.set_defaults(func=menu.show_menu)


# Checkout command
def parse_checkout(parser):
    """Checkout Other Yaml configurations. from git repositories."""
    add_ssh_key_argument(parser)
    parser.add_argument("--force-checkout", action="store_true", help="Force cleanup and fresh checkout")
    parser.add_argument("--update", action="store_true", help="Force update on branch")
    parser.add_argument("--layers-dir", type=str, help="Path to layers directory", 
                        default=os.getenv("CONTAINER_CRAFTS_LAYERS_DIR", "/srv/minecraft/container_craft/layers"))
    
    # TODO add the subparser for the add and remove commands to alter the layers
    # this will allow the user to add or remove layers from the layers directory
    # code needs to be added to the CheckoutCommand class to handle this
    # sub_parser = parser.add_subparsers(dest="add", required=False)

    ## if the subparser picks up the add or remove commands we run that function else we run the checkout function
    parser.add_last_args(parser)



