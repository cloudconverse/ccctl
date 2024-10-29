from llama_index.core import VectorStoreIndex, Settings, StorageContext, load_index_from_storage
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
from .ccsqldatabase import CCSQLDatabase
from rich.console import Console
import sys
from pathlib import Path
from sqlalchemy import event, Engine
import json
import os

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
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        index_directory = f"{self.home}/.ccctl/indexes"
        Path(index_directory).mkdir(parents=True, exist_ok=True)
        if os.path.isfile(f"{index_directory}/docstore.json"):
            # load index from disk
            storage_context = StorageContext.from_defaults(persist_dir=index_directory)
            obj_index = load_index_from_storage(storage_context)
        else:
            # rebuild in the index
            raw_query = self.db.run_sql("SELECT name FROM pragma_module_list()")
            table_names = [t[0] for t in raw_query[1]["result"] if t[0].startswith("aws") and t[0] not in exclude]
            table_schema_objs = [(SQLTableSchema(table_name=t)) for t in table_names]
            table_node_mapping = SQLTableNodeMapping(self.db)
            
            obj_index = ObjectIndex.from_objects(
                table_schema_objs,
                table_node_mapping,
                VectorStoreIndex
            )

            with open(f"{index_directory}/docstore.json", 'a') as doc_store:
                json.dump({}, doc_store)

            with open(f"{index_directory}/index_store.json", 'a') as index_store:
                json.dump({}, index_store)
                
            obj_index.persist(index_directory)

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
