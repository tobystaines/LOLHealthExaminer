# main.py

import argparse
import json
import logging
import os
from pathlib import Path

from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage

import prompts
import schema
import utils

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING"))
log = logging.getLogger(__name__)

FOLLOW_UP_QUESTIONS_LIBRARY = utils.load_json(
    Path(__file__).parent / "questions_library.json"
)

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


def process_file(input_file_path: str, output_file_path: str) -> None:
    input_data = utils.extract_data_from_file(input_file_path)

    log.info("Extracting key patient information from record")
    response = prompt_model(prompts.get_key_details_message(input_data))
    key_patient_details = prompts.key_details_parser.invoke(response)

    for medication in key_patient_details.current_medications:
        if not medication.side_effects or any(
            na in utils.strip_punctuation_lower(medication.side_effects[0])
            for na in ["na", "notavailable", "none", "notspecified"]
        ):
            log.info(f"Side effects missing for {medication.name}. Re-querying model")
            response = prompt_model(prompts.get_side_effects_message(medication))
            updated_medication = prompts.medication_parser.invoke(response)
            medication.side_effects = updated_medication.side_effects

    try:
        log.info(
            f"Looking for follow up questions for {key_patient_details.chief_complaint}"
        )
        follow_up_questions = next(
            questions
            for complaint, questions in FOLLOW_UP_QUESTIONS_LIBRARY.items()
            if complaint in key_patient_details.chief_complaint
        )
        follow_up_questions = schema.FollowUpQuestions(questions=follow_up_questions)
        log.info(
            f"Found follow up questions for {key_patient_details.chief_complaint} in library"
        )
    except StopIteration:
        log.info(
            f"Failed to find follow up questions for {key_patient_details.chief_complaint} in library. Querying model for questions"
        )
        follow_up_questions = get_follow_up_questions_from_model(
            key_patient_details.chief_complaint
        )

    log.info(f"Asking follow up questions")
    response = prompt_model(
        prompts.get_follow_up_questions_message(follow_up_questions)
    )
    follow_up_answers = prompts.follow_up_answer_parser.invoke(response)

    log.info("Asking for final decision")
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

    log.info(
        f"Results saved to {output_file_path}. Proposed treatment plan acceptable: {results.final_decision.treatment_plan_appropriate}"
    )


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
