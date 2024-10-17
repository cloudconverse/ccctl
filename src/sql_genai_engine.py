from llama_index.core import SQLDatabase, VectorStoreIndex, Settings
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


class SQLGenAIEngine:
    def __init__(self, llm_endpoint, model, connection_string):
        self.llm_endpoint = llm_endpoint
        self.model = model
        self.db = SQLDatabase.from_uri(connection_string)

    def index_tables(self, exclude=["aws_ec2_reserved_instance", 
                                    "aws_ec2_spot_price", 
                                    "aws_ec2_instance_type"]):
    """
    We remove some ec2 tables that can confuse LLMs on asking for ec2s
    """
        raw_query = self.db.run_sql("SELECT name FROM pragma_module_list()")
        table_names = [t[0] for t in raw_query if t[0].startswith("aws") and t[0] not in exclude]
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

    def build_query_engine(self):
        table_indexes = self.index_tables()
        self.llm = Ollama(base_url=self.endpoint, model=self.model, request_timeout=120.0)
        self.query_engine = SQLTableRetrieverQueryEngine(
            self.db, table_indexes.as_retriever(similarity_top_k=1), llm=self.llm
        )

    def query(self, query):
        return self.query_engine.query(query)
