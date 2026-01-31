import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from gradio_client import Client
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

from .utils import get_schema_string, get_all_columns_list
from .services import execute_query

# --- Helper to compare two SQL results ---
def compare_query_results(sql_generated, sql_expected):
    """
    Returns True if both queries return the exact same data.
    """
    try:
        # Execute Generated
        res_gen = execute_query(sql_generated)
        if "error" in res_gen:
            return False, res_gen["error"]

        # Execute Expected (Gold Standard)
        res_exp = execute_query(sql_expected)
        if "error" in res_exp:
            return False, "Gold standard query failed (bad test case)"

        # Compare Data
        # We sort the data to ensure column order doesn't fail the test
        data_gen = sorted(str(d) for d in res_gen.get("data", []))
        data_exp = sorted(str(d) for d in res_exp.get("data", []))

        return data_gen == data_exp, "Success"
    except Exception as e:
        return False, str(e)

@api_view(['POST'])
def ask_question(request):
    user_question = request.data.get("question")
    if not user_question:
        return Response({"error": "No question provided"}, status=400)

    # 1. Translate if needed
    try:
        # Default to auto
        src_lang = 'auto'
        try:
            # Try to help the translator by detecting Amharic explicitly
            # This helps for short queries where 'auto' might be ambiguous
            if detect(user_question) == 'am':
                src_lang = 'am'
                print(f"Detected Amharic via langdetect")
        except:
            pass # Fallback to auto if detection fails

        translated_q = GoogleTranslator(source=src_lang, target='en').translate(user_question)
        
        if translated_q and translated_q != user_question:
             print(f"Translation ({src_lang}): {user_question} -> {translated_q}")
             user_question = translated_q
             
    except Exception as e:
        print(f"Translation failed: {e}")

    # 2. Get all columns to send to the Vectorizer
    all_cols = get_all_columns_list()

    try:
        # 2. Connect to HF Space
        model_id = os.getenv("HF_MODEL_ID", "hmyunis/text-to-sql-bot")
        client = Client(model_id, token=os.getenv("HF_TOKEN"))

        # 3. Predict (Send Question + List of Columns)
        generated_sql = client.predict(user_question, str(all_cols))

        # 4. Clean up output (T5 sometimes generates text, rarely extra junk)
        generated_sql = generated_sql.strip()

        # 5. Execute
        execution_result = execute_query(generated_sql)
        return Response(execution_result)

    except Exception as e:
        return Response({"error": f"AI Error: {str(e)}"}, status=500)

@api_view(['GET'])
def run_evaluation(request):
    """
    Evaluation Metric: Execution Accuracy (ExMatch)
    This is superior to BLEU because it checks if the code WORKS, not just if it looks right.
    """
    # 1. The Gold Standard Test Set
    test_set = [
        {
            "question": "Show me all customers",
            "gold_sql": "SELECT * FROM api_customer"
        },
        {
            "question": "Who lives in Axum?",
            "gold_sql": "SELECT * FROM api_customer WHERE city = 'Axum'"
        },
        {
            "question": "Count total orders",
            "gold_sql": "SELECT COUNT(*) FROM api_order"
        },
        {
            "question": "Show me products with price higher than 15",
            "gold_sql": "SELECT * FROM api_product WHERE price > 15"
        },
        {
            "question": "List valuable products",
            "gold_sql": "SELECT * FROM api_product ORDER BY price DESC LIMIT 5"
        },
        {
            "question": "Show all orders",
            "gold_sql": "SELECT * FROM api_order"
        },
        {
            "question": "List all products",
            "gold_sql": "SELECT * FROM api_product"
        },
        {
            "question": "How many customers are there?",
            "gold_sql": "SELECT COUNT(*) FROM api_customer"
        },
        {
            "question": "Show customers from Addis Ababa",
            "gold_sql": "SELECT * FROM api_customer WHERE city = 'Addis Ababa'"
        },
        {
            "question": "Show products cheaper than 10",
            "gold_sql": "SELECT * FROM api_product WHERE price < 10"
        }
    ]

    all_cols = str(get_all_columns_list())
    client = Client(os.getenv("HF_MODEL_ID", "hmyunis/text-to-sql-bot"), token=os.getenv("HF_TOKEN"))

    results = []
    correct_count = 0

    for item in test_set:
        question = item["question"]
        gold_sql = item["gold_sql"]

        try:
            # 2. Get AI Prediction
            generated_sql = client.predict(question, all_cols)
            generated_sql = generated_sql.strip()

            # 3. Calculate Execution Accuracy (The Logic Check)
            is_correct, debug_msg = compare_query_results(generated_sql, gold_sql)

            if is_correct:
                correct_count += 1
                status = "PASS"
            else:
                status = "FAIL"

            # 4. Calculate BLEU (The Syntax Check - purely for reference)
            ref_tokens = gold_sql.lower().split()
            cand_tokens = generated_sql.lower().split()
            bleu = sentence_bleu([ref_tokens], cand_tokens, smoothing_function=SmoothingFunction().method1)

            results.append({
                "question": question,
                "status": status,
                "generated_sql": generated_sql,
                "expected_sql": gold_sql,
                "execution_match": is_correct,
                "bleu_score": round(bleu, 4),
                "debug": debug_msg
            })

        except Exception as e:
            results.append({
                "question": question,
                "status": "ERROR",
                "error": str(e)
            })

    accuracy = (correct_count / len(test_set)) * 100

    return Response({
        "metric": "Execution Accuracy (ExMatch)",
        "description": "Measures if the generated SQL returns the exact same database result as the Gold Standard query.",
        "overall_accuracy_percent": f"{accuracy}%",
        "detailed_results": results
    })

@api_view(['GET'])
def get_schema_info(request):
    return Response({"schema": get_schema_string()})
