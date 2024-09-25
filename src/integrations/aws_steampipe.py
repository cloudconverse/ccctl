import sqlite3
from pathlib import Path
from sys import platform
import platform
import requests
import tarfile
import os
import sys
from rich.console import Console
import json

SQLITE_AWS_EXTENSION_ENDPOINT = "https://github.com/turbot/steampipe-plugin-aws/releases/download/{}/steampipe_sqlite_aws.{}_{}.tar.gz"
SQLITE_PLUGIN_VERSION = "v0.147.0"
err_console = Console(stderr=True)

class AWSSteampipe:
    def __init__(self, aws_sso_profile, aws_regions=[]):
        self.db_connection = None
        self.home = Path.home()
        self.aws_sso_profile = aws_sso_profile
        self.aws_regions = aws_regions

    def setup_sqlite(self):
        self.db_connection = sqlite3.connect(f"{self.home}/.ccctl/aws_steampipe.db")
        self.db_connection.enable_load_extension(True)
        self.cursor = self.db_connection.cursor()

    def download_sqlite_extension(self):
        # don't download if already downloaded
        if os.path.isfile(f"{self.home}/.ccctl/steampipe_sqlite_aws.so"):
            return

        response = requests.get(SQLITE_AWS_EXTENSION_ENDPOINT.format(SQLITE_PLUGIN_VERSION, platform.system().lower(), platform.machine()))
        if response.ok:
            with open(f"{self.home}/.ccctl/steampipe_sqlite_aws_{SQLITE_PLUGIN_VERSION}.tar.gz", mode="wb") as file:
                file.write(response.content)
            extension_tar = tarfile.open(f"{self.home}/.ccctl/steampipe_sqlite_aws_{SQLITE_PLUGIN_VERSION}.tar.gz", "r:gz")
            extension_tar.extractall(f"{self.home}/.ccctl/")
            extension_tar.close()

    def load_sqlite_extension(self):
        self.cursor.execute(f"select load_extension('{self.home}/.ccctl/steampipe_sqlite_aws.so')")

    def setup_tables(self):
        if not self.aws_sso_profile:
            err_console.print("Please set --aws_sso_profile and/or --aws_regions")
            sys.exit(1)
        aws_steampipe_config = json.dumps({"profile": self.aws_sso_profile, "regions": self.aws_regions})
        self.cursor.execute("select steampipe_configure_aws('{}');".format(aws_steampipe_config))
