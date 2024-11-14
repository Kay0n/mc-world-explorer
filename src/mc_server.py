import os
import shutil
import subprocess
import signal
import queue
import threading
from mcstatus import JavaServer
from packaging import version
from jar_downloader import JarDownloader
from save_manager import SaveManager




class MinecraftServer():

    def __init__(self, server_dir: str, jar_dir: str, save_mgr: SaveManager, port: int=25565):
        self.server_process = None
        self.jar_downloader = JarDownloader()
        self.server_checker = JavaServer("localhost", port)
        self.server_dir = server_dir
        self.jar_dir = jar_dir
        self.server_status = "Offline"
        self.current_save_name = "invalid-1.0.0"
        self.save_mgr = save_mgr
        self.console_queue = queue.Queue()
        self.console_thread = None

    def can_connect(self) -> bool:
        try:
            self.server_checker.status()
        except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError):
            return False
        return True


    def get_status(self) -> dict:
        """
        Returns dict representing server status: 
        {"status_description": str, "version": str, "world_name": str}
        Descriptions: Offline, Setup, Starting, Running
        """

        if self.server_status == "Offline" or self.server_status == "Setup":
            pass

        elif self.server_status == "Starting" or self.server_status == "Running":
            self.server_status = "Running" if self.can_connect() else "Starting"

        if self.server_process is not None and self.server_process.poll() is not None:
            self.server_status = "Offline"

        
        name, version = SaveManager.split_world_name(self.current_save_name)

        return {
            "status_description": self.server_status,
            "version": version,
            "world_name": name
        }


        


    def get_java_command(self, mc_version, max_memory="4G"):
        """
        Determine the appropriate Java command based on Minecraft version
        Returns tuple of (java_command, memory_settings)
        """
        mc_ver = version.parse(mc_version)
        
        mem_settings = f"-Xmx{max_memory} -Xms128M"
        
        if mc_ver >= version.parse("1.20.5"):
            return "java", mem_settings  # java21
        elif mc_ver >= version.parse("1.18"):
            return "java17", mem_settings
        elif mc_ver >= version.parse("1.17"):
            return "java16", mem_settings
        elif mc_ver >= version.parse("1.12"):
            return "java8", mem_settings
        else:
            return "java8", mem_settings
    


    def setup_files(self, mc_version, save_dir):

        world_dir = os.path.join(self.server_dir, "world")

        # remove preexisting files
        if os.path.exists(world_dir):
            shutil.rmtree(world_dir)
        server_jar = os.path.join(self.server_dir, "server.jar")
        if os.path.exists(server_jar):
            os.remove(server_jar)

        # copy world and server.jar
        shutil.copytree(
            save_dir,
            world_dir
        )
        shutil.copy2(
            os.path.join(self.jar_dir, f"server-{mc_version}.jar"),
            server_jar
        )
        
        # create signed eula.txt
        eula_path = os.path.join(self.server_dir, "eula.txt")
        if not os.path.exists(eula_path):
            with open(eula_path, "w") as f:
                f.write("eula=true\n")




    def get_version_from_name(self, world_name):
        """Extract version from world name (e.g., 'world-1.19.2' -> '1.19.2')"""
        return world_name.split('-')[-1]



    def start_server(self, world_name, mc_version):
        """Start the Minecraft server with the specified world"""

        self.stop_server()

        

        self.server_status = "Setup"
        self.current_save_name = world_name + "-" + mc_version

        self.jar_downloader.download_if_missing(mc_version, self.jar_dir)

        if self.check_stopping(): return

        save_dir = self.save_mgr.get_save_path(world_name + "-" + mc_version)
        self.setup_files(mc_version, save_dir)
        
        if self.check_stopping(): return

        java_cmd, mem_settings = self.get_java_command(mc_version)
        command = f"{java_cmd} {mem_settings} -jar server.jar nogui"
        
        self.server_process = subprocess.Popen(
            command.split(),
            cwd=self.server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid    
        )

        if self.check_stopping(): return

        self.console_thread = threading.Thread(
            target=self._read_console_output,
            daemon=True
        )
        self.console_thread.start()

        if self.check_stopping(): return
        self.server_status = "Starting"

        return True
    


    def stop_server(self):
        """Stop the currently running server if any"""
        if self.server_process:
            try:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                self.server_process.wait(timeout=25)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass # may have already exited
            finally:
                self.server_process = None
        self.server_status = "Offline"
    


    def check_stopping(self) -> bool:
        if self.server_status == "Offline":
            self.stop_server()
            return True
        return False
    


    def _read_console_output(self):
        """Read console output and put it in the queue"""
        while self.server_process:
            line = self.server_process.stdout.readline()
            if line:
                self.console_queue.put(line.decode().strip())
    


    def send_command(self, command):
        """Send a command to the server"""
        if self.server_process and self.server_process.poll() is None:
            self.server_process.stdin.write(f"{command}\n".encode())
            self.server_process.stdin.flush()
            return True
        return False