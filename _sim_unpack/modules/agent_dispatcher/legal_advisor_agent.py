# legal_advisor_agent.py
def respond(user_input: str) -> str:
    response = ["📜 Legal Advisor Activated"]
    if "contract" in user_input.lower():
        response.append(
            "\n📄 Contract Review:\n- I can help identify common risk clauses.\n- Need the text or a summary of the contract to proceed."
        )
    if "privacy" in user_input.lower():
        response.append(
            "\n🔐 Privacy Guidance:\n- GDPR and CCPA compliance checks available.\n- Be sure to disclose cookie usage and data collection policies."
        )
    if "license" in user_input.lower():
        response.append(
            "\n📘 Licensing Help:\n- I can help you understand open-source software licenses (e.g., MIT, GPL)."
        )
    if len(response) == 1:
        response.append(
            "\n🤖 Please specify if this is about contracts, privacy, or licensing."
        )
    return "\n".join(response)
