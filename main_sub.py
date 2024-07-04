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
    conditions = {
    'V201200': {
            (1, 2, 3): "liberal",
            4: "moderate",
            (5, 6, 7): "conservative"
    },
    'V201231x': {
            (1, 2, 3): "democrat",
            4: "independent",
            (5, 6, 7): "republican"
    },
    'V201507x': {
            range(18, 31): "18~30",
            range(31, 46): "31~45",
            range(46, 61): "46~60",
            range(61, 200): "over_60"  # Assuming 200 as a reasonable upper age limit
    },
    'V201600': {
            1: "man",
            2: "woman"
    },
    'V202406': {
            (1, 2): "interest",
            (3, 4): "no_interest"
    },
    'V201549x': {1: 'white', 2: 'black', 3: 'asian', 4: 'native American', 5: 'hispanic'},
    'V202022': {
            1: 'like_to_discuss',
            2: 'never_discuss'
        },
    'V201452':  {1: "attend_church", 2: "do_not_attend"}
}
if sys.argv[1] == '2024':
    from anes2024 import *
    conditions = {
    'ideo5': {
            (1, 2): "liberal",
            3: "moderate",
            (4, 5): "conservative"
    },
    'pid7': {
            (1, 2, 3): "democrat",
            4: "independent",
            (5, 6, 7): "republican"
    },
    'age': {
            range(18, 31): "18~30",
            range(31, 46): "31~45",
            range(46, 61): "46~60",
            range(61, 200): "over_60"  # Assuming 200 as a reasonable upper age limit
    },
    'gender': {
            1: "man",
            2: "woman"
    },
    'newsint': {
            (1, 2): "interest",
            (3, 4): "no_interest"
    },
    'race': {1: 'white', 2: 'black', 3: 'asian', 4: 'native American', 5: 'hispanic'},
    'poldisc_intldisc': {
        (1,2): 'never_discuss',
        (3, 4, 5): 'like_to_discuss'
        },
    'pew_churatd':  {
        (1, 2, 3): "attend_church", 
        (4, 5, 6): "do_not_attend"
                     }
}

if sys.argv[2] == 'gpt':
    from common_gpt import *
if sys.argv[2] == 'llama':
    from common_llama2 import *
if sys.argv[2] == 'claude':
    from common_claude3 import *


foi_keys = fields_of_interest.keys()
model_name = model_name

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

def filter_dataframe(df, value_set, column):
    # 각 value_set에 대해서 단일 조건 필터링을 수행합니다.
    if isinstance(value_set, tuple):
        mask = df[column].isin(value_set)
    elif isinstance(value_set, range):
        mask = df[column].between(value_set.start, value_set.stop - 1)
    else:
        mask = (df[column] == value_set)
    return df[mask]

anesdf = pd.read_csv(ANES_FN, sep=',', encoding='utf-8', low_memory=False)

def run_simulation():
    
    for column, value_sets in conditions.items():
        for value_set, label in value_sets.items():
            # 현재 필터링 조건에 대한 설명을 출력합니다.
            if isinstance(value_set, tuple) or isinstance(value_set, range):
                value_set_description = f"{' '.join(map(str, value_set))}"
            else:
                value_set_description = str(value_set)
            print(f"Running experiment for {column} with condition: {label} for values {value_set_description}")
            
            # 단일 조건으로 필터링된 데이터프레임을 생성합니다.
            filtered_df = filter_dataframe(anesdf, value_set, column)
            
            # 각 조건에 대한 full_results 리스트를 초기화합니다.
            full_results = []

            # 필터링된 데이터프레임에 대한 처리를 수행합니다.
            distributions = compute_demographic_distribution(filtered_df)

            MAX_RETRIES = 5
            for idx in tqdm(range(len(filtered_df))):

                fake_person = generate_fake_respondent(distributions)
                backstory = gen_backstory_from_fake_person(fake_person)
                user_prompt = query
                full_prompt = generate_query_with_backstory(backstory, user_prompt)
                
                fake_id = f"fake_{idx}"  # 가짜 응답자의 ID 생성

                retries = 0
                success = False
                while not success and retries < MAX_RETRIES:
                    try:
                        response = do_query(backstory, user_prompt)
                        result_entry = (fake_id, *fake_person.values(), full_prompt, response)
                        full_results.append(result_entry)
                        success = True  # 성공적으로 API 호출이 완료되면 success를 True로 설정
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        time.sleep(10)  # an underlying Exception, likely raised within httpx.
                    retries += 1  # 재시도 횟수 증가

                if not success:
                    print(f"Failed to get a response after {MAX_RETRIES} retries for respondent {fake_id}.")

            # 결과를 저장합니다.
            #pickle.dump(full_results, open(OUTPUT_FN, "wb"))

            columns = ["ID", *fields_of_interest.keys(), "Prompt", "Response"]
            df_results = pd.DataFrame(full_results, columns=columns)
            output_csv = f"output_{model_name}_{column}_{label}.csv"  # 각 조건에 대해 고유한 파일 이름을 생성합니다.
            unique_filepath = create_unique_filename(output_csv)

            # DataFrame을 새로운 파일 경로에 저장
            df_results.to_csv(unique_filepath, index=False)
            print(f"Results saved to {unique_filepath}")

# 실행 횟수 지정
num_simulations = 5

for _ in range(num_simulations):
    run_simulation()
