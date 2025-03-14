import csv
import json

from apyori import apriori
from dotenv import load_dotenv
import os

import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules

load_dotenv()
base_dir = os.getenv('BASE_PATH', '/opt/render/project/src/')

path_models = os.path.join(base_dir, 'data', 'models.json')
path_model_details = os.path.join(base_dir, 'data/model_details.json')


def load_existing_data(file_path):
    """Load existing data from a JSON file if it exists, else return an empty list"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


data = load_existing_data(path_model_details)


def suggest_similar(current_girl_id, exclude_ids, liked_ids):
    global data
    # Logic for finding similar girls using Apriori
    train_data = [liked_ids]
    with open(base_dir + 'data/train.txt', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            train_data.append([item.strip() for item in line])

    # print(train_data)
    rule_list_sorted = suggestion_apriori(train_data)
    # rule_list_sorted = suggestion_fp_growth(train_data)

    # Find the most similar girl based on the current girl's ID
    recommended_girl = None
    selected_confidence = None
    for rule in rule_list_sorted:
        antecedent, consequent, confidence = rule
        if str(current_girl_id) in antecedent:
            # Look for the next girl that is not in the exclude list
            for girl_id in consequent:
                if girl_id not in exclude_ids:
                    recommended_girl = girl_id
                    selected_confidence = confidence
                    break
        if recommended_girl:
            print(f'recommended_girl {recommended_girl}')
            break

    if recommended_girl:
        return {
            'model': next((item for item in data if int(item['id']) == int(recommended_girl)), None),
            'suggestion': {
                'rule': 'Apriori',
                'confidence': selected_confidence,
            }
        }
    else:
        return {
            'model': None,
            'suggestion': None
        }


def suggest_random(excluded_ids=None):
    global data
    # Return a random girl
    import random
    filtered_data = data

    if excluded_ids is not None:
        filtered_data = [girl for girl in data if girl['id'] not in excluded_ids]

    if not filtered_data:
        return None

    return random.choice(filtered_data)


def get_detail(girl_id):
    global data

    return next((item for item in data if item['id'] == girl_id), None)


def suggestion_apriori(train_data):
    rules = apriori(train_data, min_support=0.01, min_confidence=0.05, min_lift=1)
    results = list(rules)

    print(f'Number of rules found: {len(results)}')

    # Prepare the rules list
    rule_list = []

    # Loop through each rule
    for rule in results:
        for item in rule.ordered_statistics:
            if len(item.items_base) > 0 and len(item.items_add) > 0:
                antecedent = list(item.items_base)
                consequent = list(item.items_add)
                confidence = item.confidence
                rule_list.append((antecedent, consequent, confidence))

    # Sort the rules by confidence in descending order
    return sorted(rule_list, key=lambda x: x[2], reverse=True)


def suggestion_fp_growth(train_data):
    """
    Generate association rules using FP-Growth algorithm.

    Args:
        train_data (list of list): The transactional dataset where each sublist contains item IDs.

    Returns:
        list of tuple: A sorted list of rules with antecedent, consequent, and confidence.
    """
    # Encode the transaction data into a one-hot DataFrame
    te = TransactionEncoder()
    te_ary = te.fit(train_data).transform(train_data)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    # Generate frequent item sets
    frequent_item_sets = fpgrowth(df_encoded, min_support=0.05, use_colnames=True)

    # Ensure compatibility with association_rules function
    frequent_item_sets["num_itemsets"] = frequent_item_sets['support'] * len(train_data)

    # Generate association rules
    rules = association_rules(
        frequent_item_sets,
        metric="confidence",
        min_threshold=0.1
    )

    print(f"Number of rules found: {len(rules)}")

    # Prepare the rules list in the desired format
    rule_list = []
    for _, row in rules.iterrows():
        antecedent = list(row["antecedents"])
        consequent = list(row["consequents"])
        confidence = row["confidence"]
        rule_list.append((antecedent, consequent, confidence))

    # Sort rules by confidence in descending order
    return sorted(rule_list, key=lambda x: x[2], reverse=True)
