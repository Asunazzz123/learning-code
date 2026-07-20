import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def main(prompt: str) -> None:
    env_path = Path(__file__).with_name(".env")
    load_dotenv(env_path)

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    request_body = {
        "model": os.getenv("OPENAI_MODEL"),
        "messages": [{"role": "user", "content": prompt}],
    }

    print("\n===== OpenAI JSON Request =====")
    print(json.dumps(request_body, ensure_ascii=False, indent=2))
    

    response = client.chat.completions.create(**request_body)

    content = response.choices[0].message.content
    print(content or "[模型返回了空内容]")


if __name__ == "__main__":
    prompt = input("Prompt: ")
    main(prompt)
