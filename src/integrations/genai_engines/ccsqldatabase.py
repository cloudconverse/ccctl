from llama_index.core import SQLDatabase

class CCSQLDatabase(SQLDatabase):
    def get_single_table_info(self, table_name):
        """Get table info for a single table."""
        # an override to remove foriegn keys checks as our virtual tables dont have foriegn keys
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