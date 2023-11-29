# main.py

import argparse
import json
from pathlib import Path
from typing import List

from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage

import prompts
import schema
import utils

MODEL = ChatOpenAI(
    model_name="gpt-3.5-turbo-1106",
    model_kwargs={"response_format": {"type": "json_object"}},
)
MESSAGES = [prompts.get_system_message()]


def prompt_model(prompt: HumanMessage) -> AIMessage:
    MESSAGES.append(prompt)
    response = MODEL(MESSAGES)
    MESSAGES.append(response)
    return response


def get_follow_up_questions_from_model(
    cheif_complaint: str,
) -> schema.FollowUpQuestions:
    response = prompt_model(
        prompts.get_follow_up_questions_request_message(cheif_complaint)
    )
    follow_up_questions = prompts.follow_up_question_parser.invoke(response)
    return follow_up_questions


def process_file(input_file_path, output_file_path):
    input_data = utils.extract_data_from_file(input_file_path)

    response = prompt_model(prompts.get_key_details_message(input_data))
    key_patient_details = prompts.key_details_parser.invoke(response)
    # try:
    #     key_patient_details = prompts.key_details_parser.invoke(key_patient_details)
    # except ValueError as e:
    #     for medication in key_patient_details.content.current_medication:
    #         query_response = prompt_model(prompts.get_side_effects_message(medication))

    follow_up_questions_library = utils.load_json(
        Path(__file__).parent / "questions_library.json"
    )

    try:
        follow_up_questions = next(
            questions
            for complaint, questions in follow_up_questions_library.items()
            if complaint in key_patient_details.chielf_complaint
        )
        follow_up_questions = schema.FollowUpQuestions(questions=follow_up_questions)
    except StopIteration:
        follow_up_questions = get_follow_up_questions_from_model(
            key_patient_details.chielf_complaint
        )

    response = prompt_model(
        prompts.get_follow_up_questions_message(follow_up_questions)
    )
    follow_up_answers = prompts.follow_up_answer_parser.invoke(response)

    response = prompt_model(prompts.get_final_decision_message())
    final_decision = prompts.final_decision_parser.invoke(response)

    results = schema.Results(
        key_patient_details=key_patient_details,
        follow_up_questions=follow_up_questions,
        follow_up_answers=follow_up_answers,
        final_decision=final_decision,
    )

    with open(output_file_path, "w") as f:
        json.dump(results.dict(), f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process a medical record file and save JSON output."
    )
    parser.add_argument(
        "input_file_path", help="Path to the input medical record file."
    )
    parser.add_argument("output_file_path", help="Path to the output JSON file.")
    args = parser.parse_args()

    process_file(args.input_file_path, args.output_file_path)
