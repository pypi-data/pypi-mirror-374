import subprocess, sys, time, textwrap

# Tự động cài requests nếu chưa có
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

ai_enabled = True

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def loading(seconds=3):
    print(f"{YELLOW}Loading", end="")
    for _ in range(seconds):
        time.sleep(1)
        print(".", end="", flush=True)
    print(RESET + "\n")

def pretty_print(title, content, color=CYAN, width=70):
    lines = textwrap.wrap(content, width=width)
    print(color + "═" * (width + 4))
    print(f"  {title}")
    print("─" * (width + 4))
    for line in lines:
        print("  " + line)
    print("═" * (width + 4) + RESET + "\n")

def ask_ai(message, mode="error"):
    try:
        if mode == "error":
            role_system = (
                "Bạn là trợ lý Termux/Linux. "
                "Luôn phân tích lỗi và trả lời NGẮN GỌN theo format:\n"
                "Nguyên nhân:\n- ...\n\nCách khắc phục:\n1. ...\n2. ..."
            )
            prompt = f"Tôi vừa chạy lệnh trong Termux và gặp lỗi:\n{message}"
        else:
            role_system = "Bạn là một trợ lý AI thân thiện, trả lời ngắn gọn, dễ hiểu và trực tiếp."
            prompt = message

        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": role_system},
                {"role": "user", "content": prompt}
            ]
        }
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        r = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Lỗi khi gọi AI: {e}"

def run_ai_helper():
    global ai_enabled
    print(f"{GREEN} STV AI Helper đã khởi động. Gõ 'exit' để thoát.{RESET}\n")

    while True:
        try:
            cmd = input(f"{GREEN}$ {RESET}").strip()
            if cmd.lower() == "exit":
                break

            if cmd.lower() == "/on":
                ai_enabled = True
                print(f"{GREEN} AI trợ giúp đã BẬT{RESET}\n")
                continue
            if cmd.lower() == "/off":
                ai_enabled = False
                print(f"{RED} AI trợ giúp đã TẮT{RESET}\n")
                continue

            if cmd.startswith("ask "):
                question = cmd[4:].strip()
                if not ai_enabled:
                    print(f"{RED} AI đang tắt, hãy gõ /on để bật lại.{RESET}")
                    continue
                loading()
                answer = ask_ai(question, mode="ask")
                pretty_print(" Trả lời:", answer, CYAN)
                continue

            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="")
                if ai_enabled:
                    loading()
                    fix = ask_ai(result.stderr, mode="error")
                    if fix:
                        pretty_print(" Gợi ý xử lý:", fix, GREEN)

        except KeyboardInterrupt:
            break

def stop_ai_helper():
    print(f"{RED} STV AI Helper đã dừng.{RESET}")

# Wrapper class
class botaistv:
    def __init__(self, token=API_KEY, system_prompt=None):
        self.token = token
        self.system_prompt = system_prompt

    def chat(self, message):
        return ask_ai(message, mode="ask")