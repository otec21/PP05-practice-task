
"""
Менеджер личных расходов
Версия 2.0
"""

import sys
import database as db

def main():
    """Главная функция"""
    try:
        # Инициализация БД
        db.init_db()
        
        # Запуск GUI
        from gui import main as gui_main
        gui_main()
        
    except KeyboardInterrupt:
        print("\nПрограмма завершена")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
