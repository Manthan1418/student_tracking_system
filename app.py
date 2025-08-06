import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from collections import defaultdict

expenses = []

# Function to add expense
def add_expense():
    date = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()
    note = note_entry.get()

    if not date or not category or not amount:
        messagebox.showerror("Error", "All fields except note are required!")
        return

    try:
        amt = float(amount)
    except:
        messagebox.showerror("Error", "Amount must be a number")
        return

    expenses.append([date, category, amt, note])
    tree.insert("", "end", values=(date, category, amt, note))
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    note_entry.delete(0, tk.END)

# Show summary chart
def show_summary():
    if not expenses:
        messagebox.showinfo("Info", "No data to show")
        return

    totals = defaultdict(float)
    for exp in expenses:
        totals[exp[1]] += exp[2]

    plt.figure(figsize=(5,5))
    plt.pie(totals.values(), labels=totals.keys(), autopct="%1.1f%%")
    plt.title("Expenses by Category")
    plt.show()

# Export to CSV
def export_csv():
    if not expenses:
        messagebox.showinfo("Info", "No data to export")
        return
    file = filedialog.asksaveasfilename(defaultextension=".csv",
                                        filetypes=[("CSV files","*.csv")])
    if file:
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Note"])
            writer.writerows(expenses)
        messagebox.showinfo("Success", "Data exported successfully")

# GUI
root = tk.Tk()
root.title("Student Expense Tracker")
root.geometry("800x600")
root.config(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#2d2d2d", 
                foreground="white", rowheight=25, fieldbackground="#2d2d2d")
style.map("Treeview", background=[("selected", "#4CAF50")])

# Input frame
frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(pady=10)

tk.Label(frame, text="Date (YYYY-MM-DD)", fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=5)
date_entry = ttk.Entry(frame)
date_entry.grid(row=0, column=1, padx=5)
date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

tk.Label(frame, text="Category", fg="white", bg="#1e1e1e").grid(row=0, column=2, padx=5)
category_entry = ttk.Entry(frame)
category_entry.grid(row=0, column=3, padx=5)

tk.Label(frame, text="Amount", fg="white", bg="#1e1e1e").grid(row=0, column=4, padx=5)
amount_entry = ttk.Entry(frame)
amount_entry.grid(row=0, column=5, padx=5)

tk.Label(frame, text="Note", fg="white", bg="#1e1e1e").grid(row=0, column=6, padx=5)
note_entry = ttk.Entry(frame)
note_entry.grid(row=0, column=7, padx=5)

add_btn = tk.Button(frame, text="Add Expense", command=add_expense, bg="#4CAF50", fg="white")
add_btn.grid(row=0, column=8, padx=10)

# Treeview
columns = ("Date", "Category", "Amount", "Note")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Buttons at bottom
btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Show Summary", command=show_summary, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Export CSV", command=export_csv, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)

root.mainloop()
