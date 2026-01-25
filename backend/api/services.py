import re
from django.db import connection
from .utils import get_text_columns

def _apply_case_insensitive_collation(sql_query):
    if connection.vendor != "sqlite":
        return sql_query

    text_columns = get_text_columns()
    updated_query = sql_query
    for column in text_columns:
        pattern = re.compile(
            rf"(?P<qual>(?:\\b\\w+\\.)?)"
            rf"(?P<col>{re.escape(column)})"
            r"(?!\\s+collate\\s+nocase)"
            r"\\s*=\\s*"
            r"(?P<val>'[^']*'|\"[^\"]*\")",
            re.IGNORECASE,
        )
        updated_query = pattern.sub(
            lambda match: (
                f"{match.group('qual')}{match.group('col')} COLLATE NOCASE = {match.group('val')}"
            ),
            updated_query,
        )
    return updated_query

def execute_query(sql_query):
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    if any(word in sql_query.upper() for word in forbidden):
        return {"error": "Security violation: Only SELECT allowed.", "sql": sql_query}

    try:
        sql_query = _apply_case_insensitive_collation(sql_query)
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return {"columns": columns, "data": data, "sql": sql_query}
            return {"columns": [], "data": [], "sql": sql_query}
    except Exception as e:
        return {"error": f"Database Error: {str(e)}", "sql": sql_query}
