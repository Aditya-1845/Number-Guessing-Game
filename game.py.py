import tkinter as tk
from tkinter import ttk
import random
import pyttsx3
import os
import time

SCORES_FILE = "scores.txt"

class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("500x500")
        self.root.configure(bg="#f0f0f0")

        self.engine = pyttsx3.init()
        self.user_name = ""
        self.secret_number = 0
        self.attempts = 0
        self.start_time = 0
        self.stats = self.load_scores()
        self.difficulty = "Medium"

        self.themes = {
            "Light": {"bg": "#f0f0f0", "fg": "#000000"},
            "Dark": {"bg": "#2e2e2e", "fg": "#ffffff"}
        }
        self.current_theme = "Light"

        self.create_name_frame()
        self.create_game_frame()
        self.apply_theme()

    def create_name_frame(self):
        self.name_frame = ttk.Frame(self.root)
        self.name_frame.pack(pady=20)

        ttk.Label(self.name_frame, text="Enter your name:", font=("Arial", 14)).pack(pady=5)
        self.name_entry = ttk.Entry(self.name_frame, font=("Arial", 12))
        self.name_entry.pack(pady=5)

        ttk.Label(self.name_frame, text="Select Difficulty:", font=("Arial", 12)).pack(pady=5)
        self.difficulty_var = tk.StringVar(value="Medium")
        self.difficulty_menu = ttk.OptionMenu(self.name_frame, self.difficulty_var, "Medium", "Easy", "Medium", "Hard")
        self.difficulty_menu.pack(pady=5)

        ttk.Label(self.name_frame, text="Select Theme:", font=("Arial", 12)).pack(pady=5)
        self.theme_var = tk.StringVar(value="Light")
        self.theme_menu = ttk.OptionMenu(self.name_frame, self.theme_var, "Light", *self.themes.keys(), command=self.change_theme)
        self.theme_menu.pack(pady=5)

        ttk.Button(self.name_frame, text="Start Game", command=self.start_game).pack(pady=10)
        ttk.Button(self.name_frame, text="View Scores", command=self.view_scores).pack(pady=5)

    def create_game_frame(self):
        self.game_frame = ttk.Frame(self.root)

        self.title_label = ttk.Label(self.game_frame, text="Guess a number", font=("Arial", 14))
        self.title_label.pack(pady=10)

        self.entry = ttk.Entry(self.game_frame, font=("Arial", 12))
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", lambda event: self.check_guess())

        self.result_label = ttk.Label(self.game_frame, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

        self.attempts_label = ttk.Label(self.game_frame, text="Attempts: 0", font=("Arial", 12))
        self.attempts_label.pack(pady=5)

        self.check_button = ttk.Button(self.game_frame, text="Check Guess", command=self.check_guess)
        self.check_button.pack(pady=5)

        self.reset_button = ttk.Button(self.game_frame, text="Restart Game", command=self.reset_game)
        self.reset_button.pack(pady=5)

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])
        for frame in [self.name_frame, self.game_frame]:
            frame.configure(style="TFrame")
            for widget in frame.winfo_children():
                if isinstance(widget, (ttk.Label, ttk.Button)):
                    widget.configure(style="TLabel")

    def change_theme(self, selected_theme):
        self.current_theme = selected_theme
        self.apply_theme()

    def start_game(self):
        name = self.name_entry.get().strip()
        if name == "":
            self.speak("Please enter your name.")
            return

        self.user_name = name
        self.difficulty = self.difficulty_var.get()
        self.secret_number = self.get_random_number()
        self.attempts = 0
        self.start_time = time.time()

        self.name_frame.pack_forget()
        self.game_frame.pack(pady=10)

        self.entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.attempts_label.config(text="Attempts: 0")
        self.entry.config(state='normal')
        self.check_button.config(state='normal')

        welcome_msg = f"Welcome {self.user_name}! Guess a number in {self.difficulty} mode."
        self.title_label.config(text=f"Guess a number between 1 and {self.get_max_number()}")
        self.speak(welcome_msg)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def get_max_number(self):
        return {"Easy": 50, "Medium": 100, "Hard": 500}[self.difficulty]

    def get_random_number(self):
        return random.randint(1, self.get_max_number())

    def generate_hint(self):
        if self.secret_number % 5 == 0:
            return "Hint: The number is divisible by 5."
        elif self.secret_number % 2 == 0:
            return "Hint: The number is even."
        else:
            return f"Hint: The number is between {self.secret_number - 10} and {self.secret_number + 10}."

    def check_guess(self):
        try:
            guess = int(self.entry.get())
            if not 1 <= guess <= self.get_max_number():
                raise ValueError

            self.attempts += 1
            self.attempts_label.config(text=f"Attempts: {self.attempts}")

            if guess < self.secret_number:
                msg = "Too low! Try again."
                self.result_label.config(text=msg, foreground="blue")
                self.speak(msg)
            elif guess > self.secret_number:
                msg = "Too high! Try again."
                self.result_label.config(text=msg, foreground="orange")
                self.speak(msg)
            else:
                time_taken = round(time.time() - self.start_time, 2)
                msg = f"Congratulations {self.user_name}! You guessed it in {self.attempts} tries and {time_taken} seconds."
                self.result_label.config(text=msg, foreground="green")
                self.save_score(time_taken)
                self.speak(msg)
                self.show_stats()
                self.entry.config(state='disabled')
                self.check_button.config(state='disabled')
                return

            if self.attempts == 3:
                hint = self.generate_hint()
                self.result_label.config(text=self.result_label.cget("text") + f"\n{hint}")
                self.speak(hint)

        except ValueError:
            msg = f"Please enter a valid number between 1 and {self.get_max_number()}."
            self.result_label.config(text=msg, foreground="red")
            self.speak(msg)

    def reset_game(self):
        self.secret_number = self.get_random_number()
        self.attempts = 0
        self.start_time = time.time()
        self.entry.config(state='normal')
        self.check_button.config(state='normal')
        self.entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.attempts_label.config(text="Attempts: 0")
        self.title_label.config(text=f"Guess a number between 1 and {self.get_max_number()}")
        self.speak(f"{self.user_name}, new game started. Guess a number between 1 and {self.get_max_number()}.")

    def show_stats(self):
        if self.user_name in self.stats:
            attempts, time_taken = self.stats[self.user_name]
            stats_msg = f"\n{self.user_name}'s best: {attempts} attempts in {time_taken} seconds."
            self.result_label.config(text=self.result_label.cget("text") + stats_msg)

    def load_scores(self):
        stats = {}
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, "r") as file:
                for line in file:
                    if ":" in line:
                        parts = line.strip().split(":")
                        if len(parts) == 3:
                            name = parts[0].strip()
                            attempts = int(parts[1].strip())
                            time_taken = float(parts[2].strip())
                            stats[name] = (attempts, time_taken)
        return stats

    def save_score(self, time_taken):
        if (self.user_name not in self.stats or 
            self.attempts < self.stats[self.user_name][0] or 
            (self.attempts == self.stats[self.user_name][0] and time_taken < self.stats[self.user_name][1])):
            self.stats[self.user_name] = (self.attempts, time_taken)
            with open(SCORES_FILE, "w") as file:
                for name, (attempt, time_taken) in self.stats.items():
                    file.write(f"{name}: {attempt}: {time_taken}\n")

    def view_scores(self):
        scores_text = ""
        if self.stats:
            for name, (attempts, time_taken) in sorted(self.stats.items(), key=lambda x: (x[1][0], x[1][1])):
                scores_text += f"{name}: {attempts} attempts in {time_taken} seconds\n"
        else:
            scores_text = "No scores recorded yet."

        top = tk.Toplevel(self.root)
        top.title("Past Scores")
        top.geometry("300x250")
        top.configure(bg="#ffffff")
        ttk.Label(top, text="Past Scores", font=("Arial", 14, "bold"), background="#ffffff").pack(pady=10)
        ttk.Label(top, text=scores_text, font=("Arial", 12), justify="left", background="#ffffff").pack(padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()
