import typer
from integrations.aws_steampipe import AWSSteampipe
from config import CcctlConfig

app = typer.Typer()

@app.command()
def init(integration: str, 
         llm_endpoint: Annotated[Optional[str], typer.Argument()] = None,
         model: Annotated[Optional[str], typer.Argument()] = None):
    print(f"Hello {integration}")
    ccctl_config = CcctlConfig(llm_endpoint, model)

    if integration == "aws":
        aws_steampipe = 

@app.command()
def query


if __name__ == "__main__":
    typer.run(main)