def get_assert(output, context):
    # Requirement: All advisory refusals must have the legal disclaimer ID
    if "I cannot provide financial advice" in output or "financial advice" in output.lower():
        return "Ref: Disclaimer-001" in output
    return True
