import subprocess
import os
from container_craft_core.env import ContainerCraftEnv
from container_craft_core.error_handling import error_handler
from container_craft_core.logger import get_logger

logger = get_logger("ssh_agent")

class SSHAgent:
    def __init__(self, env: ContainerCraftEnv):
        self.env = env
        self.agent_process = None
        self.ssh_auth_sock = self.env.get("SSH_AUTH_SOCK")
        self.ssh_agent_pid = self.env.get("SSH_AGENT_PID")
        self.ssh_askpass = self.env.get("SSH_ASKPASS")

    def start(self):
        if self.ssh_auth_sock and self.ssh_agent_pid:
            logger.debug("SSH agent already running via env — skipping start")
            return

        logger.info("Starting new ssh-agent process...")
        result = subprocess.run(['ssh-agent', '-s'], capture_output=True, text=True)
        if result.returncode != 0:
            error_handler.handle_error('Failed to start ssh-agent')

        for line in result.stdout.splitlines():
            if line.startswith('SSH_AUTH_SOCK') or line.startswith('SSH_AGENT_PID'):
                key, value = line.split('=', 1)
                value = value.rstrip(';')
                os.environ[key] = value
                logger.debug(f"Exported {key}={value}")

        self.agent_process = True

    def add_key(self, key_path: str):
        self.start()

        logger.debug(f"Adding SSH key: {key_path}")
        env = os.environ.copy()
        if self.ssh_askpass:
            env["SSH_ASKPASS"] = self.ssh_askpass
            env["DISPLAY"] = ":0"  # required by some askpass implementations

        result = subprocess.run(['ssh-add', key_path], capture_output=True, text=True, env=env)
        if result.returncode != 0:
            error_handler.handle_error(f'Failed to add ssh key {key_path}', result.stderr)
        logger.info(f"SSH key added: {key_path}")

    def stop(self):
        if self.agent_process:
            logger.info("Stopping ssh-agent")
            subprocess.run(['ssh-agent', '-k'])
            self.agent_process = None


# Global instance will be passed the default env at runtime if needed
ssh_agent = None
