import os
from google import genai


def main():
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("NO_API_KEY")
        return
    client = genai.Client(api_key=api_key)
    try:
        models = client.models.list()
    except Exception as e:
        print("LIST_ERROR", repr(e))
        return
    for m in models:
        name = getattr(m, "name", "")
        methods = getattr(m, "supported_generation_methods", [])
        if isinstance(methods, (list, tuple)):
            caps = ",".join(methods)
        else:
            caps = str(methods)
        print(f"{name}|{caps}")


if __name__ == "__main__":
    main()