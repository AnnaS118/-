import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

# Файл для хранения данных
DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("800x600")
        
        # Список для хранения расходов
        self.expenses = []
        
        # Загрузка данных из файла
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # === Фрейм для ввода данных ===
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле "Сумма"
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле "Категория"
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Жильё", "Другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=categories, width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set("Еда")
        
        # Поле "Дата"
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Кнопка "Добавить"
        self.add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # === Фрейм для фильтрации ===
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        filter_categories = ["Все"] + categories
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=filter_categories, width=15)
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category_combo.set("Все")
        
        ttk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_from = tk.StringVar()
        self.date_from_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_from, width=12)
        self.date_from_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Дата до (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.filter_date_to = tk.StringVar()
        self.date_to_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_to, width=12)
        self.date_to_entry.grid(row=0, column=5, padx=5, pady=5)
        
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table)
        self.filter_btn.grid(row=0, column=6, padx=5, pady=5)
        
        self.reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=7, padx=5, pady=5)
        
        # === Таблица для отображения расходов ===
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("id", "Дата", "Категория", "Сумма")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма", text="Сумма (руб)")
        
        self.tree.column("id", width=50)
        self.tree.column("Дата", width=120)
        self.tree.column("Категория", width=150)
        self.tree.column("Сумма", width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === Фрейм для итогов ===
        total_frame = ttk.Frame(self.root)
        total_frame.pack(fill="x", padx=10, pady=5)
        
        self.total_label = ttk.Label(total_frame, text="Общая сумма за период: 0.00 руб", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=10)
        
        # Кнопка удаления
        self.delete_btn = ttk.Button(total_frame, text="Удалить выбранное", command=self.delete_expense)
        self.delete_btn.pack(side="right", padx=10)
        
        # Контекстное меню для удаления
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить", command=self.delete_expense)
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def validate_amount(self, amount_str):
        """Проверка, что сумма - положительное число"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                return False, "Сумма должна быть положительным числом"
            return True, amount
        except ValueError:
            return False, "Сумма должна быть числом"
    
    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, date_str
        except ValueError:
            return False, "Дата должна быть в формате ГГГГ-ММ-ДД"
    
    def add_expense(self):
        """Добавление нового расхода"""
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_var.get().strip()
        
        # Валидация
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму")
            return
        
        valid_amount, amount_result = self.validate_amount(amount_str)
        if not valid_amount:
            messagebox.showerror("Ошибка", amount_result)
            return
        
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию")
            return
        
        valid_date, date_result = self.validate_date(date_str)
        if not valid_date:
            messagebox.showerror("Ошибка", date_result)
            return
        
        # Генерация ID
        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        
        # Добавление расхода
        expense = {
            "id": new_id,
            "amount": amount_result,
            "category": category,
            "date": date_result
        }
        self.expenses.append(expense)
        
        # Сохранение и обновление
        self.save_data()
        self.refresh_table()
        
        # Очистка поля суммы
        self.amount_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        
        messagebox.showinfo("Успех", "Расход добавлен")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный расход?"):
            item = self.tree.item(selected[0])
            expense_id = item["values"][0]
            
            self.expenses = [e for e in self.expenses if e["id"] != expense_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Расход удалён")
    
    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтрация
        filtered_expenses = self.expenses.copy()
        
        # Фильтр по категории
        filter_category = self.filter_category_var.get()
        if filter_category != "Все":
            filtered_expenses = [e for e in filtered_expenses if e["category"] == filter_category]
        
        # Фильтр по дате
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                filtered_expenses = [e for e in filtered_expenses if datetime.strptime(e["date"], "%Y-%m-%d") >= from_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'от'")
                return
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                filtered_expenses = [e for e in filtered_expenses if datetime.strptime(e["date"], "%Y-%m-%d") <= to_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'до'")
                return
        
        # Сортировка по дате
        filtered_expenses.sort(key=lambda x: x["date"])
        
        # Заполнение таблицы
        for exp in filtered_expenses:
            self.tree.insert("", "end", values=(
                exp["id"],
                exp["date"],
                exp["category"],
                f"{exp['amount']:.2f}"
            ))
        
        # Подсчёт суммы за период
        total = sum(exp["amount"] for exp in filtered_expenses)
        self.total_label.config(text=f"Общая сумма за период: {total:.2f} руб")
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_category_var.set("Все")
        self.filter_date_from.set("")
        self.filter_date_to.set("")
        self.refresh_table()
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.expenses = []
        else:
            self.expenses = []
    
    def save_data(self):
        """Сохранение данных в JSON"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
