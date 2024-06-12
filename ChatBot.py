import tkinter as tk
from tkinter import Toplevel, Text, Entry, Label, Button, messagebox
from tkcalendar import Calendar
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# 토큰 정보 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

class ChatBot:
    def __init__(self, master):
        self.master = master
        master.title("Diary with AI")
        master.geometry("800x600")
        master.configure(bg='#202124')

        # 현재 날짜 가져오기
        today = datetime.now()
        self.today = today.strftime('%Y-%m-%d')  # YYYY-MM-DD 형식으로 저장
        self.calendar = Calendar(master, selectmode='day', year=today.year, month=today.month, day=today.day, bg="#303134", fg="white", font=("Arial", 12))
        self.calendar.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.calendar.bind("<<CalendarSelected>>", self.create_diary_popup)

        # 날짜별 일기 데이터 저장
        self.diaries = {}

        # 캘린더에 저장된 일기 표시
        self.initialize_calendar_events()

    def initialize_calendar_events(self):
        for date in self.diaries:
            self.calendar.calevent_create(date, 'Diary Entry', 'diary')
        self.calendar.tag_config('diary', background='white', foreground='white')

    def create_diary_popup(self, event=None):
        selected_date_str = self.calendar.get_date()
        
        self.popup = Toplevel(self.master)
        self.popup.title(f"Diary Entry for {selected_date_str}")
        self.popup.geometry("500x600")
        self.popup.configure(bg='#202124')

        Label(self.popup, text="Title:", bg='#202124', fg='white', font=("Arial", 12)).pack(pady=(10,0))
        self.title_entry = Entry(self.popup, bg="#303134", fg="white", font=("Arial", 12))
        self.title_entry.pack(fill=tk.X, padx=20)
        self.title_entry.bind("<KeyRelease>", self.validate_title_input)

        Label(self.popup, text="Content:", bg='#202124', fg='white', font=("Arial", 12)).pack(pady=(10,0))
        self.content_text = Text(self.popup, height=10, bg="#303134", fg="white", font=("Arial", 12))
        self.content_text.pack(padx=20, pady=(0,10))
        self.content_text.bind("<KeyRelease>", self.validate_content_input)

        Label(self.popup, text="AI Response:", bg='#202124', fg='white', font=("Arial", 12)).pack(pady=(10,0))
        self.response_text = Text(self.popup, height=10, bg="#505050", fg="white", font=("Arial", 12))
        self.response_text.pack(padx=20, pady=(0,10))
        self.response_text.config(state=tk.DISABLED)

        self.save_button = Button(self.popup, text="Save and Get Response", command=lambda: self.save_diary(selected_date_str), bg='#5f6368', fg='black', font=("Arial", 12))
        self.save_button.pack(pady=10)
        self.save_button.config(state=tk.DISABLED)  # Initially disabled

        # Load existing diary if available
        if selected_date_str in self.diaries:
            data = self.diaries[selected_date_str]
            self.title_entry.insert(0, data['title'])
            self.content_text.insert('1.0', data['content'])
            self.response_text.config(state=tk.NORMAL)
            self.response_text.insert('1.0', data['response'])
            self.response_text.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)

    def validate_title_input(self, event=None):
        self.check_save_button_state()

    def validate_content_input(self, event=None):
        self.check_save_button_state()

    def check_save_button_state(self):
        if self.title_entry.get().strip() and self.content_text.get("1.0", "end-1c").strip():
            self.save_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.DISABLED)

    def save_diary(self, date):
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END).strip()
        self.save_button.config(state=tk.DISABLED)  # Disable the button to prevent multiple clicks
        if date not in self.diaries:
            response = self.get_response_from_openai(content)
            self.update_response(response)
            self.diaries[date] = {'title': title, 'content': content, 'response': response}
            self.calendar.calevent_create(date, 'Diary Entry', 'diary')
            self.calendar.see(date)

    def update_response(self, response):
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete('1.0', tk.END)
        self.response_text.insert(tk.END, response)
        self.response_text.config(state=tk.DISABLED)

    def get_response_from_openai(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message['content']
        except Exception as e:
            return "An error occurred: " + str(e)

root = tk.Tk()
chat_bot = ChatBot(root)
root.mainloop()
