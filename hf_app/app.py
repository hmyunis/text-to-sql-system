import gradio as gr
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer, util

# --- CONFIGURATION ---
FINE_TUNED_MODEL_ID = "hmyunis/t5-base-sql-custom" 

print(f"Loading Model: {FINE_TUNED_MODEL_ID}...")
try:
    tokenizer = T5Tokenizer.from_pretrained(FINE_TUNED_MODEL_ID)
    model = T5ForConditionalGeneration.from_pretrained(FINE_TUNED_MODEL_ID)
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("Models loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR LOADING MODELS: {e}")

def format_schema_like_training(raw_column_list):
    """
    Transforms ['api_customer.name', 'api_customer.city', 'api_order.id']
    Into: "api_customer: name, city | api_order: id"
    
    This matches the pattern the model saw during training.
    """
    schema_map = {}
    for item in raw_column_list:
        if "." in item:
            table, col = item.split('.', 1)
            if table not in schema_map:
                schema_map[table] = []
            schema_map[table].append(col)
            
    # Join nicely
    parts = [f"{table}: {', '.join(cols)}" for table, cols in schema_map.items()]
    return " | ".join(parts)

def get_sql_pipeline(question, all_columns_str):
    print(f"Input Q: {question}")
    
    try:
        # 1. Parse Columns
        all_columns = eval(all_columns_str) 
        
        # 2. Schema Linking (Embeddings)
        question_embedding = embedder.encode(question, convert_to_tensor=True)
        column_embeddings = embedder.encode(all_columns, convert_to_tensor=True)
        
        # Increase Top-K to 10 to ensure we get enough context from the right table
        hits = util.semantic_search(question_embedding, column_embeddings, top_k=10)
        relevant_cols = [all_columns[hit['corpus_id']] for hit in hits[0]]
        
        # 3. Formulate Prompt (CRITICAL FIX HERE)
        # We re-format the list to look like "table: col1, col2"
        schema_context = format_schema_like_training(relevant_cols)
        
        input_text = f"translate English to SQL: {question} </s> {schema_context}"
        print(f"Prompt: {input_text}")
        
        # 4. Generate
        input_ids = tokenizer(input_text, return_tensors="pt").input_ids
        
        outputs = model.generate(
            input_ids, 
            max_length=128, 
            num_beams=4, 
            early_stopping=True
        )
        
        generated_sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Output: '{generated_sql}'")
        
        return generated_sql

    except Exception as e:
        return f"Error: {str(e)}"

iface = gr.Interface(fn=get_sql_pipeline, inputs=["text", "text"], outputs="text")
iface.launch()