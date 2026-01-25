import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from gradio_client import Client
from .utils import get_schema_string
from .services import execute_query

@api_view(['POST'])
def ask_question(request):
    user_question = request.data.get("question")
    if not user_question:
        return Response({"error": "No question provided"}, status=400)

    schema = get_schema_string()
    prompt = (
        f"{schema} \n\n"
        "-- Use case-insensitive comparisons for text columns "
        "(e.g., LOWER(column) = LOWER('value')).\n"
        f"-- {user_question} \n SELECT"
    )

    try:
        model_id = os.getenv("HF_MODEL_ID", "hmyunis/text-to-sql-bot")
        client = Client(model_id, token=os.getenv("HF_TOKEN"))
        result = client.predict(prompt)
        
        raw_output = result if isinstance(result, str) else result[0]
        
        upper_output = raw_output.upper()
        if "SELECT" in upper_output:
            select_index = upper_output.rfind("SELECT")
            generated_sql = raw_output[select_index:]
        else:
            generated_sql = raw_output

        generated_sql = generated_sql.split(";")[0].split("\n")[0].strip()

        execution_result = execute_query(generated_sql)
        return Response(execution_result)

    except Exception as e:
        return Response({"error": f"AI Error: {str(e)}"}, status=500)

@api_view(['GET'])
def get_schema_info(request):
    return Response({"schema": get_schema_string()})
