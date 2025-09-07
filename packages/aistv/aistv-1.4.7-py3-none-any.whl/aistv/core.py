import sqlite3
import time
import requests
from groq import Groq


# Cấu hình
DB_FILE = "usage.db"
SPAM_DELAY_SECONDS = 5
FREE_MAX_REQUESTS = 20
NORMAL_MAX_REQUESTS = 50
VIP_MAX_REQUESTS = None  # Không giới hạn

API_KEYS = [
    "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",
    "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",
]

# Danh sách token
TOKEN_VIP_SET = {"aistv", "phuc"}
TOKEN_NORMAL_SET = {"token_sk-or-v1-56d24544a83100b354a57f82ea83fc31e6ae249749df44a912e35769123ea5d5", "another_token..."}

class STVBot:
    def __init__(self, token: str = None, system_prompt: str = None):
        self.token = token
        self.system_prompt = system_prompt or "Tôi là AI STV, được phát triển bởi Trọng Phúc."
        self.api_keys = API_KEYS
        self.api_index = 0
        self.client = self._create_client()
        self.model = "openai/gpt-oss-120b"
        self.history = [{"role": "system", "content": self.system_prompt}]

        # Xác định user & giới hạn
        if not token:
            self.user_id = "free_user"
            self.max_requests = FREE_MAX_REQUESTS
        elif token in TOKEN_VIP_SET:
            self.user_id = token
            self.max_requests = VIP_MAX_REQUESTS
        elif token in TOKEN_NORMAL_SET:
            self.user_id = token
            self.max_requests = NORMAL_MAX_REQUESTS
        else:
            self.user_id = "free_user"
            self.max_requests = FREE_MAX_REQUESTS

        # CSDL lưu lượt dùng
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage (
                user_id TEXT PRIMARY KEY,
                count INTEGER,
                last_time REAL,
                last_date TEXT
            )
        ''')
        self.conn.commit()
        self._init_user()

    def _create_client(self):
        return Groq(api_key=self.api_keys[self.api_index])

    def _init_user(self):
        today = time.strftime("%Y-%m-%d")
        self.cursor.execute("SELECT * FROM usage WHERE user_id = ?", (self.user_id,))
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO usage (user_id, count, last_time, last_date) VALUES (?, ?, ?, ?)",
                (self.user_id, 0, 0, today)
            )
            self.conn.commit()

    def _get_usage(self):
        self.cursor.execute("SELECT count, last_time, last_date FROM usage WHERE user_id = ?", (self.user_id,))
        row = self.cursor.fetchone()
        return {
            "count": row[0],
            "last_time": row[1],
            "last_date": row[2]
        } if row else {"count": 0, "last_time": 0, "last_date": time.strftime("%Y-%m-%d")}

    def _save_usage(self, count, last_time, last_date):
        self.cursor.execute(
            "UPDATE usage SET count = ?, last_time = ?, last_date = ? WHERE user_id = ?",
            (count, last_time, last_date, self.user_id)
        )
        self.conn.commit()

    def chat(self, prompt: str) -> str:
        usage = self._get_usage()
        now = time.time()
        today = time.strftime("%Y-%m-%d")

        # Reset lượt mỗi ngày
        if usage["last_date"] != today:
            usage["count"] = 0
            usage["last_date"] = today

        # Kiểm tra giới hạn lượt dùng
        if self.max_requests is not None and usage["count"] >= self.max_requests:
            return (
                f"⚠️ Bạn đã dùng hết {self.max_requests} lượt trong ngày.\n"
                "Hãy thử lại vào ngày mai hoặc liên hệ để nâng cấp quyền. https://www.facebook.com/groups/583338454431039/?ref=share&mibextid=NSMWBT"
            )

        # Kiểm tra spam
        if now - usage["last_time"] < SPAM_DELAY_SECONDS:
            wait = SPAM_DELAY_SECONDS - int(now - usage["last_time"])
            return f"⚠️ Vui lòng đợi {wait} giây nữa trước khi gửi câu hỏi tiếp theo."

        self.history.append({"role": "user", "content": prompt})
        tries = len(self.api_keys)

        for _ in range(tries):
            try:
                self.client = self._create_client()
                response = self.client.chat.completions.create(
                    messages=self.history,
                    model=self.model,
                    stream=False
                )
                reply = response.choices[0].message.content.strip()
                self.history.append({"role": "assistant", "content": reply})

                # Lưu lượt dùng (trừ VIP)
                if self.max_requests is not None:
                    usage["count"] += 1
                    usage["last_time"] = now
                    self._save_usage(usage["count"], usage["last_time"], usage["last_date"])

                return reply

            except Exception as e:
                self.api_index += 1
                if self.api_index >= len(self.api_keys):
                    return f"⚠️ Tất cả sever đều hết chỗ hoặc hết lượt.\nLỗi cuối cùng: {e}"

        return "⚠️ Đã xảy ra lỗi. Vui lòng thử lại sau."