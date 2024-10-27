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
from .genai_engines.sql_genai_engine import SQLGenAIEngine

SQLITE_AWS_EXTENSION_ENDPOINT = "https://github.com/turbot/steampipe-plugin-aws/releases/download/{}/steampipe_sqlite_aws.{}_{}.tar.gz"
SQLITE_PLUGIN_VERSION = "v0.147.0"
err_console = Console(stderr=True)

class AWSSteampipe:
    def __init__(self, aws_sso_profile, aws_regions=[]):
        self.db_connection = None
        self.home = Path.home()
        self.aws_sso_profile = aws_sso_profile
        self.aws_regions = aws_regions
        self.db_connection_string = f"{self.home}/.ccctl/aws_steampipe.db"

    def setup_sqlite(self):
        self.db_connection = sqlite3.connect(self.db_connection_string)
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
            if platform.system().lower() == "darwin":
                os.rename(f"{self.home}/.ccctl/steampipe_sqlite_aws.so", f"{self.home}/.ccctl/steampipe_sqlite_aws.dylib")

    def load_sqlite_extension(self):
        self.cursor.execute(f"select load_extension('{self.home}/.ccctl/steampipe_sqlite_aws')")

    def setup_tables(self):
        if not self.aws_sso_profile:
            err_console.print("Please set --aws_sso_profile and/or --aws_regions")
            sys.exit(1)
        aws_steampipe_config = json.dumps({"profile": self.aws_sso_profile, "regions": self.aws_regions})
        self.cursor.execute("select steampipe_configure_aws('{}');".format(aws_steampipe_config))


    def index_tables(self):
        pass

    def generate_query(self, llm_endpoint, model, query):
        self.genai_engine = SQLGenAIEngine(llm_endpoint, model, self.db_connection_string)
        self.genai_engine.build_query_engine()
        self.genai_engine.authenticate_aws_steampipe(self.aws_sso_profile, self.aws_regions)
        return self.genai_engine.query(query)
