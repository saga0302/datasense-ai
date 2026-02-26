import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ask_claude(prompt: str, system: str = "You are a senior data reliability engineer.") -> str:
    """
    Send a prompt to Claude and get a response back.
    This is the single function all 5 nodes will use to talk to Claude.
    """
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=system,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text