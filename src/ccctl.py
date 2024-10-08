import typer
from typing_extensions import Annotated
from typing import List, Optional
from integrations.aws_steampipe import AWSSteampipe
from config import CcctlConfig

app = typer.Typer(no_args_is_help=True)

def init_aws(integration: str, 
             aws_sso_profile: str,
             aws_regions: list[str],
             llm_endpoint=None,
             model=None):
    ccctl_config = CcctlConfig(integration, llm_endpoint, model, 
                               aws_sso_profile=aws_sso_profile, 
                               aws_regions=aws_regions)
    ccctl_config.setup_aws()

    aws_steampipe = AWSSteampipe(aws_sso_profile, aws_regions)
    aws_steampipe.download_sqlite_extension()
    aws_steampipe.setup_sqlite()
    aws_steampipe.load_sqlite_extension()
    aws_steampipe.setup_tables()

@app.command()
def init(integration: str, 
         llm_endpoint: str = None,
         model: str = None,
         aws_sso_profile: str = None,
         aws_regions: Annotated[Optional[List[str]], typer.Option()] = None):
    """
    $ ccctl init aws # setup AWS steampipe integration
    """

    if integration == "aws":
        init_aws(integration=integration, 
                 llm_endpoint=llm_endpoint, 
                 model=model, 
                 aws_sso_profile=aws_sso_profile, 
                 aws_regions=aws_regions)
    

@app.command()
def query():
    pass


if __name__ == "__main__":
    app()