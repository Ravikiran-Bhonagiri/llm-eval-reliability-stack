import pytest
import json
import logging
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from src.summarizer import summarize_note
from tests.metrics import critical_entity_metric, faithfulness_metric

def load_cases():
    with open("tests/data/patient_notes.json", "r") as f:
        return json.load(f)

@pytest.mark.parametrize("case", load_cases())
def test_clinical_summary_safety(case):
    input_text = case["input"]
    
    # 1. Run the Summarizer
    actual_summary = summarize_note(input_text)
    
    print(f"\nGenerared Summary: {actual_summary}")

    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_summary
    )

    # 2. Assert Safety
    # We strip empty lines to ensure the print output is clean
    assert_test(test_case, [critical_entity_metric, faithfulness_metric])
