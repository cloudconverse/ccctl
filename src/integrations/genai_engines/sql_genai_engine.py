from llama_index.core import VectorStoreIndex, Settings, SQLDatabase
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine,
)
from llama_index.llms.ollama import Ollama
from rich.console import Console
import sys
from pathlib import Path
from sqlalchemy import event, Engine
import json

err_console = Console(stderr=True)

class SQLGenAIEngine:
    def __init__(self, llm_endpoint, model, connection_string):
        self.llm_endpoint = llm_endpoint
        self.model = model
        self.home = Path.home()
        # we only support sqlite
        self.db = CCSQLDatabase.from_uri(f"sqlite:///{connection_string}")

    def index_tables(self, exclude=["aws_ec2_reserved_instance", 
                                    "aws_ec2_spot_price", 
                                    "aws_ec2_instance_type"]):
        """
        We remove some ec2 tables that can confuse LLMs on asking for ec2s
        """
        raw_query = self.db.run_sql("SELECT name FROM pragma_module_list()")
        table_names = [t[0] for t in raw_query[1]["result"] if t[0].startswith("aws") and t[0] not in exclude]
        table_schema_objs = [(SQLTableSchema(table_name=t)) for t in table_names]
        table_node_mapping = SQLTableNodeMapping(self.db)
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
        obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex
        )

        return obj_index

    @event.listens_for(Engine, "connect")
    def receive_connect(connection, record):
        home = Path.home()
        connection.enable_load_extension(True)
        connection.execute(f"select load_extension('{home}/.ccctl/steampipe_sqlite_aws')")
        connection.enable_load_extension(False)

    def build_query_engine(self):
        if not self.llm_endpoint or not self.model:
            err_console.print("Please set --llm-endpoint and/or --model")
            sys.exit(1)
        table_indexes = self.index_tables()
        self.llm = Ollama(base_url=self.llm_endpoint, model=self.model, request_timeout=60.0)
        self.query_engine = SQLTableRetrieverQueryEngine(
            self.db, table_indexes.as_retriever(similarity_top_k=1), llm=self.llm
        )

    def authenticate_aws_steampipe(self, aws_sso_profile, aws_regions):
        if not aws_sso_profile:
            err_console.print("Please set --aws_sso_profile and/or --aws_regions")
            sys.exit(1)
        aws_steampipe_config = json.dumps({"profile": aws_sso_profile, "regions": aws_regions})
        self.db.run_sql("select steampipe_configure_aws('{}');".format(aws_steampipe_config))

    def query(self, query):
        return self.query_engine.query(query)

class CCSQLDatabase(SQLDatabase):
    def get_single_table_info(self, table_name):
        """Get table info for a single table."""
        # a money patch to remove foriegn keys checks as our virtual tables dont have foriegn keys
        # taken from: https://github.com/run-llama/llama_index/blob/38cfe22bfd4a1763c7d998aa26002d84b4c7e1b3/llama-index-core/llama_index/core/utilities/sql_wrapper.py#L151
        template = "Table '{table_name}' has columns: {columns}, "
        try:
            # try to retrieve table comment
            table_comment = self._inspector.get_table_comment(
                table_name, schema=self._schema
            )["text"]
            if table_comment:
                template += f"with comment: ({table_comment}) "
        except NotImplementedError:
            # get_table_comment raises NotImplementedError for a dialect that does not support comments.
            pass
        
        columns = []
        for column in self._inspector.get_columns(table_name, schema=self._schema):
            if column.get("comment"):
                columns.append(
                    f"{column['name']} ({column['type']!s}): "
                    f"'{column.get('comment')}'"
                )
            else:
                columns.append(f"{column['name']} ({column['type']!s})")
        column_str = ", ".join(columns)
        
        return template.format(
            table_name=table_name, columns=column_str
        )

