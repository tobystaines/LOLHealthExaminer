from langchain.output_parsers import (
    PydanticOutputParser,
    CommaSeparatedListOutputParser,
)
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage

import schema

SYSTEM_ROLE = "You are an expert medical assistant. You give conscise, precise answers to medical questions. Answers must be in valid JSON format."

key_details_parser = PydanticOutputParser(pydantic_object=schema.KeyPatientDetails)
list_parser = CommaSeparatedListOutputParser()
follow_up_question_parser = PydanticOutputParser(
    pydantic_object=schema.FollowUpQuestions
)
follow_up_answer_parser = PydanticOutputParser(pydantic_object=schema.FollowUpAnswers)
final_decision_parser = PydanticOutputParser(pydantic_object=schema.FinalDecision)


def get_system_message():
    return SystemMessage(content=SYSTEM_ROLE)


def get_key_details_message(patient_record: str) -> HumanMessage:
    template = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="""
                {format_instructions}
                Fill in the above data structure with information from this patient record:
                {patient_record}
            """,
            partial_variables={
                "format_instructions": key_details_parser.get_format_instructions(),
            },
            input_variables=["patient_record"],
        )
    )
    return template.format(patient_record=patient_record)


def get_side_effects_message(medication: schema.Medication) -> HumanMessage:
    template = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="""
                {format_instructions}
                Fill in the above data structure with a list of known side effects for the following medication:
                {medication}
            """,
            partial_variables={
                "format_instructions": list_parser.get_format_instructions(),
            },
            input_variables=["medication"],
        )
    )
    return template.format(medication=medication)


def get_follow_up_questions_request_message(chief_complaint: str) -> HumanMessage:
    template = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="""
                {format_instructions}
                Given the chief complaint of {chief_complaint}, and the additional key information you have already identified,
                what follow up questions would you ask about this patient record in order to determine if the doctor's treatment plan is appropriate?
                The questions should be provided in the above specificed format.
            """,
            partial_variables={
                "format_instructions": follow_up_question_parser.get_format_instructions(),
            },
            input_variables=["chief_complaint"],
        )
    )
    return template.format(chief_complaint=chief_complaint)


def get_follow_up_questions_message(follow_up_questions: str) -> HumanMessage:
    template = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="""
                {format_instructions}
                Fill in the above data structure with answers to the following questions.
                Answers should be based on the previously provided patient record and your expert medical knowledge.
                For each answer, justify your reasoning (i.e. provide conclusive evidence) and Provide a confidence score (where 10/10 is very confident).
                If your answer is negative, you should only have high confidence if a negative answer can be determined explicitly from the provided information,
                rather than simply there being a lack of evidence for a positive answer.

                {follow_up_questions}
            """,
            partial_variables={
                "format_instructions": follow_up_answer_parser.get_format_instructions(),
            },
            input_variables=["follow_up_questions"],
        )
    )
    return template.format(follow_up_questions=follow_up_questions)


def get_final_decision_message() -> HumanMessage:
    template = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="""
                {format_instructions}
                Given the patient data, your previous answers, and your expert medical knowledge,
                fill in the above data structure for a final decision as to whether the doctor's
                treatment plan is appropriate or not.
                Your final decision should be True or False, and your justification should make
                reference to the data provided and your answers to the previous questions.
            """,
            partial_variables={
                "format_instructions": final_decision_parser.get_format_instructions(),
            },
            input_variables=[],
        )
    )
    return template.format()
