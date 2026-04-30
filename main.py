"""
Random Task Generator
GUI-приложение для генерации случайных задач с сохранением истории
Автор: Стерхов Егор Владимирович
Дата: 30.04.2026
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import random


class TaskGenerator:
    """Основной класс приложения для генерации случайных задач"""
    
    # Предопределённые задачи с категориями
    DEFAULT_TASKS = [
        {"title": "Прочитать статью по Python", "category": "учёба"},
        {"title": "Сделать зарядку 15 минут", "category": "спорт"},
        {"title": "Ответить на рабочие письма", "category": "работа"},
        {"title": "Посмотреть лекцию по ООП", "category": "учёба"},
        {"title": "Пробежка 2 км", "category": "спорт"},
        {"title": "Составить отчёт", "category": "работа"},
        {"title": "Решить 3 задачи на алгоритмы", "category": "учёба"},
        {"title": "Растяжка и йога", "category": "спорт"},
        {"title": "Позвонить клиенту", "category": "работа"},
        {"title": "Написать тесты для кода", "category": "учёба"}
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Хранилище задач и истории
        self.tasks = self.DEFAULT_TASKS.copy()
        self.history = []
        
        # Загрузка сохранённых данных
        self.load_data()
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Обновление отображения
        self.refresh_history_list()
    
    def setup_ui(self):
        """Настройка всех элементов интерфейса"""
        # Основной контейнер с отступами
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # ===== Верхняя секция: кнопка генерации =====
        generate_frame = ttk.LabelFrame(main_frame, text="Генерация задачи", padding="10")
        generate_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        generate_frame.columnconfigure(0, weight=1)
        
        self.generate_btn = ttk.Button(
            generate_frame, 
            text=">> Сгенерировать случайную задачу <<", 
            command=self.generate_random_task
        )
        self.generate_btn.grid(row=0, column=0, pady=5)
        
        # Текущая сгенерированная задача
        self.current_task_label = ttk.Label(
            generate_frame, 
            text="Нажмите кнопку, чтобы получить задачу",
            font=("Arial", 12, "bold"),
            wraplength=600
        )
        self.current_task_label.grid(row=1, column=0, pady=10)
        
        # ===== Секция добавления новой задачи =====
        add_frame = ttk.LabelFrame(main_frame, text="Добавить свою задачу", padding="10")
        add_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        add_frame.columnconfigure(1, weight=1)
        
        ttk.Label(add_frame, text="Название задачи:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.task_entry = ttk.Entry(add_frame, width=40)
        self.task_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(add_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.category_var = tk.StringVar(value="учёба")
        category_combo = ttk.Combobox(add_frame, textvariable=self.category_var, values=["учёба", "спорт", "работа"], state="readonly")
        category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.add_btn = ttk.Button(add_frame, text="[+] Добавить задачу", command=self.add_task)
        self.add_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # ===== Секция фильтрации =====
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация истории", padding="10")
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.filter_var = tk.StringVar(value="все")
        filter_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.filter_var, 
            values=["все", "учёба", "спорт", "работа"],
            state="readonly",
            width=15
        )
        filter_combo.grid(row=0, column=1, sticky=tk.W)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_history_list())
        
        ttk.Button(filter_frame, text="[X] Очистить фильтр", command=self.clear_filter).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(filter_frame, text="[#] Очистить историю", command=self.clear_history).grid(row=0, column=3, padx=(10, 0))
        
        # ===== Секция истории =====
        history_frame = ttk.LabelFrame(main_frame, text="История сгенерированных задач", padding="10")
        history_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Список с прокруткой
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.history_listbox = tk.Listbox(
            history_frame, 
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            height=12
        )
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.history_listbox.yview)
        
        # Информационная метка
        self.info_label = ttk.Label(main_frame, text="", foreground="gray")
        self.info_label.grid(row=4, column=0, pady=(5, 0))
    
    def add_task(self):
        """Добавление новой задачи с валидацией"""
        task_title = self.task_entry.get().strip()
        category = self.category_var.get()
        
        # Валидация: проверка на пустую строку
        if not task_title:
            messagebox.showwarning("Ошибка ввода", "Название задачи не может быть пустым!")
            return
        
        # Проверка на минимальную длину
        if len(task_title) < 3:
            messagebox.showwarning("Ошибка ввода", "Название задачи должно содержать минимум 3 символа!")
            return
        
        # Добавление задачи в общий список
        new_task = {"title": task_title, "category": category}
        self.tasks.append(new_task)
        
        # Очистка поля ввода
        self.task_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Задача '{task_title}' добавлена в категорию '{category}'")
        
        # Визуальная обратная связь
        self.info_label.config(text="[OK] Задача добавлена. Всего задач в базе: " + str(len(self.tasks)), foreground="green")
        self.root.after(3000, lambda: self.info_label.config(text="", foreground="gray"))
    
    def generate_random_task(self):
        """Генерация случайной задачи и добавление в историю"""
        if not self.tasks:
            messagebox.showwarning("Нет задач", "Список задач пуст. Добавьте новые задачи!")
            return
        
        # Выбор случайной задачи
        selected_task = random.choice(self.tasks)
        
        # Добавление в историю с временной меткой
        history_entry = {
            "title": selected_task["title"],
            "category": selected_task["category"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        
        # Сохранение в JSON
        self.save_to_json()
        
        # Обновление отображения
        self.current_task_label.config(
            text="*** " + selected_task["title"] + " ***\n(категория: " + selected_task["category"] + ")",
            foreground="darkgreen"
        )
        self.refresh_history_list()
        
        # Визуальная обратная связь
        self.info_label.config(text="[OK] Сгенерирована задача #" + str(len(self.history)), foreground="green")
        self.root.after(2000, lambda: self.info_label.config(text="", foreground="gray"))
    
    def refresh_history_list(self):
        """Обновление списка истории с учётом фильтра"""
        self.history_listbox.delete(0, tk.END)
        
        filter_category = self.filter_var.get()
        
        # Фильтрация истории
        filtered_history = self.history
        if filter_category != "все":
            filtered_history = [item for item in self.history if item["category"] == filter_category]
        
        # Отображение в списке
        if not filtered_history:
            self.history_listbox.insert(tk.END, "[!] История пуста")
        else:
            for i, item in enumerate(filtered_history, 1):
                display_text = str(i) + ". [" + item["timestamp"] + "] " + item["title"] + " (" + item["category"] + ")"
                self.history_listbox.insert(tk.END, display_text)
        
        # Обновление информации
        total = len(self.history)
        shown = len(filtered_history)
        self.info_label.config(
            text="Всего задач в истории: " + str(total) + " | Отображается: " + str(shown),
            foreground="gray"
        )
    
    def clear_filter(self):
        """Очистка фильтра"""
        self.filter_var.set("все")
        self.refresh_history_list()
        self.info_label.config(text="Фильтр очищен", foreground="blue")
        self.root.after(2000, lambda: self.refresh_history_list())
    
    def clear_history(self):
        """Очистка всей истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_to_json()
            self.refresh_history_list()
            self.current_task_label.config(text="История очищена. Нажмите кнопку для генерации", foreground="gray")
            self.info_label.config(text="[OK] История очищена", foreground="green")
            self.root.after(2000, lambda: self.info_label.config(text="", foreground="gray"))
    
    def save_to_json(self):
        """Сохранение истории и задач в JSON файл"""
        data = {
            "history": self.history,
            "custom_tasks": [task for task in self.tasks if task not in self.DEFAULT_TASKS]
        }
        
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", "Не удалось сохранить данные: " + str(e))
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.history = data.get("history", [])
                custom_tasks = data.get("custom_tasks", [])
                
                # Объединение стандартных и пользовательских задач
                self.tasks = self.DEFAULT_TASKS.copy()
                for task in custom_tasks:
                    if task not in self.tasks:
                        self.tasks.append(task)
                        
            except Exception as e:
                print("Ошибка загрузки: " + str(e))
                self.history = []
                self.tasks = self.DEFAULT_TASKS.copy()


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGenerator(root)
    root.mainloop()