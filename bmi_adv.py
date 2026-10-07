import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv

COLORS = {
    "background": "#F5F7F4",
    "header": "#82BDBB",
    "header_title": "#123B69",
    "header_subtitle": "#E4F4F0",
    "card": "#B2E4D4",
    "card_border": "#9CD8C8",
    "input": "#F1FAF7",
    "input_border": "#B7D2CC",
    "text": "#263238",
    "muted": "#64748B",
    "white": "#FFFFFF",
    "accent": "#2D60CE",
    "accent_hover": "#214EAE",
}


def create_database():
    try:
        connection = sqlite3.connect("bmi_data.db")
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not create database.\n\n{error}"
        )


def calculate_bmi():
    try:
        name = name_entry.get().strip()
        weight = float(weight_entry.get())
        height = float(height_entry.get())

        if name == "":
            messagebox.showerror(
                "Missing Name",
                "Please enter your name."
            )
            return

        if weight <= 0:
            messagebox.showerror(
                "Invalid Weight",
                "Please enter a positive weight."
            )
            return

        if height <= 0:
            messagebox.showerror(
                "Invalid Height",
                "Please enter a positive height."
            )
            return

        bmi = weight / (height ** 2)

        if bmi < 18.5:
            category = "Underweight"
            result_color = "#f59e0b"
        elif bmi < 25:
            category = "Normal"
            result_color = "#16a34a"
        elif bmi < 30:
            category = "Overweight"
            result_color = "#f59e0b"
        else:
            category = "Obese"
            result_color = "#dc2626"

        result_label.config(
            text=f"Hello, {name}!\nBMI: {bmi:.2f}\nCategory: {category}",
            fg=result_color
        )

        connection = sqlite3.connect("bmi_data.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO bmi_records
            (name, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
        """, (name, weight, height, bmi, category))

        connection.commit()
        connection.close()

        name_entry.delete(0, tk.END)
        weight_entry.delete(0, tk.END)
        height_entry.delete(0, tk.END)

        

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter numbers only for weight and height."
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not save the record.\n\n{error}"
        )


def show_history():
    history_window = tk.Toplevel(window)
    history_window.title("BMI History")
    history_window.geometry("800x500")
    history_window.configure(bg="#f8fafc")

    title = tk.Label(
        history_window,
        text="BMI History",
        font=("Arial", 20, "bold"),
        bg="#f8fafc",
        fg="#0f172a"
    )
    title.pack(pady=(15, 5))

    search_frame = tk.Frame(
        history_window,
        bg="#f8fafc"
    )
    search_frame.pack(pady=5)

    search_label = tk.Label(
        search_frame,
        text="Search User:",
        font=("Arial", 11, "bold"),
        bg="#f8fafc",
        fg="#334155"
    )
    search_label.pack(side="left", padx=5)

    search_entry = tk.Entry(
        search_frame,
        width=25,
        font=("Arial", 11),
        relief="solid",
        bd=1
    )
    search_entry.pack(side="left", padx=5)

    scrollbar = tk.Scrollbar(history_window)
    scrollbar.pack(side="right", fill="y")

    history_text = tk.Text(
        history_window,
        yscrollcommand=scrollbar.set,
        font=("Consolas", 10),
        bg="white",
        fg="#1e293b",
        relief="solid",
        bd=1
    )
    history_text.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    scrollbar.config(command=history_text.yview)

    def load_records():
        history_text.config(state="normal")
        history_text.delete("1.0", tk.END)

        try:
            connection = sqlite3.connect("bmi_data.db")
            cursor = connection.cursor()

            user_name = search_entry.get().strip()

            if user_name:
                cursor.execute("""
                    SELECT name, bmi, category, date
                    FROM bmi_records
                    WHERE name LIKE ?
                    ORDER BY id DESC
                """, (f"%{user_name}%",))
            else:
                cursor.execute("""
                    SELECT name, bmi, category, date
                    FROM bmi_records
                    ORDER BY id DESC
                    LIMIT 50
                """)

            records = cursor.fetchall()
            connection.close()

            history_text.insert(
                "end",
                "Name\tBMI\tCategory\tDate\n"
            )
            history_text.insert(
                "end",
                "-" * 90 + "\n"
            )

            for record in records:
                history_text.insert(
                    "end",
                    f"{record[0]}\t"
                    f"{record[1]:.2f}\t"
                    f"{record[2]}\t"
                    f"{record[3]}\n"
                )

            history_text.config(state="disabled")

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

    search_button = tk.Button(
        search_frame,
        text="Search",
        font=("Arial", 10, "bold"),
        bg="#2563eb",
        fg="white",
        activebackground="#1d4ed8",
        activeforeground="white",
        relief="flat",
        padx=15,
        pady=5,
        cursor="hand2",
        command=load_records
    )
    search_button.pack(side="left", padx=5)

    load_records()


def show_graph():
    try:
        user_name = name_entry.get().strip()

        if user_name == "":
            messagebox.showerror(
                "Missing Name",
                "Please enter your name first."
            )
            return

        connection = sqlite3.connect("bmi_data.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT bmi, date
            FROM bmi_records
            WHERE name LIKE ?
            ORDER BY id ASC
        """, (f"%{user_name}%",))

        records = cursor.fetchall()
        connection.close()

        if not records:
            messagebox.showinfo(
                "No Data",
                f"No BMI records found for {user_name}."
            )
            return

        bmi_values = []
        dates = []

        for record in records:
            bmi_values.append(record[0])
            dates.append(
                datetime.datetime.strptime(
                    record[1],
                    "%Y-%m-%d %H:%M:%S"
                )
            )

        plt.figure(figsize=(9, 5))

        plt.plot(
            dates,
            bmi_values,
            marker="o",
            linewidth=2,
            label="BMI"
        )

        for date, bmi in zip(dates, bmi_values):
            plt.annotate(
                f"{bmi:.2f}",
                (date, bmi),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center"
            )

        plt.axhline(y=18.5, linestyle="--", linewidth=1)
        plt.axhline(y=25, linestyle="--", linewidth=1)
        plt.axhline(y=30, linestyle="--", linewidth=1)

        plt.text(dates[0], 18.5, " Underweight", va="bottom")
        plt.text(dates[0], 25, " Normal", va="bottom")
        plt.text(dates[0], 30, " Overweight", va="bottom")

        plt.title(
            f"BMI Trend - {user_name}",
            fontsize=16,
            fontweight="bold"
        )

        plt.xlabel("Date", fontsize=11)
        plt.ylabel("BMI", fontsize=11)

        plt.gca().xaxis.set_major_formatter(
            mdates.DateFormatter("%b %d")
        )

        plt.xticks(rotation=45, ha="right")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except ValueError:
        messagebox.showerror(
            "Date Error",
            "Could not process the date data."
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not load BMI data.\n\n{error}"
        )


def clear_database():
    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure?\n\n"
        "All BMI records will be permanently deleted."
    )

    if not confirm:
        return

    try:
        connection = sqlite3.connect("bmi_data.db")
        cursor = connection.cursor()

        cursor.execute("DELETE FROM bmi_records")

        connection.commit()
        connection.close()

        messagebox.showinfo(
            "Success",
            "All BMI records have been deleted."
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not delete records.\n\n{error}"
        )


def export_to_csv():
    try:
        connection = sqlite3.connect("bmi_data.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name, weight, height, bmi, category, date
            FROM bmi_records
        """)

        records = cursor.fetchall()
        connection.close()

        if not records:
            messagebox.showinfo(
                "No Data",
                "No records found to export."
            )
            return

        with open(
            "bmi_export.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Name",
                "Weight",
                "Height",
                "BMI",
                "Category",
                "Date"
            ])

            writer.writerows(records)

        messagebox.showinfo(
            "Success",
            "Data exported successfully!\n\n"
            "File: bmi_export.csv"
        )

    except Exception as error:
        messagebox.showerror(
            "Export Error",
            str(error)
        )


window = tk.Tk()
window.title("BMI Calculator")
window.iconbitmap("icon.ico")
window.geometry("520x720")
window.resizable(False, False)
window.configure(bg=COLORS["background"])


header_frame = tk.Frame(
    window,
    bg=COLORS["header"],
    height=120
)
header_frame.pack(
    fill="x"
)

title_label = tk.Label(
    header_frame,
    text="BMI Calculator",
    font=("Arial", 25, "bold"),
    bg=COLORS["header"],
    fg=COLORS["header_title"],
    anchor="center"
)
title_label.pack(fill="x", pady=(20, 3))

subtitle_label = tk.Label(
    header_frame,
    text="Calculate your Body Mass Index",
    font=("Arial", 11),
    bg=COLORS["header"],
    fg=COLORS["header_subtitle"]
)
subtitle_label.pack(fill="x")


input_card = tk.Frame(
    window,
    bg=COLORS["card"],
    bd=0,
    highlightthickness=1,
    highlightbackground=COLORS["card_border"]
)
input_card.pack(
    padx=30,
    pady=20,
    fill="x"
)
input_card.grid_columnconfigure(0, weight=1)
input_card.grid_columnconfigure(1, weight=1)

input_title = tk.Label(
    input_card,
    text="Enter Your Details",
    font=("Arial", 15, "bold"),
    bg=COLORS["card"],
    fg=COLORS["header_title"],
    anchor="center"
)
input_title.grid(
    row=0,
    column=0,
    columnspan=2,
    pady=(15, 10),
    sticky="ew"
)


name_label = tk.Label(
    input_card,
    text="Name",
    font=("Arial", 11, "bold"),
    bg=COLORS["card"],
    fg=COLORS["text"]
)
name_label.grid(
    row=1,
    column=0,
    padx=15,
    pady=8,
    sticky="w"
)

name_entry = tk.Entry(
    input_card,
    width=22,
    font=("Arial", 11),
    bg=COLORS["input"],
    fg=COLORS["text"],
    insertbackground=COLORS["text"],
    relief="flat",
    bd=0,
    highlightthickness=1,
    highlightbackground=COLORS["input_border"],
    highlightcolor=COLORS["header"]
)
name_entry.grid(
    row=1,
    column=1,
    padx=15,
    pady=8
)


weight_label = tk.Label(
    input_card,
    text="Weight (kg)",
    font=("Arial", 11, "bold"),
    bg=COLORS["card"],
    fg=COLORS["text"]
)
weight_label.grid(
    row=2,
    column=0,
    padx=15,
    pady=8,
    sticky="w"
)

weight_entry = tk.Entry(
    input_card,
    width=22,
    font=("Arial", 11),
    bg=COLORS["input"],
    fg=COLORS["text"],
    insertbackground=COLORS["text"],
    relief="flat",
    bd=0,
    highlightthickness=1,
    highlightbackground=COLORS["input_border"],
    highlightcolor=COLORS["header"]
)
weight_entry.grid(
    row=2,
    column=1,
    padx=15,
    pady=8
)


height_label = tk.Label(
    input_card,
    text="Height (m)",
    font=("Arial", 11, "bold"),
    bg=COLORS["card"],
    fg=COLORS["text"]
)
height_label.grid(
    row=3,
    column=0,
    padx=15,
    pady=8,
    sticky="w"
)

height_entry = tk.Entry(
    input_card,
    width=22,
    font=("Arial", 11),
    bg=COLORS["input"],
    fg=COLORS["text"],
    insertbackground=COLORS["text"],
    relief="flat",
    bd=0,
    highlightthickness=1,
    highlightbackground=COLORS["input_border"],
    highlightcolor=COLORS["header"]
)
height_entry.grid(
    row=3,
    column=1,
    padx=15,
    pady=(8, 18)
)


calculate_button = tk.Button(
    window,
    text="Calculate BMI",
    font=("Arial", 12, "bold"),
    bg=COLORS["accent"],
    fg=COLORS["white"],
    activebackground=COLORS["accent_hover"],
    activeforeground=COLORS["white"],
    relief="flat",
    cursor="hand2",
    padx=30,
    pady=10,
    command=calculate_bmi
)
calculate_button.pack(pady=5)


button_frame = tk.Frame(
    window,
    bg=COLORS["background"]
)
button_frame.pack(padx=24, pady=10, fill="x")

for column in range(4):
    button_frame.grid_columnconfigure(column, weight=1, uniform="actions")

history_button = tk.Button(
    button_frame,
    text="View\nHistory",
    font=("Arial", 9, "bold"),
    bg=COLORS["header"],
    fg=COLORS["text"],
    activebackground=COLORS["card_border"],
    activeforeground=COLORS["text"],
    relief="flat",
    cursor="hand2",
    padx=4,
    pady=6,
    command=show_history
)
history_button.grid(row=0, column=0, padx=3, sticky="ew")

graph_button = tk.Button(
    button_frame,
    text="BMI\nGraph",
    font=("Arial", 9, "bold"),
    bg=COLORS["header"],
    fg=COLORS["text"],
    activebackground=COLORS["card_border"],
    activeforeground=COLORS["text"],
    relief="flat",
    cursor="hand2",
    padx=4,
    pady=6,
    command=show_graph
)
graph_button.grid(row=0, column=1, padx=3, sticky="ew")

export_button = tk.Button(
    button_frame,
    text="Export\nCSV",
    font=("Arial", 9, "bold"),
    bg=COLORS["header"],
    fg=COLORS["text"],
    activebackground=COLORS["card_border"],
    activeforeground=COLORS["text"],
    relief="flat",
    cursor="hand2",
    padx=4,
    pady=6,
    command=export_to_csv
)
export_button.grid(row=0, column=2, padx=3, sticky="ew")

clear_button = tk.Button(
    button_frame,
    text="Clear\nData",
    font=("Arial", 9, "bold"),
    bg="#C94A45",
    fg=COLORS["white"],
    activebackground="#B53C37",
    activeforeground=COLORS["white"],
    relief="flat",
    cursor="hand2",
    padx=4,
    pady=6,
    command=clear_database
)
clear_button.grid(row=0, column=3, padx=3, sticky="ew")


result_card = tk.Frame(
    window,
    bg=COLORS["white"],
    highlightthickness=1,
    highlightbackground=COLORS["input_border"]
)
result_card.pack(
    padx=30,
    pady=20,
    fill="x"
)

result_title = tk.Label(
    result_card,
    text="Your Result",
    font=("Arial", 14, "bold"),
    bg=COLORS["white"],
    fg=COLORS["text"]
)
result_title.pack(pady=(12, 5))


result_label = tk.Label(
    result_card,
    text="Enter your details and calculate BMI",
    font=("Arial", 12, "bold"),
    bg=COLORS["white"],
    fg=COLORS["muted"],
    justify="center"
)
result_label.pack(pady=(5, 15))


footer = tk.Label(
    window,
    text="Developed by Sayan Pramanik © 2026",
    font=("Arial", 9)
)

footer.pack(side="bottom", pady=10)

create_database()
window.mainloop()