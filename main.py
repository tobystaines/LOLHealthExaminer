# main.py

import json
import argparse
from typing import Dict

from openai import OpenAI


def clean(data: str) -> str:
    return data


def query_openai(patient_data: str) -> Dict:
    prompt = f"""
        Below is a patient record (not real). Can you tell me:
        a. Patient’s chief complaint
        b. Treatment plan the doctor is suggesting
        c. A list of allergies the patient has
        d. A list of medications the patient is taking (including dosage), with any known side-effects (side-effects may not be listed in the patient record but you should list any that you are aware of realting to the medications you identify)

        return the answers in the structure {{
            "a": "complaint",
            "b": "treatment plan",
            "c": [
                "first allergy",
                "second allergey",
                etc.
            ],
            "d": [
                "medication 1": {{
                    "name": "The name of the medication",
                    "dosage": "The patient's dosage (if known)",
                    "side-effects": ["side-effect 1", side-effect 2", etc.]
                    }},
                "medication2": {{
                    "name": "The name of the medication",
                    "dosage": "The patient's dosage (if known)",
                    "side-effects": ["side-effect 1", side-effect 2", etc.]
                    }},
                etc.
            ]
        }}. It should be a string which can be parsed as valid json.
        Here is the patient record:
        {patient_data}
    """

    client = OpenAI()
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a medical expert. You give conscise, precise answers to medical questions."},
        {"role": "user", "content": prompt}
    ]
    )

    results = completion.choices[0].message
    r_dict = json.loads(results.content)

    for details in r_dict["d"].values():
        if not details["side-effects"]:
            prompt = f"What are the known side-effects of {details['name']}"
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical expert. You give conscise, precise answers to medical questions."},
                    {"role": "user", "content": prompt}
                ]
            )

            results = completion.choices[0].message
            details["side-effects"] = results.content

    return r_dict


def process_file(input_file, output_file):

    with open(input_file, 'r') as f:
        input_data = f.read()

    cleaned_data = clean(input_data)
    results = query_openai(cleaned_data)

    output_data = {
        'input': input_data,
        'output': results.content
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a medical record file and save JSON output.")
    parser.add_argument("input_file", help="Path to the input medical record file.")
    parser.add_argument("output_file", help="Path to the output JSON file.")
    args = parser.parse_args()

    process_file(args.input_file, args.output_file)
