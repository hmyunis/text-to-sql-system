from django.apps import apps

def get_schema_string():
    app_models = apps.get_app_config('api').get_models()
    schema_parts = []

    for model in app_models:
        table_name = model._meta.db_table
        columns = []
        for field in model._meta.fields:
            col_type = "INT" if "int" in field.get_internal_type().lower() else "TEXT"
            columns.append(f"{field.name} {col_type}")
        
        schema_parts.append(f"CREATE TABLE {table_name} ({', '.join(columns)})")

    return " ".join(schema_parts)

def get_text_columns():
    app_models = apps.get_app_config('api').get_models()
    text_columns = []
    for model in app_models:
        for field in model._meta.fields:
            field_type = field.get_internal_type().lower()
            if "char" in field_type or "text" in field_type or "email" in field_type:
                text_columns.append(field.name)
    return text_columns
