from pathlib import Path
import configparser
import os

class CcctlConfig:
	def __init__(self, integration, llm_endpoint=None, model=None, **kwargs):
		self.integration = integration
		self.llm_endpoint = llm_endpoint or ""
		self.model = model or ""
		self.aws_sso_profile = kwargs.get("aws_sso_profile", "")
		self.aws_regions = kwargs.get("aws_regions", "")
		self.config = configparser.ConfigParser()
		self.config[self.integration] = {}

	def setup_aws(self):
		home = Path.home()
		if not os.path.isdir(f"{home}/.ccctl"):
			os.mkdir(f"{home}/.ccctl")
		self.config[self.integration]["llm_endpoint"] = self.llm_endpoint
		self.config[self.integration]["model"] = self.model
		self.config[self.integration]["aws_sso_profile"] = self.aws_sso_profile
		self.config[self.integration]["aws_regions"] = self.aws_regions
		with open(f"{home}/ccctl/config", 'w') as configfile:
  			self.config.write(configfile)

