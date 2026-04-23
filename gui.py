import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import database as db
from models import Expense

class ExpenseManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер расходов")
        self.root.geometry("1200x700")
        
        # Инициализация БД
        db.init_db()
        
        # Стили
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных
        self.refresh_data()
    
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цветовая схема
        self.colors = {
            'bg': '#f0f0f0',
            'primary': '#2196F3',
            'success': '#4CAF50',
            'danger': '#f44336',
            'warning': '#FF9800'
        }
        
        self.root.configure(bg=self.colors['bg'])
    
    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель с кнопками
        self.create_top_panel()
        
        # Основной контент
        self.create_main_content()
        
        # Статус бар
        self.create_status_bar()
    
    def create_top_panel(self):
        """Создание верхней панели"""
        top_frame = tk.Frame(self.root, bg=self.colors['primary'], height=100)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        # Заголовок
        title = tk.Label(
            top_frame, 
            text="Менеджер личных расходов", 
            font=('Arial', 24, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        )
        title.pack(pady=20)
    
    def create_main_content(self):
        """Создание основного контента"""
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - форма добавления
        left_panel = tk.Frame(main_container, bg='white', relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.create_input_form(left_panel)
        
        # Правая панель - таблица и статистика
        right_panel = tk.Frame(main_container, bg=self.colors['bg'])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_stats_frame(right_panel)
        self.create_table_frame(right_panel)
    
    def create_input_form(self, parent):
        """Форма добавления расхода"""
        # Заголовок
        tk.Label(
            parent, 
            text="Добавить расход", 
            font=('Arial', 16, 'bold'),
            bg='white'
        ).pack(pady=10)
        
        # Поля ввода
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(padx=20, pady=10)
        
        # Сумма
        tk.Label(form_frame, text="Сумма:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.amount_entry = tk.Entry(form_frame, width=20, font=('Arial', 12))
        self.amount_entry.grid(row=0, column=1, pady=5)
        
        # Категория
        tk.Label(form_frame, text="Категория:", bg='white', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, width=18)
        self.category_combo['values'] = db.get_all_categories()
        self.category_combo.grid(row=1, column=1, pady=5)
        
        # Комментарий
        tk.Label(form_frame, text="Комментарий:", bg='white', font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        self.comment_text = tk.Text(form_frame, height=5, width=20)
        self.comment_text.grid(row=2, column=1, pady=5)
        
        # Кнопка добавления
        add_btn = tk.Button(
            form_frame,
            text="Добавить расход",
            command=self.add_expense,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        add_btn.grid(row=3, column=0, columnspan=2, pady=20)
    
    def create_stats_frame(self, parent):
        """Создание панели статистики"""
        stats_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Общая сумма
        self.total_label = tk.Label(
            stats_frame,
            text="Общая сумма: 0 ₽",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg=self.colors['primary']
        )
        self.total_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Фильтры
        filter_frame = tk.Frame(stats_frame, bg='white')
        filter_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(filter_frame, text="Фильтр:", bg='white').pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=["all", "today", "week", "month"], width=10)
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_data())
        
        tk.Button(
            filter_frame,
            text="Обновить",
            command=self.refresh_data,
            bg=self.colors['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
    
    def create_table_frame(self, parent):
        """Создание таблицы расходов"""
        # Фрейм для таблицы и скролла
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ('ID', 'Дата', 'Категория', 'Сумма', 'Комментарий')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        
        # Настройка колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('Дата', text='Дата')
        self.tree.heading('Категория', text='Категория')
        self.tree.heading('Сумма', text='Сумма (₽)')
        self.tree.heading('Комментарий', text='Комментарий')
        
        self.tree.column('ID', width=50)
        self.tree.column('Дата', width=100)
        self.tree.column('Категория', width=150)
        self.tree.column('Сумма', width=100)
        self.tree.column('Комментарий', width=400)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Связывание скроллов
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Контекстное меню
        self.create_context_menu()
        
        # Двойной клик для редактирования
        self.tree.bind('<Double-Button-1>', self.edit_expense)
    
    def create_context_menu(self):
        """Создание контекстного меню"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_expense)
        self.context_menu.add_command(label="Удалить", command=self.delete_expense)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def create_status_bar(self):
        """Создание статус бара"""
        self.status_bar = tk.Label(
            self.root,
            text="Готов к работе",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#e0e0e0'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def add_expense(self):
        """Добавление расхода"""
        try:
            amount = float(self.amount_entry.get())
            category = self.category_var.get()
            comment = self.comment_text.get("1.0", tk.END).strip()
            
            if not category:
                messagebox.showerror("Ошибка", "Выберите категорию")
                return
            
            # Валидация через модель
            expense = Expense(None, amount, category, comment, date.today())
            
            # Сохранение в БД
            expense_id = db.add_expense(expense.amount, expense.category, expense.comment)
            
            if expense_id:
                messagebox.showinfo("Успех", "Расход добавлен!")
                self.clear_form()
                self.refresh_data()
                self.status_bar.config(text=f"Добавлен расход на {amount} ₽")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить расход: {str(e)}")
    
    def delete_expense(self):
        """Удаление расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный расход?"):
            item = self.tree.item(selected[0])
            expense_id = item['values'][0]
            
            if db.delete_expense(expense_id):
                messagebox.showinfo("Успех", "Расход удален")
                self.refresh_data()
                self.status_bar.config(text="Расход удален")
    
    def edit_expense(self, event=None):
        """Редактирование расхода"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        expense_id, date_str, category, amount, comment = item['values']
        
        # Создание окна редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование расхода")
        edit_window.geometry("400x300")
        
        # Поля
        tk.Label(edit_window, text="Сумма:").pack(pady=5)
        amount_entry = tk.Entry(edit_window)
        amount_entry.insert(0, amount)
        amount_entry.pack(pady=5)
        
        tk.Label(edit_window, text="Комментарий:").pack(pady=5)
        comment_text = tk.Text(edit_window, height=5)
        comment_text.insert("1.0", comment)
        comment_text.pack(pady=5, padx=20)
        
        def save_changes():
            try:
                new_amount = float(amount_entry.get())
                new_comment = comment_text.get("1.0", tk.END).strip()
                
                if db.update_expense(expense_id, amount=new_amount, comment=new_comment):
                    messagebox.showinfo("Успех", "Изменения сохранены")
                    edit_window.destroy()
                    self.refresh_data()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверная сумма")
        
        tk.Button(edit_window, text="Сохранить", command=save_changes, bg=self.colors['success'], fg='white').pack(pady=20)
    
    def refresh_data(self):
        """Обновление данных"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение данных с учетом фильтра
        filter_type = self.filter_var.get()
        expenses = []
        
        if filter_type == "today":
            today = date.today()
            expenses = db.get_expenses_by_date(today, today)
        elif filter_type == "week":
            week_ago = date.today() - timedelta(days=7)
            expenses = db.get_expenses_by_date(week_ago, date.today())
        elif filter_type == "month":
            month_ago = date.today() - timedelta(days=30)
            expenses = db.get_expenses_by_date(month_ago, date.today())
        else:
            expenses = db.get_all_expenses()
        
        # Заполнение таблицы
        for expense in expenses:
            values = (
                expense['id'],
                expense['date'],
                expense['category'],
                f"{expense['amount']:.2f}",
                expense['comment'] or ""
            )
            self.tree.insert('', tk.END, values=values)
        
        # Обновление статистики
        total = db.get_total_expenses()
        self.total_label.config(text=f"Общая сумма: {total:.2f} ₽")
        
        # Обновление статуса
        self.status_bar.config(text=f"Загружено {len(expenses)} записей")
    
    def clear_form(self):
        """Очистка формы"""
        self.amount_entry.delete(0, tk.END)
        self.category_var.set("")
        self.comment_text.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    app = ExpenseManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
