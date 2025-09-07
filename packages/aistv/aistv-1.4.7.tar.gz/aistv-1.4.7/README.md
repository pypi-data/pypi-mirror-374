
---

# 🌟 aistv

**Thư viện STV AI Chatbot dành cho Python**

`aistv` là một thư viện Python nhẹ và hiệu quả, cho phép bạn tích hợp trợ lý ảo STV — một chatbot thông minh, thân thiện và linh hoạt

---

## 🧠 Giới thiệu

STV được phát triển bởi **Trọng Phúc** và ra mắt vào ngày **06/05/2025**, với mục tiêu hỗ trợ người dùng qua các cuộc trò chuyện tự nhiên, đa ngôn ngữ và mang tính cá nhân hóa cao.

---

## 🚀 Tính năng nổi bật

- ✉️ Gửi tin nhắn và nhận phản hồi theo ngữ cảnh từ STV AI  
- 🧾 Tự động lưu lịch sử hội thoại để duy trì mạch trò chuyện  
- ⚙️ Cho phép tùy chỉnh lời nhắc hệ thống (system prompt)  
- 🔌 Dễ dàng tích hợp vào mọi dự án Python  

---

## 📦 Yêu cầu

- Python **>= 3.8**
- Thư viện phụ trợ: `requests`

---

## 📥 Cài đặt

```bash
pip install aistv
```


---


🧪 Ví dụ 
```python
from aistv import aistv

bot = aistv()

while True:
    user_input = input("Bạn: ")
    if user_input.lower() == "exit":
        break
    reply = bot.chat(user_input)
    print("AI STV:", reply)
    
```    
🧪 Ví dụ 
```python
from aistv import aistv

Token=TOKEN_API
bot = aistv(token)

while True:
    user_input = input("Bạn: ")
    if user_input.lower() == "exit":
        break
    reply = bot.chat(user_input)
    print("AI STV:", reply)
    
```    


---

🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp từ cộng đồng!
Nếu bạn phát hiện lỗi hoặc muốn đề xuất tính năng mới:

Gửi issue trên GitHub

Gửi pull request kèm mô tả rõ ràng



---

📜 Giấy phép

Dự án được phát hành theo giấy phép MIT License.


---

👨‍💻 Tác giả

Trọng Phúc
Ngày phát hành đầu tiên: 01/06/2025


---

<br>🌟 aistv

STV AI Chatbot Library for Python

`aistv` is a lightweight and efficient Python library that allows you to integrate the STV virtual assistant — a smart, friendly and flexible chatbot


---

🧠 Introduction

STV was developed by Trong Phuc and officially launched on May 6, 2025, with the goal of enabling natural, multilingual, and highly personalized AI conversations.


---

🚀 Features

✉️ Send messages and receive contextual replies from STV

🧾 Auto-save chat history to maintain conversation continuity

⚙️ Customize system prompt according to your needs

🔌 Easily integrates with any Python project



---

📦 Requirements

Python >= 3.8

Dependency: requests



---

📥 Installation
```bash
pip install aistv
```


---


 🧪 Example
 ```python
 from aistv import aistv

 bot = aistv()

 whileTrue:
     user_input = input("You: ")
     if user_input.lower() == "exit":
         break. break
     reply = bot.chat(user_input)
     print("AI STV:", reply)   
 ```
🧪 Example
```python
from aistv import aistv

Token=TOKEN_API
bot = aistv(token)

while True:
    user_input = input("Bạn: ")
    if user_input.lower() == "exit":
        break
    reply = bot.chat(user_input)
    print("AI STV:", reply)
    
```    
---

⚙️ Advanced Prompt Customization

custom_prompt = "You are STV, a friendly AI assistant speaking in Vietnamese."
bot = aistv(token, system_prompt=custom_prompt)


---

🤝 Contributing

We welcome all contributions from the community!
If you find a bug or want to suggest a new feature:

Submit an issue on GitHub

Send a pull request with a clear description



---

📜 License

This project is released under the MIT License.


---

👨‍💻 Author

Trong Phuc
Initial release: June 1, 2025

