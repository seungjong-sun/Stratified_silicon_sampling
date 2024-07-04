import sys

if sys.argv[2] == 'gpt':
    from common_gpt import *
if sys.argv[2] == 'llama':
    from common_llama2 import *
if sys.argv[2] == 'claude':
    from common_claude3 import *
from anes_common import *

SEP=','
ID_COL = "caseid"
VOTE_COL = "vote24dt"  # 1-Trump, 2-Biden, 3-Someone else, 4-not vote
K1 = "trump"
K2 = "biden"
tok_sets = {
    "trump": gen_variants([ "donald", "trump", "republican", "conservative"]),
    "biden": gen_variants([ "joe", "joseph", "biden", "democrat", "democratic", "liberal"])
}
system_message = "Complete the given sentences according to the context."
# system_message = "Complete the given sentences with the candidate's name." # for Claude 3

# query = " If the candidates for 2024 US presidential election are  Donald Trump for the Republicans and Joe Biden for the Democrats,"
# query += " I will vote for"

query = " In the 2024 presidential election, Donald Trump is the Republican candidate, "
query += "and Joe Biden is the Democratic candidate, and yyy will vote for"


ANES_FN = './2024 ANES_selected_num.csv'

fields_of_interest = {
    'race': {
        "template": "Racially, yyy is XXX.",
        "valmap": {1: 'white', 2: 'black', 3: 'hispanic', 4: 'asian', 5: 'native american'}
    },
    
    'ideo5': {
        "template": "Ideologically, yyy is XXX.",
        "valmap": {
            1: "very liberal",
            2: "liberal",
            3: "moderate",
            4: "conservative",
            5: "very conservative"
        }
    },
    'pid7': {
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
    'pew_churatd': {
        "template": "YYY XXX.",
        "valmap": {1: "attends church more than once a week", 
                   2: "attends church once a week",
                   3: "attends church once or twice a month",
                   4: "attends church a few times a year",
                   5: "attends church seldom",
                   6: "does not attend church"}
    },
    'age': {
        "template": "YYY is XXX years old.",
        "valmap": {}
    },
    'gender': {
        "template": "YYY is a XXX.",
        "valmap": {1: "man", 2: "woman"}
    },
    
    'poldisc_intldisc': {
        "template": "YYY XXX discusses politics with my family and friends.",
        "valmap": {
            1: "never",
            2: "rarely",
            3: "occasionally",
            4: "somewhat often",
            5: "very often"
        }
    },
    
    'newsint': {
        "template": "YYY is XXX interested in politics.",
        "valmap": {1: "very", 2: "somewhat", 3: "not very", 4: "not at all"}
    }
}
