from utils.claude_client import ask_claude

response = ask_claude("Say hello and tell me you are ready to monitor data pipelines. Keep it to 2 sentences.")

print(response)