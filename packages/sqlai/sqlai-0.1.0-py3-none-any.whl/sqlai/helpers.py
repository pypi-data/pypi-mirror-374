import sys
from pathlib import Path

import google.generativeai as genai

from .config import read_config


def read_sql_file(file_path: str) -> str:
    """Read the content of a SQL file and return it as a string."""
    path = Path(file_path)

    if path.suffix.lower() != ".sql":
        # raise ValueError(f"Not a .sql file: {file_path}")
        print("⚠️   Only .sql files are allowed")
        exit(1)

    elif not path.exists():
        print(f"⚠️   File not found: {file_path}")
        exit(1)

    else:
        return path.read_text(encoding="utf-8")


def ask_gemini(sql_query: str, question: str) -> str:
    """Send SQL query and a question to Gemini API and return the response text."""

    config = read_config()
    if config:
        ai_provider = config["ai_provider"]  # not used yet
        api_key = config["api_key"]
        model = config["model"]

    # Configure with API key
    genai.configure(api_key=api_key)

    # Pick a model (flash is fast, pro is better quality)
    selected_model = genai.GenerativeModel(model)

    # Build the prompt
    prompt = f"SQL Query:\n{sql_query}\n\nQuestion:\n{question}"

    # Send to Gemini
    response = selected_model.generate_content(prompt)

    return response.text


def show_actions(sql_file):
    actions = ["[1] explain", "[2] validate", "[3] improve"]
    for action in actions:
        print(action)

    error_message = (
        f"⚠️   Invalid input. Please enter a number between 1 and {len(actions)}."
    )

    try:
        choice = int(input("Select an action: ").strip())

        if choice not in list(range(1, len(actions) + 1)):
            print(error_message)
            sys.exit(0)

    except ValueError:
        print(error_message)
        sys.exit(0)

    if choice == 1:
        response = ask_gemini(
            sql_query=sql_file,
            question="Explain what the SQL query does and do not exceed 150 characters",
        )
        print(response)
    elif choice == 2:
        response = ask_gemini(
            sql_query=sql_file,
            question="Check if the SQL query is generally valid. If yes, just return 'OK', if not, provide a list of the issues",
        )
        if response == "OK":
            print("✅ OK")
        else:
            print(f"⚠️ {response}")
    elif choice == 3:
        print("coming soon")
