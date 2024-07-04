from openai import OpenAI
import openai
import numpy as np
import time
import sys
# 교은 key
my_api_key = ""
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key = my_api_key,
    timeout=20.0,

)

model_id = ""
if sys.argv[3] == '3.5':
    model_id="gpt-3.5-turbo-0125"
    model_name = "gpt3.5"
if sys.argv[3] == '4':
    model_id="gpt-4-0125-preview"
    model_name = "gpt4"


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

def do_query(system_prompt, user_prompt, max_tokens=2, engine=model_id):
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    response = client.chat.completions.create(
        model=engine,
        messages=messages,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def run_prompts(prompts, engine="gpt-4-0125-preview"):
    results = []
    for prompt in prompts:
        response = do_query(prompt, max_tokens=2, engine=engine)
        results.append(response)
        time.sleep(0.1)
    return results
