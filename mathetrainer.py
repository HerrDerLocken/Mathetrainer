import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Menu, font
import sqlite3
import random
import time

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect('mathe_trainer-2.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    best_time REAL,
    avg_multiplication_time REAL,
    avg_division_time REAL,
    avg_addition_time REAL,
    avg_subtraction_time REAL
)''')
conn.commit()

class MatheTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mathe-Trainer")
        self.root.geometry("1920x1080")
        self.root.state("zoomed")
        self.user_id = None
        self.username = None
        self.max_factor = 10
        self.num_tasks = 10
        self.task_times = []
        self.operation_modes = []
        self.task_count_by_type = {"multiplication": 0, "division": 0, "addition": 0, "subtraction": 0}
        self.time_by_type = {"multiplication": [], "division": [], "addition": [], "subtraction": []}
        self.show_start_screen()

    def show_start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        title_font = font.Font(size=20)
        button_font = font.Font(size=16)
        
        tk.Label(self.root, text="Willkommen zum Mathe-Trainer", font=title_font).pack(pady=40)
        
        tk.Button(self.root, text="Bestehenden Account auswählen", command=self.show_user_selection, font=button_font).pack(pady=20)
        tk.Button(self.root, text="Neuen Account erstellen", command=self.create_user, font=button_font).pack(pady=20)
        
        # Dropdown für Bestenlisten
        tk.Label(self.root, text="Bestenlisten anzeigen:", font=button_font).pack(pady=10)
        leaderboard_options = [
            "Beste Zeiten - Addition",
            "Beste Zeiten - Subtraktion",
            "Beste Zeiten - Multiplikation",
            "Beste Zeiten - Division",
            "Gesamtdurchschnitt"
        ]
        self.leaderboard_var = tk.StringVar(self.root)
        self.leaderboard_var.set("Bestenliste auswählen")
        leaderboard_menu = ttk.Combobox(self.root, textvariable=self.leaderboard_var, values=leaderboard_options, font=button_font, state="readonly")
        leaderboard_menu.pack(pady=10)
        leaderboard_menu.bind("<<ComboboxSelected>>", self.show_selected_leaderboard)
        
        tk.Button(self.root, text="Bestenliste anzeigen", command=self.show_selected_leaderboard, font=button_font).pack(pady=20)

    def show_selected_leaderboard(self, event=None):
        selected = self.leaderboard_var.get()
        if selected == "Beste Zeiten - Addition":
            self.show_best_addition_times()
        elif selected == "Beste Zeiten - Subtraktion":
            self.show_best_subtraction_times()
        elif selected == "Beste Zeiten - Multiplikation":
            self.show_best_multiplication_times()
        elif selected == "Beste Zeiten - Division":
            self.show_best_division_times()
        elif selected == "Gesamtdurchschnitt":
            self.show_average_times()

    # Bestenlisten-Methoden
    def show_best_addition_times(self):
        self.display_best_times("avg_addition_time", "Beste Zeiten - Addition")

    def show_best_subtraction_times(self):
        self.display_best_times("avg_subtraction_time", "Beste Zeiten - Subtraktion")

    def show_best_multiplication_times(self):
        self.display_best_times("avg_multiplication_time", "Beste Zeiten - Multiplikation")

    def show_best_division_times(self):
        self.display_best_times("avg_division_time", "Beste Zeiten - Division")

    def show_average_times(self):
        query = '''
        SELECT username, 
        (avg_addition_time + avg_subtraction_time + avg_multiplication_time + avg_division_time) / 4.0 as avg_total_time
        FROM users
        WHERE avg_addition_time IS NOT NULL AND avg_subtraction_time IS NOT NULL 
        AND avg_multiplication_time IS NOT NULL AND avg_division_time IS NOT NULL
        ORDER BY avg_total_time ASC
        LIMIT 10
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        self.display_times(rows, "Gesamtdurchschnitt")

    def display_best_times(self, column, title):
        query = f"SELECT username, {column} FROM users WHERE {column} IS NOT NULL ORDER BY {column} ASC LIMIT 10"
        cursor.execute(query)
        rows = cursor.fetchall()
        self.display_times(rows, title)

    def display_times(self, rows, title):
        for widget in self.root.winfo_children():
            widget.destroy()
        title_font = font.Font(size=20)
        content_font = font.Font(size=16)
        tk.Label(self.root, text=title, font=title_font).pack(pady=40)

        if not rows:
            tk.Label(self.root, text="Keine Daten verfügbar.", font=content_font).pack(pady=20)
        else:
            for row in rows:
                username, time = row
                tk.Label(self.root, text=f"{username}: {time:.2f} Sekunden", font=content_font).pack(pady=10)

        tk.Button(self.root, text="Zurück zum Hauptmenü", command=self.show_start_screen, font=content_font).pack(pady=20)


    def show_user_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        title_font = font.Font(size=20)
        tk.Label(self.root, text="Wähle deinen Account", font=title_font).pack(pady=40)
        self.user_var = tk.StringVar(self.root)
        cursor.execute("SELECT username FROM users")
        users = [row[0] for row in cursor.fetchall()]
        if users:
            self.user_var.set(users[0])
            user_menu = tk.OptionMenu(self.root, self.user_var, *users)
            user_menu.config(font=title_font)
            user_menu.pack(pady=20)
            tk.Button(self.root, text="Auswählen", command=self.select_user, font=title_font).pack(pady=20)
        else:
            tk.Label(self.root, text="Keine Benutzer gefunden. Erstelle einen neuen Account.", font=title_font).pack(pady=40)
        tk.Button(self.root, text="Zurück", command=self.show_start_screen, font=title_font).pack(pady=20)

    def select_user(self):
        username = self.user_var.get()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            self.user_id = result[0]
            self.username = username
            self.show_operation_selection()
        else:
            messagebox.showerror("Fehler", "Benutzername nicht gefunden.")

    def create_user(self):
        username = simpledialog.askstring("Neuen Account erstellen", "Benutzernamen eingeben:")
        if username:
            try:
                cursor.execute("INSERT INTO users (username, best_time) VALUES (?, ?)", (username, None))
                conn.commit()
                self.user_id = cursor.lastrowid
                self.username = username
                self.show_operation_selection()
            except sqlite3.IntegrityError:
                messagebox.showerror("Fehler", "Benutzername bereits vergeben.")

    def show_operation_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        title_font = font.Font(size=20)
        tk.Label(self.root, text=f"Willkommen, {self.username}", font=title_font).pack(pady=40)
        tk.Label(self.root, text="Wähle den Aufgabentyp:", font=title_font).pack(pady=20)
        
        self.var_multiplication = tk.BooleanVar()
        self.var_division = tk.BooleanVar()
        self.var_addition = tk.BooleanVar()
        self.var_subtraction = tk.BooleanVar()

        tk.Checkbutton(self.root, text="Multiplikation", variable=self.var_multiplication, font=title_font).pack(pady=10)
        tk.Checkbutton(self.root, text="Division", variable=self.var_division, font=title_font).pack(pady=10)
        tk.Checkbutton(self.root, text="Addition", variable=self.var_addition, font=title_font).pack(pady=10)
        tk.Checkbutton(self.root, text="Subtraktion", variable=self.var_subtraction, font=title_font).pack(pady=10)
        
        tk.Button(self.root, text="Bestätigen", command=self.confirm_operation_modes, font=title_font).pack(pady=20)
        tk.Button(self.root, text="Zurück", command=self.show_start_screen, font=title_font).pack(pady=20)


    def confirm_operation_modes(self):
        self.operation_modes = []
        if self.var_multiplication.get():
            self.operation_modes.append("multiplication")
        if self.var_division.get():
            self.operation_modes.append("division")
        if self.var_addition.get():
            self.operation_modes.append("addition")
        if self.var_subtraction.get():
            self.operation_modes.append("subtraction")
        
        if not self.operation_modes:
            messagebox.showerror("Fehler", "Bitte mindestens einen Aufgabentyp auswählen.")
        else:
            self.show_task_and_factor_selection_screen()

    def show_task_and_factor_selection_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        title_font = font.Font(size=20)
        tk.Label(self.root, text="Wähle die Anzahl der Aufgaben:", font=title_font).pack(pady=20)
        task_options = [10, 25, 50, 100]
        for count in task_options:
            tk.Button(self.root, text=f"{count} Aufgaben", command=lambda c=count: self.show_factor_selection(c), font=title_font).pack(pady=10)
        tk.Button(self.root, text="Zurück", command=self.show_operation_selection, font=title_font).pack(pady=20)

    def show_factor_selection(self, num_tasks):
        self.num_tasks = num_tasks
        for widget in self.root.winfo_children():
            widget.destroy()
        title_font = font.Font(size=20)
        tk.Label(self.root, text="Wähle den größten Faktor für die Aufgaben:", font=title_font).pack(pady=20)
        tk.Button(self.root, text="Kleines 1x1 (Faktor bis 10)", command=self.use_small_multiplication_table, font=title_font).pack(pady=10)
        self.custom_factor_entry = tk.Entry(self.root, font=title_font)
        self.custom_factor_entry.pack(pady=10)
        tk.Button(self.root, text="Benutzerdefinierten Faktor verwenden", command=self.use_custom_factor, font=title_font).pack(pady=10)
        tk.Button(self.root, text="Zurück", command=self.show_task_and_factor_selection_screen, font=title_font).pack(pady=20)

    def use_small_multiplication_table(self):
        self.max_factor = 10
        self.start_tasks()

    def use_custom_factor(self):
        try:
            custom_factor = int(self.custom_factor_entry.get())
            if custom_factor > 0:
                self.max_factor = custom_factor
                self.start_tasks()
            else:
                messagebox.showerror("Fehler", "Der Faktor muss größer als 0 sein.")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Zahl ein.")

    def start_tasks(self):
        self.correct_answers = 0
        self.task_index = 0
        self.start_time = time.time()
        self.task_times = []
        self.task_count_by_type = {"multiplication": 0, "division": 0, "addition": 0, "subtraction": 0}
        self.time_by_type = {"multiplication": [], "division": [], "addition": [], "subtraction": []}
        self.show_next_task()

    def show_next_task(self):
        if self.task_index < self.num_tasks:
            self.task_index += 1
            operation = random.choice(self.operation_modes)

            if operation == "multiplication":
                self.a = random.randint(0, self.max_factor)
                self.b = random.randint(0, self.max_factor)
                self.correct_answer = self.a * self.b
                task_text = f"{self.a} * {self.b} = ?"

            elif operation == "division":
                self.b = random.randint(1, self.max_factor)
                self.a = self.b * random.randint(0, self.max_factor)
                self.correct_answer = self.a // self.b
                task_text = f"{self.a} / {self.b} = ?"

            elif operation == "addition":
                self.a = random.randint(0, 100)
                self.b = random.randint(0, 100)
                self.correct_answer = self.a + self.b
                task_text = f"{self.a} + {self.b} = ?"

            elif operation == "subtraction":
                self.a = random.randint(0, 100)
                self.b = random.randint(0, self.a)
                self.correct_answer = self.a - self.b
                task_text = f"{self.a} - {self.b} = ?"

            self.current_operation = operation
            for widget in self.root.winfo_children():
                widget.destroy()

            title_font = font.Font(size=20)
            tk.Label(self.root, text=f"Aufgabe {self.task_index}/{self.num_tasks}", font=title_font).pack(pady=20)
            tk.Label(self.root, text=task_text, font=title_font).pack(pady=20)
            self.answer_entry = tk.Entry(self.root, font=title_font)
            self.answer_entry.pack(pady=20)
            self.answer_entry.focus_set()
            self.answer_entry.bind("<Return>", self.check_answer)  # Enter-Taste-Bindung korrigiert

            tk.Button(self.root, text="Bestätigen", command=self.check_answer, font=title_font).pack(pady=20)
        else:
            self.end_tasks()

    def check_answer(self, event=None):  # event-Parameter hinzugefügt für die Kompatibilität mit der Enter-Taste-Bindung
        try:
            user_answer = int(self.answer_entry.get())
            task_time = time.time() - self.start_time
            if user_answer == self.correct_answer:
                self.task_times.append(task_time)
                self.time_by_type[self.current_operation].append(task_time)
                self.task_count_by_type[self.current_operation] += 1
                self.correct_answers += 1
            else:
                messagebox.showerror("Fehler", f"Falsche Antwort. Die richtige Antwort ist {self.correct_answer}.")

            self.start_time = time.time()

            if self.task_index <= self.num_tasks:
                self.show_next_task()
            else:
                self.end_tasks()

        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben.")

    def end_tasks(self):
        total_time = sum(self.task_times)
        avg_time = total_time / len(self.task_times) if self.task_times else 0

        for widget in self.root.winfo_children():
            widget.destroy()
        title_font = font.Font(size=20)
        tk.Label(self.root, text="Aufgaben beendet", font=title_font).pack(pady=20)
        tk.Label(self.root, text=f"Zeit insgesamt: {total_time:.2f} Sekunden", font=title_font).pack(pady=20)
        tk.Label(self.root, text=f"Durchschnittszeit: {avg_time:.2f} Sekunden", font=title_font).pack(pady=20)
        tk.Label(self.root, text=f"Richtige Antworten: {self.correct_answers}/{self.num_tasks}", font=title_font).pack(pady=20)
        tk.Button(self.root, text="Zurück zum Start", command=self.show_operation_selection, font=title_font).pack(pady=20)

        self.save_user_data()
        

    def save_user_data(self):
        if self.task_times:
            cursor.execute("SELECT best_time, avg_multiplication_time, avg_division_time, avg_addition_time, avg_subtraction_time FROM users WHERE id = ?", (self.user_id,))
            user_data = cursor.fetchone()

            best_time = user_data[0]
            avg_multiplication_time = user_data[1]
            avg_division_time = user_data[2]
            avg_addition_time = user_data[3]
            avg_subtraction_time = user_data[4]

            avg_time = sum(self.task_times) / len(self.task_times) if self.task_times else None
            if best_time is None or (avg_time is not None and avg_time < best_time):
                best_time = avg_time

            if self.time_by_type["multiplication"]:
                avg_multiplication_time = sum(self.time_by_type["multiplication"]) / len(self.time_by_type["multiplication"])

            if self.time_by_type["division"]:
                avg_division_time = sum(self.time_by_type["division"]) / len(self.time_by_type["division"])

            if self.time_by_type["addition"]:
                avg_addition_time = sum(self.time_by_type["addition"]) / len(self.time_by_type["addition"])

            if self.time_by_type["subtraction"]:
                avg_subtraction_time = sum(self.time_by_type["subtraction"]) / len(self.time_by_type["subtraction"])

            cursor.execute('''
                UPDATE users SET best_time = ?, avg_multiplication_time = ?, avg_division_time = ?, avg_addition_time = ?, avg_subtraction_time = ?
                WHERE id = ?
            ''', (best_time, avg_multiplication_time, avg_division_time, avg_addition_time, avg_subtraction_time, self.user_id))

            conn.commit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MatheTrainerApp(root)
    root.mainloop()