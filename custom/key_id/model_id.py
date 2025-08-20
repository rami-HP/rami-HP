#!/usr/bin/env python3
import os
from openai import OpenAI

def main():
    token = os.getenv("OPENAI_API_KEY")
    if not token:
        raise RuntimeError("Please set OPENAI_API_KEY as an environment variable or repository secret")

    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-5-chat"

    client = OpenAI(base_url=endpoint, api_key=token)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
        ],
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
    )

    # The response structure may vary depending on the SDK version
    try:
        print(resp.choices[0].message.content)
    except Exception:
        print(resp)

if __name__ == "__main__":
    main()