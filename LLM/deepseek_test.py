import requests
import json

api_url = "http://localhost:8080/v1/chat/completions"

payload = {
    "model": "deepseek-r1-distill-qwen-7b:2",
    "messages": [
        {"role": "system", "content": "Always answer in rhymes."},
        {"role": "user", "content": "What day is it today?"}
    ],
    "temperature": 0.7,
    "max_tokens": 3000
}

headers = {"Content-Type": "application/json"}

response = requests.post(api_url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print("Model Response:", response.json()["choices"][0]["message"]["content"])
else:
    print(f"Error {response.status_code}: {response.text}")
