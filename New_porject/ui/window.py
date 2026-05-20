# ui/window.py
import tkinter as tk
from tkinter import font, messagebox, scrolledtext
from word.wrong_book import add_wrong_word, load_wrong_words, clear_wrong_words
from word.progress import save_progress, load_progress, clear_current_progress, clear_all_progress
import os
import random

class WordApp:
    def __init__(self, root, word_file, initial_words, on_back_callback, shuffle=False):
        self.root = root
        self.on_back_callback = on_back_callback
        self.root.title("GREat@背单词")
        self.root.geometry("760x860")
        self.root.resizable(False, False)
        self.word_file = word_file
        self.shuffle = shuffle

        self.words = initial_words
        self.total_word_count = len(initial_words)
        self.current_word = None

        # 正确率统计
        self.current_total = 0
        self.current_correct = 0
        self.load_accuracy_from_progress()

        self.create_ui()
        self.next_word()
        self.update_stats_display()

    # 从进度文件加载正确率
    def load_accuracy_from_progress(self):
        data = load_progress()
        if data and data.get("last_word_file") == self.word_file:
            self.current_total = data.get("current_total", 0)
            self.current_correct = data.get("current_correct", 0)

    def load_words(self):
        pass

    def create_ui(self):
        # 顶部状态栏
        top_frame = tk.Frame(self.root, bg="#009E5F", height=120)
        top_frame.pack(fill=tk.X, anchor=tk.N)

        # 上方大字：仅显示剩余单词
        self.status_label = tk.Label(
            top_frame, text="剩余：0",
            bg="#009E5F", fg="yellow", font=("微软雅黑", 24, "bold")
        )
        self.status_label.pack(pady=8)

        # 下方小字：已背/总数 + 当前正确率
        self.stats_label = tk.Label(
            top_frame, text="已背：0 / 总：0 | 当前正确率 0%",
            bg="#009E5F", fg="white", font=("微软雅黑", 16)
        )
        self.stats_label.pack(pady=3)

        # 单词展示区域
        word_frame = tk.Frame(self.root, bg="white", height=260)
        word_frame.pack(fill=tk.X, pady=20)

        self.word_label = tk.Label(word_frame, text="", bg="white", font=("微软雅黑", 36, "bold"))
        self.word_label.pack(pady=15)
        tk.Frame(word_frame, bg="#EEEEEE", height=2).pack(fill=tk.X, padx=100)
        self.meaning_label = tk.Label(word_frame, text="", bg="white", font=("微软雅黑", 20))
        self.meaning_label.pack(pady=20)

        # 核心操作按钮（纯白+黑边）
        btn_frame = tk.Frame(self.root, bg="#F8F8F8")
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self.btn_forget = tk.Button(
            btn_frame, text="我忘了", font=("微软雅黑", 22, "bold"),
            bg="#FFFFFF", fg="#222", relief=tk.SOLID, bd=1,
            activebackground="#EEEEEE", cursor="hand2", command=self.on_forget
        )
        self.btn_forget.grid(row=0, column=0, sticky="nswe", padx=10, pady=10, ipady=10)

        self.btn_remember = tk.Button(
            btn_frame, text="我记得", font=("微软雅黑", 22, "bold"),
            bg="#FFFFFF", fg="#222", relief=tk.SOLID, bd=1,
            activebackground="#EEEEEE", cursor="hand2", command=self.on_remember
        )
        self.btn_remember.grid(row=0, column=1, sticky="nswe", padx=10, pady=10, ipady=10)

        # 底部功能按钮通用样式：纯白+黑边
        button_style = {
            "font": ("微软雅黑", 16),
            "relief": tk.SOLID, "bd": 1,
            "cursor": "hand2",
            "bg": "#FFFFFF",
            "fg": "#222"
        }

        self.back_btn = tk.Button(self.root, text="返回词库选择", **button_style, command=self.go_back)
        self.back_btn.pack(fill=tk.X, padx=30, pady=4)

        self.wrong_btn = tk.Button(self.root, text="打开错题本",** button_style, command=self.open_wrong_book)
        self.wrong_btn.pack(fill=tk.X, padx=30, pady=4)

        self.set_btn = tk.Button(self.root, text="Settings", **button_style, command=self.open_settings)
        self.set_btn.pack(fill=tk.X, padx=30, pady=10)

    # 刷新进度与正确率显示
    def update_stats_display(self):
        remaining = len(self.words)
        finished = self.total_word_count - remaining

        if self.current_total > 0:
            acc = round(self.current_correct / self.current_total * 100, 1)
        else:
            acc = 0

        self.status_label.config(text=f"剩余：{remaining}")
        self.stats_label.config(text=f"已背：{finished} / 总：{self.total_word_count} | 当前正确率 {acc}%")

    def next_word(self):
        if not self.words:
            self.word_label.config(text="🎉 背完啦！")
            self.meaning_label.config(text="学习完成")
            self.status_label.config(text=f"剩余：0")
            self.btn_forget.config(state=tk.DISABLED)
            self.btn_remember.config(state=tk.DISABLED)
            return

        self.current_word = self.words.pop()
        self.word_label.config(text=self.current_word[0])
        self.meaning_label.config(text=self.current_word[1])
        self.update_stats_display()

    # 忘记单词（错误）
    def on_forget(self):
        add_wrong_word(self.current_word[0], self.current_word[1])
        self.words.insert(0, self.current_word)
        self.current_total += 1
        save_progress(self.word_file, self.words, self.current_total, self.current_correct)
        self.update_stats_display()
        self.next_word()

    # 记住单词（正确）
    def on_remember(self):
        self.current_total += 1
        self.current_correct += 1
        save_progress(self.word_file, self.words, self.current_total, self.current_correct)
        self.update_stats_display()
        self.next_word()

    # 打开错题本
    def open_wrong_book(self):
        wrong_words = load_wrong_words()
        if not wrong_words:
            messagebox.showinfo("错题本", "暂无错题！")
            return
        book_win = tk.Toplevel(self.root)
        book_win.title("错题本")
        book_win.geometry("600x500")
        text_area = scrolledtext.ScrolledText(book_win, font=("微软雅黑", 14))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for word, meaning in wrong_words:
            text_area.insert(tk.END, f"📌 {word}\n{meaning}\n\n")
        text_area.config(state=tk.DISABLED)

    # 【纯净版】设置弹窗：纯白+黑边，无多余色彩
    def open_settings(self):
        set_win = tk.Toplevel(self.root)
        set_win.title("设置中心")
        set_win.geometry("420x280")
        set_win.resizable(False, False)
        set_win.transient(self.root)

        tk.Label(set_win, text="请选择操作", font=("微软雅黑", 16, "bold")).pack(pady=20)

        # 设置内按钮统一：纯白+黑边
        btn_style = {
            "font": ("微软雅黑", 14),
            "relief": tk.SOLID, "bd": 1,
            "cursor": "hand2",
            "bg": "#FFFFFF",
            "fg": "#222",
            "width": 25, "height": 2
        }

        def func_clear_current():
            if messagebox.askyesno("确认", "确定清除【当前词库】的进度和正确率？"):
                clear_current_progress(self.word_file)
                messagebox.showinfo("提示", "✅ 当前词库记录已清除！")
                set_win.destroy()

        def func_clear_wrong():
            if messagebox.askyesno("确认", "确定清空【错题本】所有单词？"):
                clear_wrong_words()
                messagebox.showinfo("提示", "✅ 错题本已清空！")
                set_win.destroy()

        def func_clear_all():
            if messagebox.askyesno("警告", "确定清除【全部数据】？\n（进度、正确率、错题本全清空）"):
                clear_all_progress()
                clear_wrong_words()
                messagebox.showinfo("提示", "✅ 所有数据已清空！")
                set_win.destroy()

        tk.Button(set_win, text="清除当前词库背诵记录",** btn_style, command=func_clear_current).pack(pady=5)
        tk.Button(set_win, text="清空错题本", **btn_style, command=func_clear_wrong).pack(pady=5)
        tk.Button(set_win, text="一键清除所有数据",** btn_style, command=func_clear_all).pack(pady=5)

    # 返回词库选择界面
    def go_back(self):
        self.root.destroy()
        self.on_back_callback()