import os
import glob
from io import BytesIO
import zipfile
from typing import Tuple

class SaveManager:
    def __init__(self, saves_dir: str):
        self.saves_dir = saves_dir
        self.save_cache = []

    def flush_save_cache(self):
        self.save_cache = [];


    def get_split_world_saves(self):
        """Get list of available world saves """
        save_list = glob.glob(os.path.join(self.saves_dir, "*"))
        saves = []

        if len(save_list) == len(self.save_cache):
            return self.save_cache

        for save_path in save_list:

            save_name = str(os.path.basename(save_path))
            
            world_name, version = self.split_world_name(save_name)
            saves.append({
                "name": world_name,
                "version": version,
            })

        sorted_saves = sorted(saves, key=lambda x: x["name"])
        self.save_cache = sorted_saves
        return sorted_saves



    def rename_save(self, save_name: str, new_save_name:str):
        save_path = os.path.join(self.saves_dir, save_name)
        new_save_path = os.path.join(self.saves_dir, new_save_name)
        try:
            os.rename(save_path, new_save_path)
            print(f"Renamed {save_name} to {new_save_name}")
        except FileNotFoundError:
            print(f"Error: The save '{save_name}' does not exist.")
        except FileExistsError:
            print(f"Error: A save with the name '{new_save_name}' already exists.")
        except PermissionError:
            print(f"Error: Insufficient permissions to rename '{save_name}'.")



    def create_world_zip(self, save_name: str):
        """Create a ZIP file of the world save in memory"""
        memory_file = BytesIO()
        world_path = os.path.join(self.saves_dir, save_name)
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(world_path):
                for file in files:
                    absolute_path = os.path.join(root, file)
                    relative_path = os.path.relpath(absolute_path, world_path)
                    zf.write(absolute_path, relative_path)
        
        memory_file.seek(0)
        return memory_file



    @staticmethod
    def split_world_name(save_name: str) -> Tuple[str, str]:
        world_name, separator, version = save_name.rpartition('-')
        if separator:  
            return world_name, version
        raise ValueError(f"Save name {save_name} does not follow 'name-version' format")



    def get_save_path(self, world_name: str) -> str:
        return os.path.join(self.saves_dir, world_name)