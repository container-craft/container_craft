from container_craft.modloaders import fabric, forge, neoforge, paper, velocity

class ModLoaderManager:
    def __init__(self):
        self.loaders = {
            "fabric": fabric,
            "forge": forge,
            "neoforge": neoforge,
            "paper": paper,
            "velocity": velocity,
        }

    def get_loader(self, loader_name):
        return self.loaders.get(loader_name)

    def fetch_modloader(self, loader_name, mc_version):
        loader = self.get_loader(loader_name)
        if not loader:
            raise ValueError(f"Modloader {loader_name} not found")
        return loader.do_fetch(mc_version)

    def install_modloader(self, loader_name):
        loader = self.get_loader(loader_name)
        if not loader:
            raise ValueError(f"Modloader {loader_name} not found")
        return loader.do_install()
