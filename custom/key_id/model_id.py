import os
import sys
import openai


def get_response(prompt: str, model: str | None = None) -> str:
    """Call OpenAI ChatCompletion and return the assistant reply."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
    openai.api_key = api_key
    model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise


def main():
    prompt = os.getenv("PROMPT", "Hello from repository script (replace this prompt as needed)")
    try:
        output = get_response(prompt)
        print(output)
    except Exception as e:
        print("Request failed:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()