import numpy as np
import time
import os
from langchain_community.llms import Bedrock
import sys
import openai
# 교은 key

# modelID
# meta.llama2-13b-chat-v1
# meta.llama2-70b-chat-v1
model_id = ""
if sys.argv[3] == '13b':
    model_id="meta.llama2-13b-chat-v1"
    # model_id="meta.llama3-8b-instruct-v1:0"
    model_name = "llama3_8b"
if sys.argv[3] == '70b':
    model_id="meta.llama2-70b-chat-v1"
    # model_id="meta.llama3-70b-instruct-v1:0"
    model_name = "llama3_70b"


OUTPUT_FN = "./full_results_2020.pkl"
if sys.argv[1] == '2020':
    OUTPUT_CSV = f"./full_results_2020_{model_name}.csv"
if sys.argv[1] == '2024':
    OUTPUT_CSV = f"./full_results_2024_{model_name}.csv"


def lc(t):
    return t.lower()

def uc(t):
    return t.upper()

def mc(t):
    tmp = t.lower()
    return tmp[0].upper() + t[1:]

def gen_variants(toks):
    results = []
    variants = [lc, uc, mc]
    for t in toks:
        for v in variants:
            results.append(" " + v(t))
    return results

def extract_probs(lp):
    lp_keys = list(lp.keys())
    ps = [lp[k] for k in lp_keys]
    vals = [(lp_keys[ind], ps[ind]) for ind in range(len(lp_keys))]
    vals = sorted(vals, key=lambda x: x[1], reverse=True)
    result = {}
    for v in vals:
        result[v[0]] = v[1]
    return result
            # "prompt": f"\n\nHuman: {system_prompt}\n\nAssistant: {user_prompt}",

# def do_query(system_prompt, user_prompt):
#     bedrock_llm = Bedrock(
#         credentials_profile_name='config.json',
#         model_id=model_id,
#         model_kwargs={
#             "prompt": f"""
#             <|begin_of_text|><|start_header_id|>system<|end_header_id|>
#             {system_prompt}<|eot_id|>
#             <|start_header_id|>user<|end_header_id|>
#             {user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
#             """,
#             "temperature": 1.0,
#             "top_p": 1,
#             "max_gen_len": 3
#             })

#     # Combine system_prompt and user_prompt into a single string
#     combined_prompt = f"""
#             <|begin_of_text|><|start_header_id|>system<|end_header_id|>
#             {system_prompt}<|eot_id|>
#             <|start_header_id|>user<|end_header_id|>
#             {user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
#             """
#                 # <s><<SYS>>\n{system_prompt}\n<</SYS>>\n\nUser:{user_prompt}


#     # Pass the combined prompt as the single argument to predict
#     return bedrock_llm.predict(combined_prompt)

def do_query(system_prompt, user_prompt):
    bedrock_llm = Bedrock(
        credentials_profile_name='default',
        model_id=model_id,
        model_kwargs={
            "prompt": f"<s><<SYS>>\n{system_prompt}\n<</SYS>>\n\nUser:{user_prompt}",
            "temperature": 1.0,
            "top_p": 1,
            "max_gen_len": 3
            })

    # Combine system_prompt and user_prompt into a single string
    combined_prompt = f"<s><<SYS>>\n{system_prompt}\n<</SYS>>\n\nUser:{user_prompt}"
                # <s><<SYS>>\n{system_prompt}\n<</SYS>>\n\nUser:{user_prompt}


    # Pass the combined prompt as the single argument to predict
    return bedrock_llm.predict(combined_prompt)


def run_prompts(prompts):
    results = []
    for prompt in prompts:
        response = do_query(prompt)
        results.append(response)
        time.sleep(0.1)
    return results
