import sqlite3
from pathlib import Path
from sys import platform
import platform
import requests
import tarfile

SQLITE_AWS_EXTENSION_ENDPOINT = "https://github.com/turbot/steampipe-plugin-aws/releases/download/{}/steampipe_sqlite_aws.{}_{}.tar.gz"
SQLITE_PLUGIN_VERSION = "v0.147.0"

class AWSSteampipe:
    def __init__(self):
        self.db_connection = None
        self.home = Path.home()

    def setup_sqlite(self):
        self.db_connection = sqlite3.connect(f"{self.home}/.ccctl/aws_steampipe.db")
        self.cursor = db_connection.cursor()

    def download_sqlite_extension(self):
        response = requests.get(SQLITE_AWS_EXTENSION_ENDPOINT.format(SQLITE_PLUGIN_VERSION, platform.system().lower(), platform.machine()))
        if response.ok:
            with open(f"{self.home}/.ccctl/steampipe_sqlite_aws_{SQLITE_PLUGIN_VERSION}.tar.gz", mode="wb") as file:
                file.write(response.content)
        extension_tar = tarfile.open(f"{self.home}/.ccctl/steampipe_sqlite_aws_{SQLITE_PLUGIN_VERSION}.tar.gz", "r:gz")
        extension_tar.extractall()
        extension_tar.close()

    def load_sqlite_extension(self):
        self.cursor.execute(f".load {self.home}/.ccctl/steampipe_sqlite_aws.so")

    def setup_tables(self):
