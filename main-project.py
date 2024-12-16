import tkinter as tk
import random
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

# Функция для подключения к базе данных
def connect_db():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            port='3306',
            database='naperstki_db',
            user='root',
            password='55555'
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Функция для создания таблиц пользователей и результатов
def create_tables():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        # Создаем таблицу пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        # Создаем таблицу результатов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                result VARCHAR(255) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

# Функция для добавления нового пользователя в базу данных
def insert_user(username, password):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password) VALUES (%s, %s)
            """, (username, password))
            conn.commit()
            messagebox.showinfo("Успех", "Регистрация успешна!")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {e}")
        finally:
            cursor.close()
            conn.close()

# Функция для аутентификации пользователя
def authenticate(username, password):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = %s AND password = %s
        """, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            messagebox.showinfo("Успех", "Авторизация успешна!")
            root.destroy()
            main_application(user[0]) # вызов основного приложения после аутентификации
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")

# Основное приложение - игра "Наперстки"
def main_application(user_id):
    global ball_under, user_id_global
    user_id_global = user_id
    main_window = tk.Tk()  # создаем главное окно
    main_window.title("Наперстки")
    main_window.geometry("500x300")

    ball_under = 0  # создаем переменную для хранения номера шарика

    button_frame = tk.Frame(main_window)  # создаем фрейм для кнопок
    button_frame.pack()

    button1 = tk.Button(button_frame, text="1", command=lambda: check_guess(0), background="#a1e0eb", foreground="black")  # кнопка первого стакана
    button1.pack(side=tk.LEFT, padx=10, pady=10)

    button2 = tk.Button(button_frame, text="2", command=lambda: check_guess(1), background="#a1e0eb", foreground="black")  # кнопка второго стакана
    button2.pack(side=tk.LEFT, padx=10, pady=10)

    button3 = tk.Button(button_frame, text="3", command=lambda: check_guess(2), background="#a1e0eb", foreground="black")  # кнопка третьего стакана
    button3.pack(side=tk.LEFT, padx=10, pady=10)

    shuffle_button = tk.Button(main_window, text="Перемешать", command=shuffle_balls, background="yellow")  # кнопка перемешивания
    shuffle_button.pack(pady=10)

    global result_label
    result_label = tk.Label(main_window, text="Угадай где шарик!", font=("Arial", 14))  # лейбл для вывода результата
    result_label.pack(pady=10)

    main_window.mainloop()

# Функция для обработки клика на кнопку
def check_guess(number):
    global ball_under
    if number == ball_under:
        result_label.config(text="Вы угадали!")  # вывод при победе =)
        save_result("Вы угадали!")
    else:
        result_label.config(text=f"Не угадали! Шарик был под наперстком номер {ball_under + 1} :-(")  # вывод при поражении =(
        save_result(f"Не угадали! Шарик был под наперстком номер {ball_under + 1} :-(")

# Функция для перемешивания шариков
def shuffle_balls():
    global ball_under
    ball_under = random.randint(0, 2)  # случайный выбор номера наперстка
    result_label.config(text="Наперстки перемешаны!")  # сообщение после перемешивания

# Функция для сохранения результата в базу данных
def save_result(result):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO results (user_id, result) VALUES (%s, %s)
        """, (user_id_global, result))
        conn.commit()
        cursor.close()
        conn.close()

# Функция для регистрации нового пользователя
def register():
    username = entry_username.get()
    password = entry_password.get()
    if username and password:
        insert_user(username, password)
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")

# Функция для входа пользователя
def login():
    username = entry_username.get()
    password = entry_password.get()
    authenticate(username, password)

# Основная часть программы
if __name__ == "__main__":
    create_tables()  # создание таблиц пользователей и результатов, если они не существуют
    root = tk.Tk()
    root.title("Авторизация")
    root.geometry("250x200")
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.wm_geometry("+%d+%d" % (x, y))

    tk.Label(root, text="Логин:").pack()
    entry_username = tk.Entry(root)
    entry_username.pack()

    tk.Label(root, text="Пароль:").pack()
    entry_password = tk.Entry(root, show='*')
    entry_password.pack()

    button_login = tk.Button(root, text="Войти", command=login) # кнопка входа
    button_login.pack()

    button_register = tk.Button(root, text="Зарегистрироваться", command=register) # кнопка регистрации
    button_register.pack()

    root.mainloop()
