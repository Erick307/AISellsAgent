import yaml
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate


PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> ChatPromptTemplate:
    """
    Loads a ChatPromptTemplate from a YAML file in the prompts/ folder.

    Expected YAML format:
        messages:
          - role: system
            content: "You are a sales assistant..."
          - role: placeholder
            variable: "{conversation_history}"
          - role: human
            content: "{customer_message}"
    """
    path = PROMPTS_DIR / f"{name}.yaml"
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    messages = []
    for msg in data["messages"]:
        role = msg["role"]
        if role == "placeholder":
            messages.append((role, msg["variable"]))
        else:
            messages.append((role, msg["content"]))

    return ChatPromptTemplate.from_messages(messages)
