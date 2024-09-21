import typer
from integrations.aws_steampipe import AWSSteampipe
from config import CcctlConfig

app = typer.Typer()

@app.command()
def init_aws(integration: str, 
             llm_endpoint: Annotated[Optional[str], typer.Argument()] = None,
             model: Annotated[Optional[str], typer.Argument()] = None,
             aws_sso_profile: Annotated[Optional[str], typer.Argument()] = None,
             aws_regions: Annotated[Optional[str], typer.Argument()] = None):
    print(f"Hello {integration}")
    ccctl_config = CcctlConfig(integration, llm_endpoint, model, aws_sso_profile, aws_regions)

    if integration == "aws":
        aws_steampipe = AWSSteampipe

@app.command()
def query


if __name__ == "__main__":
    typer.run(main)