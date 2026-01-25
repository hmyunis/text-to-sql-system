import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import torch

# NSQL-350M is a CausalLM (like GPT), not a Seq2Seq (like T5)
model_name = "NumbersStation/nsql-350M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_sql(prompt):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    generated_ids = model.generate(input_ids, max_new_tokens=100)
    return tokenizer.decode(generated_ids[0], skip_special_tokens=True)

interface = gr.Interface(fn=generate_sql, inputs="text", outputs="text")
interface.launch()