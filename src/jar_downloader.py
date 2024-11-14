import os
import requests


VERSION_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"

class JarDownloader:
    def __init__(self, ):
        self.manifest_cache = None



    def get_version_manifest(self, force_refresh=False):
        """Fetch and cache the version manifest"""
        if force_refresh or self.manifest_cache is None:
            response = requests.get(VERSION_MANIFEST_URL)
            response.raise_for_status()
            self.manifest_cache = response.json()
        
        return self.manifest_cache



    def get_server_download_url(self, mc_version):
        """Get the server download URL for a specific version"""
        manifest = self.get_version_manifest()
        
        version_info = next(
            (v for v in manifest["versions"] if v["id"] == mc_version),
            None
        )
        if not version_info:
            raise ValueError(f"Version {mc_version} not found in manifest")
        
        version_meta = requests.get(version_info["url"]).json()
        
        if "server" in version_meta["downloads"]:
            return {
                "url": version_meta["downloads"]["server"]["url"],
                "sha1": version_meta["downloads"]["server"]["sha1"]
            }
        raise ValueError(f"No server download found for version {mc_version}")



    def download_if_missing(self, mc_version, download_dir, redownload=False) -> str:
        """Downloads jar to specified dir."""
        jar_path = os.path.join(download_dir, f"server-{mc_version}.jar")

        if os.path.exists(jar_path) and redownload:
            os.remove(jar_path)
        
        if not os.path.exists(jar_path):
            print(f"Downloading server JAR for Minecraft {mc_version}...")
            download_info = self.get_server_download_url(mc_version)
            
            response = requests.get(download_info["url"], stream=True)
            response.raise_for_status()
            
            temp_path = jar_path + ".tmp"
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                        
            os.rename(temp_path, jar_path)
            print(f"Successfully downloaded server JAR for {mc_version}")

        
        return jar_path