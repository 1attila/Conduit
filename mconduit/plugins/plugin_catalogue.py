from typing import Optional, Dict, List, TYPE_CHECKING
from dataclasses import dataclass
from pathlib import Path
from io import BytesIO
import subprocess
import threading
import datetime
import requests
import zipfile
import json
import sys
import os

from ..constants import PLUGINS_DIR, METADATA_FILENAME, CATALOGUE_URL, ACTIVE_PLUGINS_FILE
from ..utils.version_checker import is_new_version

if TYPE_CHECKING:
    from ..handler import Handler
    from ..server import Server


class PluginCatalogueDownloadError(Exception):
    """
    Error while requesting a copy of the catalogue
    """

class PluginDoesntExist(Exception):
    """
    The given plugin it's not in the `/plugins` dir
    """

class PluginNotInArchive(Exception):
    """
    The given plugin it's not present in the latest copy downloaded from the archive
    """

class PluginAlreadyDownloaded(Exception):
    """
    The given plugin is present in the `/plugins` folder
    """

class MissingMetadataFile(Exception):
    """
    The given plugin doesn't have the `metadata.json` file inside it's folder
    """

class MissingPluginVersion(Exception):
    """
    The given plugin doesn't have the `version` field in it's `metadata.json` file
    """

class PluginAlreadyUpdated(Exception):
    """
    The given plugin it's already in it's latest version and can't be updated
    """


@dataclass
class PluginCatalogueCache:

    update_time: datetime.datetime
    file_cache: bytes
    latest_versions: Dict[str, str]


class PluginCatalogue:
    """

    Class that represent the PluginCatalogue.

    It's responsible for downloading and keeping track of the updates and download the plugins.
    """


    __catalogue_url: str
    __base_plugin_path: str
    __plugin_catalogue_cache: PluginCatalogueCache
    __handler: "Handler"
    __etag: Optional[str]
    __lock: threading.RLock
    __skipped_updates: List[str]


    def __init__(
        self,
        handler: "Handler",
        catalogue_url: Optional[str]=None,
        base_plugin_path: Optional[str]=None
    ) -> None:
        
        self.__handler = handler
        self.__lock = threading.RLock()
        self.__skipped_updates = []
        self.__etag = None


        self.__catalogue_url = CATALOGUE_URL if catalogue_url is None else catalogue_url
        self.__base_plugin_path = "ConduitPlugins-main/plugins/" if base_plugin_path is None else base_plugin_path


    def _update_catalogue_cache(self) -> None:
        """
        Fetches the latest version of the plugins catalogue.

        Uses ETags to avoid to hit the maximum requests.

        This should be called only by AsyncTaskLoop
        """

        headers = {}
        
        if self.__etag:
            headers["If-None-Match"] = self.__etag

        try:
            response = requests.get(self.__catalogue_url, headers=headers)

        except:

            error = "Unable to fetch catalogue data"

            try:
                self.__handler.cli.out(error)
            except:
                print(error)

            return
        
        try:
            response.raise_for_status()

        except Exception as e:

            error = "Unable to fetch catalogue data"

            try:
                self.__handler.cli.out(error)
            except:
                print(error)
            
            return

        if response.status_code == 200:
            
            self.__plugin_catalogue_cache = PluginCatalogueCache(
                update_time = datetime.datetime.now(),
                file_cache = response.content,
                latest_versions = {}
            )

            self.__etag = response.headers.get("ETag")
            self.__plugin_catalogue_cache.latest_versions = self._get_latest_plugins_version()
            self._check_for_updates()

        elif response.status_code == 304:
            self.__plugin_catalogue_cache.update_time = datetime.datetime.now()
        else:
            raise PluginCatalogueDownloadError()


    def _get_latest_plugins_version(self) -> Dict[str, str]:
        """
        Returns a dict that matches each plugin name with his latest version
        """
        
        latest_versions = {}

        with zipfile.ZipFile(BytesIO(self.__plugin_catalogue_cache.file_cache)) as zip_file:

            metadatas = [m for m in zip_file.namelist() if m.endswith(METADATA_FILENAME)]

            for metadata in metadatas:

                with zip_file.open(metadata) as f:

                    meta_json = json.load(f)
                    latest_versions[meta_json["name"]] = meta_json["version"]

        return latest_versions
        

    def _check_for_updates(self) -> None:

        try:
            downloaded_plugins = os.listdir(PLUGINS_DIR)

        except FileNotFoundError:
            return

        for plugin, latest_version in self.latest_plugin_versions.items():

            if plugin in downloaded_plugins:

                if plugin in self.__skipped_updates:
                    continue
                
            try:
                with open(os.path.join(PLUGINS_DIR, plugin, METADATA_FILENAME)) as f:
                    version = json.load(f)["version"]

            except FileNotFoundError:
                continue
                    
            if is_new_version(version, latest_version):
                self.__handler.to_all_servers(lambda s: s.plugin_manager._try_update_plugin(plugin, latest_version))

    
    def _download_plugin(self, plugin_name: str) -> None:
        """
        Downloads a new plugin from the catalogue
        """

        with self.__lock:

            with zipfile.ZipFile(BytesIO(self.__plugin_catalogue_cache.file_cache)) as zip_file:
            
                plugin_folder_prefix = f"{self.__base_plugin_path}{plugin_name}/"
                members = [m for m in zip_file.namelist() if m.startswith(plugin_folder_prefix)]

                if not members:
                    raise PluginNotInArchive()
            
                for member in members:

                    member_path = os.path.relpath(member, plugin_folder_prefix)

                    if member_path:

                        target_path = os.path.join(PLUGINS_DIR, plugin_name, member_path)

                        if member.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)

                        else:
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)

                            with zip_file.open(member) as source, open(target_path, 'wb') as target:
                            
                                src = source.read()
                                target.write(src)

                                if member.endswith(METADATA_FILENAME):
                                
                                    json_metadata = json.loads(src)
                                    requirements = json_metadata["dependencies"]
                                
                                    if len(requirements) > 0:
                                    
                                        self.__handler.cli.out("Installing the following packages:", *requirements)

                                        try:
                                            subprocess.check_call([sys.executable, "-m", "pip", "install", *requirements])
            
                                        except Exception as e:
                                            raise e


    def download_plugin(self, plugin_name: str) -> None:
        """
        Downloads the given plugin, if it's not in the `plugins` folder yet
        """
        
        with self.__lock:

            if Path(PLUGINS_DIR).joinpath(plugin_name).exists() or plugin_name == "builtin_plugin":
                raise PluginAlreadyDownloaded()
        
            try:
                self._download_plugin(plugin_name)
                self.__handler.telemetry.plugin_download(plugin_name)
            except Exception as e:
                raise e
        

    def update_plugin(self, plugin_name: str) -> None:
        """
        Updates the given plugin, if its downloaded
        """

        with self.__lock:

            if not Path(PLUGINS_DIR).joinpath(plugin_name).exists():
                raise PluginDoesntExist()

            filename = Path(PLUGINS_DIR).joinpath(plugin_name)
            meta_path = os.path.join(filename, METADATA_FILENAME)
        
            if not Path(meta_path).exists():
                raise MissingMetadataFile()

            metadata = json.load(open(meta_path))

            if not "version" in metadata.keys():
                raise MissingPluginVersion()
        
            current_version = metadata["version"]

            if plugin_name in self.__plugin_catalogue_cache.latest_versions.keys():

                catalogue_version = self.__plugin_catalogue_cache.latest_versions[plugin_name]

                if is_new_version(current_version, catalogue_version):
                    try:
                        self._download_plugin(plugin_name)
                        self.__handler.telemetry.plugin_update(plugin_name, current_version, catalogue_version)
                    except Exception as e:
                        raise e
                else:
                    raise PluginAlreadyUpdated()
            else:
                raise PluginNotInArchive()

    
    def set_permanent(
        self,
        server: "Server",
        plugin_name: str,
        value: bool
    ) -> None:
        """
        Sets the permanent value for the given plugin of the given server.

        If value is set to `True`, the server `PluginManager` will load it automatically at every conduit start
        """

        with self.__lock:

            with open(ACTIVE_PLUGINS_FILE) as f:
                active_plugins = json.load(f)
                
                try:
                    sap = active_plugins[server.name]

                    if value is True and plugin_name not in sap:
                        sap.append(plugin_name)
                    elif value is False and plugin_name in sap:
                        sap.remove(plugin_name)

                except Exception as e:
                    raise e
            
            with open(ACTIVE_PLUGINS_FILE, "w") as f:
                f.write(json.dumps(active_plugins, indent=4))


    def get_active_plugins_for(self, server: "Server") -> List[str]:
        """
        Returns the plugins that a Server PluginManager should load.

        Fetches these values from  `active_plugins.json` and if the server is missing adds it and returns an empty list
        """

        with self.__lock:
            
            with open(ACTIVE_PLUGINS_FILE, "r") as f:

                all_active_plugins = json.load(f)

                try:
                    return all_active_plugins[server.name]
                except KeyError:
                    
                    f.close()
                    all_active_plugins[server.name] = []

                    with open(ACTIVE_PLUGINS_FILE, "w") as f:
                        json.dump(all_active_plugins, f, indent=4)

                    return []


    def skip_update(self, plugin_name: str) -> None:
        """
        Appends the plugin_name to the list of updates to skip
        """

        with self.__lock:

            if plugin_name not in self.__skipped_updates:
                self.__skipped_updates.append(plugin_name)
        
    
    @property
    def cache(self) -> PluginCatalogueCache:
        """
        Entire plugin catalogue cache
        """

        return self.__plugin_catalogue_cache
    

    @property
    def update_time(self) -> datetime.datetime:
        """
        Datetime of the last cache update
        """

        return self.__plugin_catalogue_cache.update_time
    

    @property
    def latest_plugin_versions(self) -> Dict[str, str]:
        """
        Returns a dict that matches every plugin name in the catalogue with it's latest version
        """

        return self.__plugin_catalogue_cache.latest_versions
    

    @property
    def skipped_updates(self) -> List[str]:
        """
        Skipped plugins updates
        """

        return self.__skipped_updates