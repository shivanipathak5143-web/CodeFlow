"""Run:  python -m app.check_llm     It tells you exactly what is wrong with your LLM setup."""
import httpx

from . import config, llm


def main():
    provider = config.LLM_PROVIDER
    print(f"Provider: {provider}   Model: {llm._model()}")
    if provider == "openai":
        print(f"Base URL: {config.OPENAI_BASE_URL}")
        if not config.OPENAI_API_KEY:
            print("\nPROBLEM: OPENAI_API_KEY is empty, so your .env was not found or not read.\n"
                  "  - It must be named exactly .env (not .env.txt) and sit in the project root.\n"
                  "  - It needs one line like: OPENAI_API_KEY=gsk_...\n"
                  "  - Restart the server after creating it.")
            return
        print(f"Key found (starts with {config.OPENAI_API_KEY[:4]}..., {len(config.OPENAI_API_KEY)} chars)")
        try:
            r = httpx.get(config.OPENAI_BASE_URL.rstrip("/") + "/models", timeout=30,
                          headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"})
        except httpx.HTTPError as e:
            print(f"\nPROBLEM: cannot reach the server: {e}\n  Check your internet / firewall / proxy.")
            return
        if r.status_code in (401, 403):
            print("\nPROBLEM: the provider rejected your key. Make a new key and paste it into .env.")
            return
        if r.status_code == 200:
            ids = sorted(m.get("id", "") for m in r.json().get("data", []))
            print(f"\n{len(ids)} models are available to your key:")
            for i in ids:
                print("  ", i)
            if ids and config.OPENAI_MODEL not in ids:
                print(f"\nPROBLEM: model '{config.OPENAI_MODEL}' is not in that list.\n"
                      "  Add OPENAI_MODEL=<one name from the list above> to .env and restart.")
                return
    print("\nTest call...")
    try:
        print("SUCCESS. Model replied:", llm._call("Reply with the single word: ok").strip())
    except llm.LLMError as e:
        print("\nPROBLEM:", e)
        if "429" in str(e):
            print("  Rate limit: wait a minute and retry. Retries are now automatic in the app.")


if __name__ == "__main__":
    main()