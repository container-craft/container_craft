import argparse
from container_craft.context import context
import kconfiglib
from container_craft.libcore import logger, error_handler
from container_craft.plugins import build, runner

def show(args):
    """Display Kconfig-style menu."""
    kconf = kconfiglib.Kconfig(args.kconfig)
    while True:
        kconf.menuconfig()
        choice = input("Enter your choice (build/run/save/exit/help): ")
        if choice == 'build':
            logger.info('Build selected')
            build.build_all(args)
        elif choice == 'run':
            logger.info('Run selected')
            server = input('Enter server name to run: ')
            runner.run(server)
        elif choice == 'save':
            logger.info('Save & Exit selected')
            kconf.write_config()
            break
        elif choice == 'exit':
            logger.info('Exit selected')
            break
        elif choice == 'help':
            logger.info('Help selected')
            print("Help information...")
