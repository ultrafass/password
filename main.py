import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

# --- Константы ---
HISTORY_FILE = "password_history.json"
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 128
DEFAULT_PASSWORD_LENGTH = 12

# --- Функции генерации пароля ---
def generate_password(length, use_digits, use_letters, use_symbols):
    """Генерирует пароль на основе заданных параметров."""
    characters = ""
    if use_digits:
        characters += string.digits
    if use_letters:
        characters += string.ascii_letters
    if use_symbols:
        characters += string.punctuation

    if not characters:
        return "", "Выберите хотя бы один тип символов."

    if not (MIN_PASSWORD_LENGTH <= length <= MAX_PASSWORD_LENGTH):
        return "", f"Длина пароля должна быть от {MIN_PASSWORD_LENGTH} до {MAX_PASSWORD_LENGTH} символов."

    password = ''.join(random.choice(characters) for _ in range(length))
    return password, None

# --- Функции управления историей ---
def load_history():
    """Загружает историю паролей из JSON-файла."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_history(history):
    """Сохраняет историю паролей в JSON-файл."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# --- GUI Окно ---
class PasswordGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Генератор Паролей")
        self.geometry("600x500")

        self.password_history = load_history()

        self.create_widgets()
        self.populate_history_table()

    def create_widgets(self):
        """Создает элементы интерфейса."""
        # --- Панель настроек ---
        settings_frame = ttk.LabelFrame(self, text="Настройки пароля")
        settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Ползунок длины
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.length_slider = ttk.Scale(settings_frame, from_=MIN_PASSWORD_LENGTH, to=MAX_PASSWORD_LENGTH, orient="horizontal", command=self.update_length_label)
        self.length_slider.set(DEFAULT_PASSWORD_LENGTH)
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text=str(DEFAULT_PASSWORD_LENGTH))
        self.length_label.grid(row=0, column=2, padx=5, pady=5)

        # Чекбоксы
        self.var_digits = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Цифры", variable=self.var_digits).grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.var_letters = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Буквы", variable=self.var_letters).grid(row=1, column=1, padx=5, pady=2, sticky="w")

        self.var_symbols = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Спецсимволы", variable=self.var_symbols).grid(row=1, column=2, padx=5, pady=2, sticky="w")

        # Кнопка генерации
        self.generate_button = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_and_display)
        self.generate_button.grid(row=2, column=0, columnspan=3, padx=5, pady=10)

        # Результат генерации
        ttk.Label(settings_frame, text="Сгенерированный пароль:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(settings_frame, width=50, state="readonly", font=("Arial", 12, "bold"))
        self.password_entry.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # --- Панель истории ---
        history_frame = ttk.LabelFrame(self, text="История паролей")
        history_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(history_frame, columns=("Password", "Length", "Digits", "Letters", "Symbols", "Timestamp"), show="headings")
        self.tree.heading("Password", text="Пароль")
        self.tree.heading("Length", text="Длина")
        self.tree.heading("Digits", text="Цифры")
        self.tree.heading("Letters", text="Буквы")
        self.tree.heading("Symbols", text="Символы")
        self.tree.heading("Timestamp", text="Время")

        self.tree.column("Password", width=200, anchor="w")
        self.tree.column("Length", width=70, anchor="center")
        self.tree.column("Digits", width=50, anchor="center")
        self.tree.column("Letters", width=50, anchor="center")
        self.tree.column("Symbols", width=60, anchor="center")
        self.tree.column("Timestamp", width=150, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Вертикальный скроллбар для таблицы
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        # Кнопка очистить историю
        clear_history_button = ttk.Button(history_frame, text="Очистить историю", command=self.clear_history)
        clear_history_button.grid(row=1, column=0, columnspan=2, pady=5)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)

    def update_length_label(self, value):
        """Обновляет метку с текущей длиной пароля."""
        self.length_label.config(text=str(int(float(value))))

    def populate_history_table(self):
        """Заполняет таблицу истории данными."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in self.password_history:
            self.tree.insert("", tk.END, values=(
                entry["password"],
                entry["length"],
                "✅" if entry["digits"] else "❌",
                "✅" if entry["letters"] else "❌",
                "✅" if entry["symbols"] else "❌",
                entry["timestamp"]
            ))

    def generate_and_display(self):
        """Генерирует пароль, обновляет поле ввода и сохраняет в историю."""
        length = int(self.length_slider.get())
        use_digits = self.var_digits.get()
        use_letters = self.var_letters.get()
        use_symbols = self.var_symbols.get()

        password, error = generate_password(length, use_digits, use_letters, use_symbols)

        if error:
            messagebox.showerror("Ошибка", error)
            return

        self.password_entry.config(state="normal")
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        self.password_entry.config(state="readonly")

        # Добавление в историю
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "password": password,
            "length": length,
            "digits": use_digits,
            "letters": use_letters,
            "symbols": use_symbols,
            "timestamp": timestamp
        }
        self.password_history.append(history_entry)
        save_history(self.password_history)
        self.populate_history_table()

    def clear_history(self):
        """Очищает историю паролей."""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю паролей?"):
            self.password_history = []
            save_history(self.password_history)
            self.populate_history_table()
            messagebox.showinfo("Готово", "История паролей очищена.")

# --- Главная функция ---
if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
