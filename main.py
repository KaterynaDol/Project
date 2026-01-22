"""
Main module (CLI).
Содержит:
- главное меню
- выбор действия
- запуск сценариев (flows)
"""

# Импортируем сценарии (потоки) - отдельные функции, которые выполняют логику пунктов меню
from Project.flows import keyword_flow, genre_years_flow, stats_flow

# Текст главного меню (многострочная строка, выводится в консоль)
TEXT_MAIN_MENU = """
=== Movies Search ===
Please input 1, 2, 3 or 0:
1: Search by keyword (title)
2: Search by genre and years range
3: View statistics
0: Exit
"""


def read_choice(prompt: str, allowed: set[str]) -> str:
    """
    Считывает выбор пользователя и проверяет, что входит в allowed.
    Возвращает корректное значение (строку).
    """
    while True:
        value = input(prompt).strip()
        if value in allowed:
            return value

        # Если ввод неверный - просим повторить
        print(f"Wrong input. Allowed: {', '.join(sorted(allowed))}")


def main() -> None:
    """
    Точка входа CLI - приложения.
    В цикле показываем меню, читаем выбор и запускаем нужный flow.
    """
    while True:
        print(TEXT_MAIN_MENU)
        choice = read_choice("Your choice: ", {"1", "2", "3", "0"})

        if choice == "1":
            keyword_flow()
        elif choice == "2":
            genre_years_flow()
        elif choice == "3":
            stats_flow()
        elif choice == "0":
            print("Bye!")
            return


# Запуск только если файл выполняется напрямую, а не импортируется как модуль
if __name__ == "__main__":
    main()
