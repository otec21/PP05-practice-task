import sqlite3
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

DATABASE_NAME = 'expenses.db'

@contextmanager
def get_db_connection():
    """Контекстный менеджер для соединения с БД"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Доступ по имени колонки
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Инициализация базы данных"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Таблица категорий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица расходов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK(amount > 0),
                category_id INTEGER NOT NULL,
                comment TEXT,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT
            )
        ''')
        
        # Индекс для ускорения запросов по дате
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON expenses(date)')
        
        # Добавление стандартных категорий
        default_categories = ['Еда', 'Транспорт', 'Развлечения', 'Здоровье', 
                             'Коммунальные услуги', 'Связь', 'Одежда', 'Другое']
        for cat in default_categories:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

def add_expense(amount: float, category_name: str, comment: str = "") -> int:
    """Добавление расхода"""
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Получаем или создаем категорию
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = cursor.fetchone()
        
        if result:
            category_id = result['id']
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            category_id = cursor.lastrowid
        
        today = date.today().isoformat()
        cursor.execute(
            'INSERT INTO expenses (amount, category_id, comment, date) VALUES (?, ?, ?, ?)',
            (amount, category_id, comment, today)
        )
        return cursor.lastrowid

def get_all_expenses(limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
    """Получение всех расходов с пагинацией"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT e.id, e.amount, c.name as category, e.comment, e.date
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            ORDER BY e.date DESC, e.created_at DESC
        '''
        
        if limit:
            query += f' LIMIT {limit} OFFSET {offset}'
        
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def get_expenses_by_date(start_date: date, end_date: date) -> List[Dict]:
    """Получение расходов за период"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, e.amount, c.name as category, e.comment, e.date
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date BETWEEN ? AND ?
            ORDER BY e.date DESC
        ''', (start_date.isoformat(), end_date.isoformat()))
        return [dict(row) for row in cursor.fetchall()]

def get_expenses_by_category(category_name: str) -> List[Dict]:
    """Получение расходов по категории"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, e.amount, c.name as category, e.comment, e.date
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE c.name = ?
            ORDER BY e.date DESC
        ''', (category_name,))
        return [dict(row) for row in cursor.fetchall()]

def get_total_expenses() -> float:
    """Общая сумма расходов"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses')
        return cursor.fetchone()[0]

def get_statistics_by_category() -> List[Dict]:
    """Статистика по категориям"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.name as category, 
                   COUNT(e.id) as count, 
                   SUM(e.amount) as total,
                   ROUND(AVG(e.amount), 2) as average
            FROM categories c
            LEFT JOIN expenses e ON c.id = e.category_id
            GROUP BY c.id
            ORDER BY total DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def delete_expense(expense_id: int) -> bool:
    """Удаление расхода"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        return cursor.rowcount > 0

def update_expense(expense_id: int, **kwargs) -> bool:
    """Обновление расхода"""
    allowed_fields = {'amount', 'comment', 'date'}
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [expense_id]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'UPDATE expenses SET {set_clause} WHERE id = ?', values)
        return cursor.rowcount > 0

def get_all_categories() -> List[str]:
    """Получение всех категорий"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM categories ORDER BY name')
        return [row['name'] for row in cursor.fetchall()]
