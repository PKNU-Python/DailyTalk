import os
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from tkinter import Toplevel, Text, Entry, Label, Button

import openai
from dotenv import load_dotenv

# 환경 설정 및 상수
class Config:
    BG_COLOR = '#202124'
    TEXT_COLOR = '#303134'
    RESPONSE_BG_COLOR = '#505050'
    FONT_STYLE = ("Arial", 12)

    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is MISSING")

    @property
    def openai_key(self):
        return self.openai_api_key

# API 통신 관리
class OpenAIManager:
    def __init__(self, config):
        self.config = config

    def fetch_response(self, prompt):
        openai.api_key = self.config.openai_key
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message['content']
        except Exception as e:
            return "An error occurred: " + str(e)

# 비즈니스 로직 처리
class DiaryManager:
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.diaries = {}

    def save_entry(self, date, title, content):
        response = self.api_manager.fetch_response(content)
        self.diaries[date] = {'title': title, 'content': content, 'response': response}
        return response

    def load_entry(self, date):
        return self.diaries.get(date, None)

# UI 구성 관리
class DiaryUI:
    def __init__(self, master, config, diary_manager):
        self.master = master
        self.config = config
        self.diary_manager = diary_manager
        self.initialize_ui()

    def initialize_ui(self):
        self.master.title("Daily Talk")
        self.master.geometry("800x600")
        self.master.configure(bg=self.config.BG_COLOR)
        self.initialize_calendar()

    def initialize_calendar(self):
        style = ttk.Style()
        style.theme_use('clam')
        today = datetime.now()
        self.calendar = Calendar(self.master, selectmode='day', year=today.year, month=today.month, day=today.day, maxdate=today, bg=self.config.TEXT_COLOR, fg="white", font=self.config.FONT_STYLE)
        self.calendar.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.calendar.bind("<<CalendarSelected>>", self.open_diary_entry_popup)

    def open_diary_entry_popup(self, event=None):
        selected_date_str = self.calendar.get_date()
        self.popup = Toplevel(self.master)
        self.setup_diary_popup(selected_date_str)

    def setup_diary_popup(self, date):
        self.popup.title(f"Diary Entry for {date}")
        self.popup.geometry("500x600")
        self.popup.configure(bg=self.config.BG_COLOR)
        
        Label(self.popup, text="Title:", bg=self.config.BG_COLOR, fg='white', font=self.config.FONT_STYLE).pack(pady=(10,0))
        title_entry = Entry(self.popup, bg=self.config.TEXT_COLOR, fg="white", font=self.config.FONT_STYLE)
        title_entry.pack(fill=tk.X, padx=20)
        
        Label(self.popup, text="Content:", bg=self.config.BG_COLOR, fg='white', font=self.config.FONT_STYLE).pack(pady=(10,0))
        content_text = Text(self.popup, height=10, bg=self.config.TEXT_COLOR, fg="white", font=self.config.FONT_STYLE)
        content_text.pack(padx=20, pady=(0,10))
        
        Label(self.popup, text="AI Response:", bg=self.config.BG_COLOR, fg='white', font=self.config.FONT_STYLE).pack(pady=(10,0))
        response_text = Text(self.popup, height=10, bg=self.config.RESPONSE_BG_COLOR, fg="white", font=self.config.FONT_STYLE, state=tk.DISABLED)
        response_text.pack(padx=20, pady=(0,10))
        
        save_button = Button(self.popup, text="Save and Get Response", bg='#5f6368', fg='black', font=self.config.FONT_STYLE)
        save_button.pack(pady=10)
        
        title_entry.bind("<KeyRelease>", lambda e: self.validate_input(title_entry, content_text, save_button))
        content_text.bind("<KeyRelease>", lambda e: self.validate_input(title_entry, content_text, save_button))
        self.validate_input(title_entry, content_text, save_button)

        entry_data = self.diary_manager.load_entry(date)
        if entry_data:
            title_entry.insert(0, entry_data['title'])
            content_text.insert('1.0', entry_data['content'])
            response_text.config(state=tk.NORMAL)
            response_text.insert('1.0', entry_data['response'])
            response_text.config(state=tk.DISABLED)
            save_button.config(state=tk.DISABLED)
        else:
            save_button.config(command=lambda: self.save_diary_entry(date, title_entry.get(), content_text.get("1.0", tk.END).strip(), response_text, save_button))

    def validate_input(self, title_entry, content_text, save_button):
        if title_entry.get().strip() and content_text.get("1.0", "end-1c").strip():
            save_button.config(state=tk.NORMAL)
        else:
            save_button.config(state=tk.DISABLED)

    def save_diary_entry(self, date, title, content, response_text, save_button):
        response = self.diary_manager.save_entry(date, title, content)
        response_text.config(state=tk.NORMAL)
        response_text.delete('1.0', tk.END)
        response_text.insert(tk.END, response)
        response_text.config(state=tk.DISABLED)
        save_button.config(state=tk.DISABLED)
        self.calendar.calevent_create(date, 'Diary Entry', 'diary')
        self.calendar.see(date)

# 메인 실행 부분
def main():
    root = tk.Tk()
    config = Config()
    api_manager = OpenAIManager(config)
    diary_manager = DiaryManager(api_manager)
    app_ui = DiaryUI(root, config, diary_manager)
    root.mainloop()

if __name__ == "__main__":
    main()