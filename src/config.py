from pathlib import Path
import os
import yaml

class CcctlConfig:
    def __init__(self, integration, llm_endpoint=None, model=None, **kwargs):
        self.integration = integration
        self.llm_endpoint = llm_endpoint or ""
        self.model = model or ""
        self.aws_sso_profile = kwargs.get("aws_sso_profile", "")
        self.aws_regions = kwargs.get("aws_regions", [])
        self.config = {}
        self.config[self.integration] = {}
        self.home = Path.home()

    def load_aws(self):
        with open(f"{self.home}/.ccctl/config.yaml",'r') as f:
            return yaml.safe_load(f)

    def setup_aws(self):
        if not os.path.isdir(f"{self.home}/.ccctl"):
            os.mkdir(f"{self.home}/.ccctl")
        self.config[self.integration]["llm_endpoint"] = self.llm_endpoint
        self.config[self.integration]["model"] = self.model

        if self.aws_sso_profile:
            self.config[self.integration]["aws_sso_profile"] = self.aws_sso_profile
            self.config[self.integration]["aws_regions"] = self.aws_regions

        with open(f"{self.home}/.ccctl/config.yaml", 'w+') as configfile:
            yaml.dump(self.config, configfile, sort_keys=False) 

