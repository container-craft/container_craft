import argparse
from pathlib import Path
from container_craft.libcore import ssh_agent, logger, error_handler
from container_craft.layers import LayerManager
from container_craft.context_manager import load_context

def checkout(args):
    """Checkout layers locally with caching and conditional update."""
    if args.ssh_key:
        ssh_agent.add_key(args.ssh_key)

    layer_manager = LayerManager(args.layers_dir, ssh_key=args.ssh_key)

    from git import Repo

    for name, layer in load_context([]).get("layers", {}).items():
        repo_path = layer_manager.layers_dir / (layer.get('path') or name)
        if repo_path.exists():
            repo = Repo(repo_path)
            if args.force_checkout:
                import shutil
                shutil.rmtree(repo_path)
                layer_manager.clone_or_update_layer(name, layer.get('url'), layer.get('branch'), layer.get('commit'), layer.get('path'))
                continue
            if not args.update and repo.is_dirty(untracked_files=True):
                logger.info(f"Skipping update for dirty layer {name} at {repo_path}")
                continue
            if args.update:
                # Force update branch
                repo.git.checkout(layer.get('branch'))
                repo.remotes.origin.pull()
                continue
        else:
            layer_manager.clone_or_update_layer(name, layer.get('url'), layer.get('branch'), layer.get('commit'), layer.get('path'))

    logger.info("Checkout complete.")

