# ================================================================
#  external_llm_api.py
#  External LLM API Wrapper (Mock + Real API Support)
# ================================================================

import os
import requests


# ================================================================
# 1. Load API Key
# ================================================================

API_KEY = os.getenv("LLM_API_KEY")


def get_api_key() -> str:
    """
    Returns the API key.
    If not found in environment variables, the user is asked to input it.
    """
    global API_KEY

    if not API_KEY:
        print("لم يتم العثور على مفتاح API في متغيرات البيئة.")
        print("يرجى إدخال مفتاح API الخاص بك (مثل OpenAI API Key):")

        API_KEY = input().strip()

        if not API_KEY:
            raise ValueError("يجب إدخال مفتاح API صالح للتشغيل.")

    return API_KEY


# ================================================================
# 2. Main LLM Call Handler
# ================================================================

def llm_call(prompt: str) -> str:
    """
    Executes a call to a real LLM API (default: OpenAI ChatCompletion API).
    Falls back to a mock mode when no API key is provided.
    """

    api_key = get_api_key()

    # ------------------------------------------------------------
    # Mock Mode (for offline / no-key testing)
    # ------------------------------------------------------------
    if api_key == "DUMMY_KEY_FOR_TESTING_ONLY" or not api_key:
        print("[تحذير] استخدام وضع تجريبي (mock) – أدخل مفتاح API حقيقي للنتائج الفعلية.")

        if "score" in prompt.lower():
            return "0.85"

        return f"[MOCK OUTPUT] Action executed: {prompt[:40]}..."

    # ------------------------------------------------------------
    # Real API Call (OpenAI example)
    # ------------------------------------------------------------
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"[ERROR] فشل الاتصال بالـ API: {str(e)}. تأكد من المفتاح أو الاتصال بالإنترنت."


# ================================================================
# 3. Direct execution for quick testing
# ================================================================

if __name__ == "__main__":
    test_prompt = "What is the capital of France?"
    print(llm_call(test_prompt))
