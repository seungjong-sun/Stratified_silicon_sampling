import anthropic
import numpy as np
import time
import json
import boto3
import sys
from openai import OpenAI
import openai

# 교은 key
my_api_key = ""
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key = my_api_key,
    timeout=20.0,

)

# model ID
# anthropic.claude-3-haiku-20240307-v1:0
# anthropic.claude-3-sonnet-20240229-v1:0
# anthropic.claude-3-opus-20240229-v1:0


model_id = ""
if sys.argv[3] == 'haiku':
    model_id="anthropic.claude-3-haiku-20240307-v1:0"
    model_name = "claude_haiku"
if sys.argv[3] == 'sonnet':
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
    model_name = "claude_sonnet"
if sys.argv[3] == 'opus':
    model_id="anthropic.claude-3-opus-20240229-v1:0"
    model_name = "claude_opus"


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

# model ID
# anthropic.claude-3-haiku-20240307-v1:0
# anthropic.claude-3-sonnet-20240229-v1:0
# anthropic.claude-3-opus-20240229-v1:0



def do_query(system_prompt, user_prompt, max_tokens=512, model_id=model_id):
    
    body=json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content":user_prompt}
            ]
        }  
    )  

    bedrock_runtime = boto3.client(service_name='bedrock-runtime')

    response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())
    print(response_body['content'][0]['text'])
    messages_sd = [
        {"role": "system", "content": """You are a stance detector. Extract which presidential candidate the given sentence is intended to elect. Answer only with the candidate's name or 'Neither'."""}, 
        {"role": "user", "content": response_body['content'][0]['text']}
        ]
    response_sd = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages_sd,
        max_tokens=3,
    )

   
    return response_sd.choices[0].message.content







def run_prompts(prompts, engine="anthropic.claude-3-haiku-20240307-v1:0"):
    results = []
    for prompt in prompts:
        response = do_query(prompt, max_tokens=50, engine=engine)
        results.append(response)
        time.sleep(0.1)
    return results
