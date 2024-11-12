import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import sqlite3
import string
import random
from cryptography.fernet import Fernet

# Генерация и хранение ключа шифрования
def load_key():
    try:
        with open("key.key", "rb") as file:
            return file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("key.key", "wb") as file:
            file.write(key)
        return key

key = load_key()
cipher = Fernet(key)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            login TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Генерация пароля
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Сохранение пароля в базу
def save_password(site, login, password):
    encrypted_password = cipher.encrypt(password.encode()).decode()
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO passwords (site, login, password) VALUES (?, ?, ?)", (site, login, encrypted_password))
    conn.commit()
    conn.close()

# Поиск пароля
def search_password(site):
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("SELECT login, password FROM passwords WHERE site = ?", (site,))
    results = cursor.fetchall()
    conn.close()
    if results:
        decrypted_results = [(login, cipher.decrypt(password.encode()).decode()) for login, password in results]
        return decrypted_results
    else:
        return None

# Интерфейс tkinter
class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")

        # Метки и поля
        self.site_label = tk.Label(root, text="Website:")
        self.site_label.grid(row=0, column=0, padx=10, pady=5)
        self.site_entry = tk.Entry(root, width=30)
        self.site_entry.grid(row=0, column=1, padx=10, pady=5)

        self.login_label = tk.Label(root, text="Login:")
        self.login_label.grid(row=1, column=0, padx=10, pady=5)
        self.login_entry = tk.Entry(root, width=30)
        self.login_entry.grid(row=1, column=1, padx=10, pady=5)

        self.password_label = tk.Label(root, text="Password:")
        self.password_label.grid(row=2, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(root, width=30)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        # Кнопки
        self.generate_button = tk.Button(root, text="Generate Password", command=self.generate_password)
        self.generate_button.grid(row=3, column=0, padx=10, pady=5)
        self.save_button = tk.Button(root, text="Save Password", command=self.save_password)
        self.save_button.grid(row=3, column=1, padx=10, pady=5)
        self.search_button = tk.Button(root, text="Search Password", command=self.search_password)
        self.search_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    def generate_password(self):
        password = generate_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def save_password(self):
        site = self.site_entry.get()
        login = self.login_entry.get()
        password = self.password_entry.get()
        if site and login and password:
            save_password(site, login, password)
            messagebox.showinfo("Success", "Password saved successfully!")
            self.site_entry.delete(0, tk.END)
            self.login_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please fill all fields!")

    def search_password(self):
        site = self.site_entry.get()
        if site:
            results = search_password(site)
            if results:
                message = "\n".join([f"Login: {login}, Password: {password}" for login, password in results])
                messagebox.showinfo("Results", message)
            else:
                messagebox.showinfo("Results", "No passwords found for this website!")
        else:
            messagebox.showwarning("Warning", "Please enter a website!")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
