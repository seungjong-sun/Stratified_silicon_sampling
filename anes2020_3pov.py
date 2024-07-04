import sys

if sys.argv[2] == 'gpt':
    from common_gpt import *
if sys.argv[2] == 'llama':
    from common_llama2 import *
if sys.argv[2] == 'claude':
    from common_claude3 import *
from anes_common import *

SEP=','
ID_COL = "V200001"
VOTE_COL = "V202110x"  # 1-Biden, 2-Trump, 3-Jorgensen, 4-Hawkins
K1 = "trump"
K2 = "biden"
tok_sets = {
    "trump": gen_variants([ "donald", "trump", "republican", "conservative"]),
    "biden": gen_variants([ "joe", "joseph", "biden", "democrat", "democratic", "liberal"])
}
system_message = "Complete the given sentences according to the context."
# system_message = "Complete the given sentences according to the context. Answer with the candidate's name."

# system_message = "Complete the given sentences according to the context. Answer in two words." # for Claude 3

query = "In the 2020 presidential election, Donald Trump is the Republican candidate, "
query += "and Joe Biden is the Democratic candidate, and yyy voted for"
ANES_FN = './2020 ANES_test.csv'

fields_of_interest = {
    'V201549x': {
        "template": "Racially, yyy is XXX.",
        "valmap": {1: 'white', 2: 'black', 3: 'asian', 4: 'native American', 5: 'hispanic'}
    },
    'V202022': {
        "template": "YYY XXX",
        "valmap": {
            1: 'like to discuss politics with my family and friends.',
            2: 'never discuss politics with my family or friends.'
        }
    },
    'V201200': {
        "template": "Ideologically, yyy is XXX.",
        "valmap": {
            1: "extremely liberal",
            2: "liberal",
            3: "slightly liberal",
            4: "moderate",
            5: "slightly conservative",
            6: "conservative",
            7: "extremely conservative"
        }
    },
    'V201231x': {
        "template": "Politically, yyy is XXX.",
        "valmap": {
            1: "a strong democrat",
            2: "a weak Democrat",
            3: "an independent who leans Democratic",
            4: "an independent",
            5: "an independent who leans Republican",
            6: "a weak Republican",
            7: "a strong Republican"
        }
    },
    'V201452': {
        "template": "YYY XXX.",
        "valmap": {1: "attends church", 2: "does not attend church"}
    },
    'V201507x': {
        "template": "YYY is XXX years old.",
        "valmap": {}
    },
    'V201600': {
        "template": "YYY is a XXX.",
        "valmap": {1: "man", 2: "woman"}
    },
    'V202406': {
        "template": "YYY is XXX interested in politics.",
        "valmap": {1: "very", 2: "somewhat", 3: "not very", 4: "not at all"}
    }
}
