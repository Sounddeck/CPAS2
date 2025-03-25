import requests
import json

def chat_with_ollama(message):
    """Send a message to Ollama and return the response"""
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2:latest",
                "messages": [{"role": "user", "content": message}],
                "stream": False
            }
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            # Try to parse the JSON response
            try:
                result = response.json()
                print("Full response:", json.dumps(result, indent=2))
                return result.get("message", {}).get("content", "No content received")
            except json.JSONDecodeError:
                print("Raw response (not JSON):", response.text[:500])
                return "Error: Could not parse response"
        else:
            print(f"Error response: {response.text}")
            return f"Error: {response.status_code}"
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: {str(e)}"

# Simple text interface
print("Simple Ollama Chat (type \"exit\" to quit)")
while True:
    user_input = input("> ")
    if user_input.lower() in ["exit", "quit"]:
        break
    
    print("
Thinking...")
    response = chat_with_ollama(user_input)
    print("
Response:", response, "
")

