from pathlib import Path
import configparser
import os

class CcctlConfig:
	def __init__(self, llm_endpoint=None, model=None):
		self.llm_endpoint = llm_endpoint
		self.model = model
		self.config = configparser.ConfigParser()

	def setup(self):
		home = Path.home()
		os.mkdir(f"{home}/.ccctl")
		self.config["default"]["llm_endpoint"] = self.llm_endpoint
		self.config["default"]["model"] = self.model 
		with open(f"{home}/ccctl/config", 'w') as configfile:
  			self.config.write(configfile)

