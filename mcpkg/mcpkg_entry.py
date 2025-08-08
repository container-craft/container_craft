import time

class McPkgEntry:
    def __init__(self, slug, author, file_sha512, mod_version, file):
        # Initialize the class attributes with the provided data
        self.name = slug
        self.author = author
        self.sha = file_sha512
        self.loader = env.get("MC_LOADER")  # Assuming env is available and set
        self.provider = "modrith"  # Fixed provider value (can be dynamic if needed)
        self.source = file["url"]  # URL from the file data
        self.version = mod_version["version_number"]  # Version number from mod_version
        self.file_name = file["filename"]  # File name from the file data
        self.timestamp = int(time.time())  # Current timestamp in seconds
        self.signed_by = f"{env.server}_packagegroup.json.sig"  # Signed by info (from env)
        self.dependencies = mod_version.get("dependencies", [])  # Dependencies from mod_version, default empty list

    def get_entry(self):
        # Return the attributes as a dictionary
        return {
            "name": self.name,
            "author": self.author,
            "sha": self.sha,
            "loader": self.loader,
            "provider": self.provider,
            "source": self.source,
            "version": self.version,
            "file_name": self.file_name,
            "timestamp": self.timestamp,
            "signed_by": self.signed_by,
            "dependencies": self.dependencies
        }
    def to_json(self):
        return json.dumps({
            "name": self.get_name(),
            "author": self.get_author(),
            "sha": self.get_sha(),
            "loader": self.get_loader(),
            "provider": self.get_provider(),
            "source": self.get_source(),
            "version": self.get_version(),
            "file_name": self.get_file_name(),
            "timestamp": self.get_timestamp(),
            "signed_by": self.get_signed_by(),
            "dependencies": self.get_dependencies()
        })
