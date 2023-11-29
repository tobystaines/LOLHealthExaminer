from typing import List

from langchain.pydantic_v1 import BaseModel, Field, validator

from utils import strip_punctuation_lower


class Medication(BaseModel):
    name: str
    dosage: str
    side_effects: List[str]

    # @validator("side_effects")
    # def side_effects_not_empty(cls, field):
    #     if not field or strip_punctuation_lower(field[0]) in ["na", "notavailable"]:
    #         raise ValueError("Missing side effects")
    #     return field


class KeyPatientDetails(BaseModel):
    chielf_complaint: str
    proposed_treatment_plan: List[str]
    allergies: List[str]
    current_medications: List[Medication]


class FollowUpQuestion(BaseModel):
    question: str

    # @validator("question")
    # def question_ends_with_question_mark(cls, field):
    #     if field[-1] != "?":
    #         raise ValueError("Badly formed question!")
    #     return field


class FollowUpQuestions(BaseModel):
    questions: List[str]


class FollowUpAnswer(BaseModel):
    question: str
    answer: str
    confidence: int
    justification: str


class FollowUpAnswers(BaseModel):
    answers: List[FollowUpAnswer]


class FinalDecision(BaseModel):
    treatment_plan_appropriate: bool
    justification: str


class Results(BaseModel):
    key_patient_details: KeyPatientDetails
    follow_up_questions: FollowUpQuestions
    follow_up_answers: FollowUpAnswers
    final_decision: FinalDecision
