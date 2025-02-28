import tkinter as tk
from tkinter import ttk, messagebox
import joblib
import re
import numpy as np
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
import nltk
import pandas as pd
import preprocessor as p
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import sqlite3

conn = sqlite3.connect('sentimen.db')
nltk.download('punkt')
nltk.download('stopwords')

# Preprocessor
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()
stop_words = set(stopwords.words('indonesian'))

# Load Model dan Vectorizer
model = joblib.load(r'NB2\nbmodel.pkl')
tfidf = joblib.load(r'NB2\tfidf_vect.pkl')


def on_closing():
    if messagebox.askokcancel("Quit", "Apakah Anda yakin ingin keluar?"):
        plt.close('all')
        root.destroy()
        sys.exit()

def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)  # Menghapus URL
    text = re.sub(r'@\w+', '', text) #Menghapus @
    text = re.sub(r'#\w+', '', text)  #Menghapus #
    text = re.sub(r'\d+', '', text) #Menghapus Angka
    text = re.sub(r'[^\w\s]', '', text) #Menghapus Tanda Baca
    text = text.lower()
    words = word_tokenize(text) 
    words = [stemmer.stem(word) for word in words if word not in stop_words]
    return ' '.join(words)

def analyze_sentiment():
    input_text = entry.get("1.0", tk.END).strip()
    if input_text:
        preprocessed_text = clean_text(input_text)
        input_tfidf = tfidf.transform([preprocessed_text])
        prediction = model.predict(input_tfidf)[0]
        confidence = max(model.predict_proba(input_tfidf)[0]) * 100

        insert_data(input_text, preprocessed_text,prediction)

        result_label.config(text=f"Sentimen: {prediction}")
        confidence_label.config(text=f"Confidence: {confidence:.2f}%")
    else:
        messagebox.showwarning("Input Error", "Tolong Masukkan Text")

def create_chart():
    cursor = conn.cursor()
    
    # Ambil jumlah label dari database
    cursor.execute("SELECT label, COUNT(*) FROM tweets GROUP BY label")
    label_counts = cursor.fetchall()
    
    # Jika tidak ada data, tampilkan pesan dan keluar
    if not label_counts:
        messagebox.showwarning("No Data", "Tidak ada data untuk ditampilkan.")
        return
    
    # Pisahkan label dan jumlah
    labels, sizes = zip(*label_counts)
    
    fig, ax = plt.subplots(figsize=(5, 4))
    colors = ['#66c2a5', '#fc8d62', '#8da0cb']

    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    ax.set_title("Distribusi Label Sentimen")

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Menghitung total data dari database
    cursor.execute("SELECT COUNT(*) FROM tweets")
    total_data = cursor.fetchone()[0]

    info_text = "Jumlah Data:\n"
    for label, count in label_counts:
        info_text += f"{label}: {count}\n"
    
    info_text += f"\nTotal Data: {total_data}"
    
    info_label = ttk.Label(chart_frame, text=info_text, justify=tk.LEFT, padding=(10, 10))
    info_label.configure(font=('Helvetica', 12))
    info_label.pack(fill=tk.X)

def insert_data(input_text, cleaned_text, label):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tweets WHERE full_text = ?", (input_text,))
        if cursor.fetchone()[0] > 0:
            print("Error: Data with the same input already exists. Skipping insertion.")
            return
        cursor.execute("INSERT INTO tweets (full_text, tweet_clean, label) VALUES (?, ?, ?)", (input_text, cleaned_text, label))
        conn.commit()
        print("Data inserted successfully.")
    except sqlite3.IntegrityError:
        print("Error: Data with the same input already exists. Skipping insertion.")
    except Exception as e:
        print(f"An error occurred during insertion: {e}")

# Main Window
root = tk.Tk()
root.title("Analisis Sentimen")
root.geometry("600x650")

style = ttk.Style()
style.theme_use('clam')

# Font and Color
style.configure("TLabel", font=('Helvetica', 12))
style.configure("TButton", font=('Helvetica', 12), padding=10)
style.configure("TFrame", background="#f0f0f0")

# Menu Bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

analyze_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Menu", menu=analyze_menu)
analyze_menu.add_command(label="Analisis Sentimen", command=lambda: notebook.select(0))
analyze_menu.add_command(label="Lihat Chart", command=lambda: notebook.select(1))

# Notebook for Tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=20, pady=20)

# Analysis Tab
analyze_frame = ttk.Frame(notebook)
notebook.add(analyze_frame, text="Analisis Sentimen")

# Input Frame
input_frame = ttk.Frame(analyze_frame, style="TFrame")
input_frame.pack(fill='x', padx=15, pady=15)

input_label = ttk.Label(input_frame, text="Masukkan Text:", font=('Helvetica', 14))
input_label.pack(anchor='w', pady=10)

# Custom style for Text widget
entry = tk.Text(input_frame, height=10, width=50, font=('Helvetica', 12),
                wrap=tk.WORD, padx=10, pady=10,
                relief=tk.SOLID, borderwidth=1)
entry.configure(bg="#ffffff", fg="#333333")
entry.pack(fill='x', pady=10)

analyze_button = ttk.Button(analyze_frame, text="Analisis", command=analyze_sentiment,
                            style="TButton")
analyze_button.pack(pady=15)

# Result Frame
result_frame = ttk.Frame(analyze_frame, style="TFrame")
result_frame.pack(fill='x', padx=15, pady=15)

result_title = ttk.Label(result_frame, text="Hasil Analisis:", font=('Helvetica', 14))
result_title.pack(anchor='w', pady=10)

result_label = ttk.Label(result_frame, text="", font=('Helvetica', 12))
result_label.pack(anchor='w', pady=5)

confidence_label = ttk.Label(result_frame, text="", font=('Helvetica', 12))
confidence_label.pack(anchor='w', pady=5)

# Chart Tab
chart_frame = ttk.Frame(notebook, style="TFrame")
notebook.add(chart_frame, text="Chart Klasifikasi")

create_chart()

# Add closing protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()