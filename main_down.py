import sys
import pandas as pd
import pickle
from tqdm import tqdm
from transformers import GPT2Tokenizer
import random
import numpy as np
import os

if sys.argv[1] == '2020':
    from anes2020 import *
if sys.argv[1] == '2024':
    from anes2024 import *

if sys.argv[2] == 'gpt':
    from common_gpt import *
if sys.argv[2] == 'llama':
    from common_llama2 import *
if sys.argv[2] == 'claude':
    from common_claude3 import *


foi_keys = fields_of_interest.keys()
anesdf = pd.read_csv(ANES_FN, sep=',', encoding='utf-8', low_memory=False)

def create_unique_filename(filepath):
    basename, extension = os.path.splitext(filepath)
    counter = 1

    new_filepath = filepath
    while os.path.exists(new_filepath):
        new_filepath = f"{basename}_{counter}{extension}"
        counter += 1

    return new_filepath


def compute_demographic_distribution(df):
    distributions = {}
    for key in fields_of_interest.keys():
        value_counts = anesdf[key].value_counts(normalize=True).to_dict()
        distributions[key] = value_counts
    return distributions

def generate_fake_respondent(distributions):
    fake_respondent = {}
    for k, v in distributions.items():
        fake_respondent[k] = np.random.choice(list(v.keys()), p=list(v.values()))
    return fake_respondent

def gen_backstory_from_fake_person(fake_person):
    backstory = ""
    for k, anes_val in fake_person.items():
        if anes_val < 0:  # 음수 값은 backstory에 포함되지 않습니다.
            continue
        elem_template = fields_of_interest[k]['template']
        elem_map = fields_of_interest[k]['valmap']
        if len(elem_map) == 0:
            backstory += " " + elem_template.replace('XXX', str(anes_val))
        elif anes_val in elem_map:
            backstory += " " + elem_template.replace('XXX', elem_map[anes_val])
    if backstory[0] == ' ':
        backstory = backstory[1:]
    return backstory

def generate_query_with_backstory(backstory, question):
    return f"{backstory}. {question}"

def run_simulation(num_entries):
    

    # anesdf = pd.read_csv(ANES_FN, sep=SEP, encoding='latin-1', low_memory=False)
    full_results = []
    distributions = compute_demographic_distribution(anesdf)

    fake_results = []

    # iteration 횟수 지정
    MAX_RETRIES = 5
    for idx in tqdm(range(num_entries)):

        fake_person = generate_fake_respondent(distributions)
        backstory = gen_backstory_from_fake_person(fake_person)
        system_prompt = system_message
        user_prompt = backstory + query
        full_prompt = generate_query_with_backstory(system_prompt, user_prompt)
        
        fake_id = f"fake_{idx}"  # 가짜 응답자의 ID 생성

        retries = 0
        success = False
        while not success and retries < MAX_RETRIES:
            try:
                response = do_query(system_prompt, user_prompt)
                result_entry = (fake_id, *fake_person.values(), full_prompt, response)
                full_results.append(result_entry)
                # print(response)
                success = True  # 성공적으로 API 호출이 완료되면 success를 True로 설정
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(10)
            retries += 1  # 재시도 횟수 증가

        if not success:
            print(f"Failed to get a response after {MAX_RETRIES} retries for respondent {fake_id}.")


    # 결과를 저장합니다.
    # pickle.dump(full_results, open(OUTPUT_FN, "wb"))

    columns = ["ID", *fields_of_interest.keys(), "Prompt", "Response"]
    df_results = pd.DataFrame(full_results, columns=columns)

    # 원래 파일 경로
    output_csv = f"output_{model_name}_{num_entries}.csv"  # 각 조건에 대해 고유한 파일 이름을 생성합니다.
    original_filepath = output_csv
    # 중복을 확인하고 새로운 파일명 생성
    unique_filepath = create_unique_filename(original_filepath)

    # DataFrame을 새로운 파일 경로에 저장
    df_results.to_csv(unique_filepath, index=False)

    print(f"Results saved to {unique_filepath}")
    
# 실행 횟수 지정
percentages = [90, 80, 70, 60, 50, 40, 30, 20, 10] + list(range(9, 0, -1))
num_simulations = 5  # 각 비율에 대한 시뮬레이션 횟수

for percent in percentages:
    num_entries = int(len(anesdf) * (percent / 100))
    for simulation in range(num_simulations):
        print(f"Running simulation {simulation+1}/{num_simulations} for {percent}% of data: {num_entries} entries")
        run_simulation(num_entries)
