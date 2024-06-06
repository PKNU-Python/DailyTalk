import tkinter as tk
from tkinter import scrolledtext
import openai
import os
from dotenv import load_dotenv

# 토큰 정보로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

class ChatBot:
    def __init__(self, master):
        self.master = master
        master.title("ChatBot")
        master.geometry("700x500")
        master.configure(bg='#202124')

        self.text_frame = tk.Frame(master, bg='#202124')
        self.text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.chat_area = scrolledtext.ScrolledText(self.text_frame, state='disabled', bg="#303134", fg="white", font=("Arial", 12))
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        self.entry_frame = tk.Frame(master, bg='#202124')
        self.entry_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.user_input = tk.Entry(self.entry_frame, bg="#303134", fg="white", font=("Arial", 12), insertbackground='white')
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)  # 엔터 키 이벤트 바인딩

        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message, bg='#5f6368', fg='black', font=("Arial", 12))
        self.send_button.pack(side=tk.RIGHT)

    def send_message(self, event=None):  # event 매개변수 추가
        message = self.user_input.get()
        if message:
            self.update_chat("You: " + message)
            self.user_input.delete(0, tk.END)
            response = self.get_response_from_openai(message)
            self.update_chat("Bot: " + response)

    def update_chat(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def get_response_from_openai(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError as e:
            return "Sorry, I've reached my usage limit for today. Please try again later."
        except openai.error.APIError as e:
            return "API error occurred: " + str(e)
        except openai.error.AuthenticationError as e:
            return "Authentication error: Please check your API key."
        except openai.error.OpenAIError as e:
            return "An unexpected error occurred: " + str(e)
        except Exception as e:
            return "An error occurred: " + str(e)

root = tk.Tk()
chat_bot = ChatBot(root)
root.mainloop()
