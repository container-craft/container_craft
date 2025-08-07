from pathlib import Path
from typing import Optional, Dict, List
from docker import from_env as docker_from_env, errors as docker_errors
from container_craft_core.env import ContainerCraftEnv
from container_craft_core.logger import get_logger
from container_craft_core.error_handler import error_handler

logger = get_logger(__name__)


class Docker:
    def __init__(self, env: Optional[ContainerCraftEnv] = None):
        self.env = env or ContainerCraftEnv()
        self.client = docker_from_env()

    def build_image(
        self,
        dockerfile_path: str,
        tag: str,
        build_args: Optional[Dict[str, str]] = None,
        context_dir: Optional[str] = None,
    ) -> bool:
        """
        Build a Docker image using the Docker SDK with args from environment.
        """
        context_path = context_dir or str(self.env.get_path("MC_BUILD_DIR"))
        dockerfile_path = Path(dockerfile_path)

        full_build_args = {**self.env.as_dict()}
        if build_args:
            full_build_args.update(build_args)

        logger.debug(f"Building image: {tag}")
        logger.debug(f"Context dir: {context_path}")
        logger.debug(f"Dockerfile: {dockerfile_path}")
        logger.debug(f"Build args: {full_build_args}")

        try:
            image, logs = self.client.images.build(
                path=context_path,
                dockerfile=str(dockerfile_path),
                tag=tag,
                buildargs=full_build_args,
                rm=True,
                pull=False,
            )
            for chunk in logs:
                if "stream" in chunk:
                    logger.debug(chunk["stream"].strip())
            logger.info(f"Built image '{tag}' successfully")
            return True
        except docker_errors.BuildError as e:
            for line in e.build_log:
                if "stream" in line:
                    logger.error(line["stream"].strip())
            error_handler.handle_error("Docker build failed", e)
            return False
        except docker_errors.APIError as e:
            error_handler.handle_error("Docker API error during build", e)
            return False

    def run_container(
        self,
        image: str,
        name: Optional[str] = None,
        detach: bool = True,
        ports: Optional[Dict[str, str]] = None,
        env: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        command: Optional[str] = None,
    ) -> bool:
        """
        Run a Docker container using the SDK.
        """
        environment = env or self.env.as_dict()

        try:
            container = self.client.containers.run(
                image=image,
                name=name,
                detach=detach,
                ports=ports,
                environment=environment,
                volumes=volumes,
                command=command,
                tty=True,
            )
            logger.info(f"Container '{container.name}' started with ID: {container.id}")
            return True
        except docker_errors.ContainerError as e:
            error_handler.handle_error(f"Container '{name or image}' exited with error", e)
            return False
        except docker_errors.APIError as e:
            error_handler.handle_error(f"Docker API error while running container '{name or image}'", e)
            return False
