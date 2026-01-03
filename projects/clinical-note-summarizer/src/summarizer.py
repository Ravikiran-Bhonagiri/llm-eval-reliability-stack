import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def summarize_note(note_text):
    # Robust System Prompt (The "Fixed" Version)
    system_prompt = """You are a Medical Scribe.
STEP 1: Extract all ALLERGIES and MEDICATIONS first.
STEP 2: Summarize the history of present illness.
CRITICAL RULE: Never omit an allergy. If an allergy is listed, bold it in the summary."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": note_text}
        ]
    )
    return response.choices[0].message.content
