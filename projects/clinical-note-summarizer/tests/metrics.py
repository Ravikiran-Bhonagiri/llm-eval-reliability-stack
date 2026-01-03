from deepeval.metrics import GEval, FaithfulnessMetric
from deepeval.test_case import LLMTestCaseParams

# Custom Metric: Critical Entity Retention
critical_entity_metric = GEval(
    name="Critical Entity Retention",
    criteria="Check if ALL medications, allergies, and diagnoses in the 'Input' are present in the 'Actual Output'.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    strict_mode=True # Fail if score < 1.0 (Zero Tolerance)
)

# Standard Metric: Faithfulness
# verifies that claims in the summary are supported by the input text.
faithfulness_metric = FaithfulnessMetric(
    threshold=0.9,
    include_reasoning=True
)
