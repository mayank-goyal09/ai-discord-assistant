import requests
import json

# Request Ollama to pull mistral
response = requests.post("http://127.0.0.1:11434/api/pull", json={"name": "mistral"})

print("Downloading mistral model...")
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        print(data)

print("\n✅ Mistral downloaded!")

