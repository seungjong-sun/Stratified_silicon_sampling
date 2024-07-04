import sys
import pandas as pd
import pickle
from tqdm import tqdm
from transformers import GPT2Tokenizer
import random
import numpy as np
import os

if sys.argv[1] == '2020':
    from anes2020_3pov import *
if sys.argv[1] == '2024':
    from anes2024_3pov import *

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
    query_gender = query
    # Check the gender and set the pronoun accordingly
    if sys.argv[1] == '2020':
        if 'V201600' in fake_person:
            if fake_person['V201600'] == 1:
                pronoun_upper = "He"
                pronoun_lower = "he"
            elif fake_person['V201600'] == 2:
                pronoun_upper = "She"
                pronoun_lower = "she"
            else:
                pronoun_upper = "He/She"  # Fallback pronoun if it's not male (1) or female (2)
                pronoun_lower = "he/she"
        else:
            pronoun_upper = "He/She"  # Default pronoun if 'V201600' is not in fake_person
            pronoun_lower = "he/she"
    if sys.argv[1] == '2024':
        if 'gender' in fake_person:
            if fake_person['gender'] == 1:
                pronoun_upper = "He"
                pronoun_lower = "he"
            elif fake_person['gender'] == 2:
                pronoun_upper = "She"
                pronoun_lower = "she"
            else:
                pronoun_upper = "He/She"  # Fallback pronoun if it's not male (1) or female (2)
                pronoun_lower = "he/she"
        else:
            pronoun_upper = "He/She"  # Default pronoun if 'V201600' is not in fake_person
            pronoun_lower = "he/she"
            
    backstory = ""
    for k, anes_val in fake_person.items():
        if anes_val < 0:  # 음수 값은 backstory에 포함되지 않습니다.
            continue
        elem_template = fields_of_interest[k]['template']
        elem_map = fields_of_interest[k]['valmap']
        
        # Replace 'YYY' with the appropriate upper case pronoun and 'yyy' with the lower case pronoun
        elem_template = elem_template.replace("YYY", pronoun_upper).replace("yyy", pronoun_lower)

        if len(elem_map) == 0:
            backstory += " " + elem_template.replace('XXX', str(anes_val))
        elif anes_val in elem_map:
            backstory += " " + elem_template.replace('XXX', elem_map[anes_val])

    # Remove the leading space if it exists
    if backstory and backstory[0] == ' ':
        backstory = backstory[1:]

    # Replace 'YYY' in the query with the appropriate upper case pronoun and 'yyy' with the lower case pronoun
    modified_query = query_gender.replace("YYY", pronoun_upper).replace("yyy", pronoun_lower)
    complete_story = f"{backstory}. {modified_query}"
    
    return complete_story

def generate_query_with_backstory(backstory, question):
    return f"{backstory}. {question}"

def run_simulation():
    

    # anesdf = pd.read_csv(ANES_FN, sep=SEP, encoding='latin-1', low_memory=False)
    full_results = []
    distributions = compute_demographic_distribution(anesdf)

    fake_results = []

    # iteration 횟수 지정
    MAX_RETRIES = 5
    for idx in tqdm(range(len(anesdf))):

        fake_person = generate_fake_respondent(distributions)
        user_prompt = gen_backstory_from_fake_person(fake_person)
        system_prompt = system_message
        full_prompt = generate_query_with_backstory(system_prompt, user_prompt)
        
        fake_id = f"fake_{idx}"  # 가짜 응답자의 ID 생성

        retries = 0
        success = False
        while not success and retries < MAX_RETRIES:
            try:
                response = do_query(system_prompt, user_prompt)
                result_entry = (fake_id, *fake_person.values(), full_prompt, response)
                full_results.append(result_entry)
                # print(full_prompt)
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
    original_filepath = OUTPUT_CSV

    # 중복을 확인하고 새로운 파일명 생성
    unique_filepath = create_unique_filename(original_filepath)

    # DataFrame을 새로운 파일 경로에 저장
    df_results.to_csv(unique_filepath, index=False)
    print(f"Results saved to {unique_filepath}")
    
# 실행 횟수 지정
num_simulations = 5

for _ in range(num_simulations):
    run_simulation()
