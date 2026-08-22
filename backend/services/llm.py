import os
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")


def ask_llm_stream(prompt: str):
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "stop": ["User:", "\nUser", "Human:", "\nHuman"]
                }
            },
            stream=True,
            timeout=60
        )
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                import json
                chunk = json.loads(data)
                if not chunk.get("done"):
                    yield chunk.get("response", "")
    except requests.exceptions.ConnectionError:
        yield "Ollama is not running."
    except Exception as e:
        yield f"Error: {e}"
