import customtkinter as ctk
import joblib
import re
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
import nltk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3

#Database
conn = sqlite3.connect('sentimen.db')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# Preprocessor
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()
stop_words = set(stopwords.words('indonesian'))

# Model
model = joblib.load(r'Model\best_model.pkl')

# Insert Data
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

# Clean Data
def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)   # Menghapus URL
    text = re.sub(r'@\w+', '', text) # Menghapus mention (@username)
    text = re.sub(r'#\w+', '', text) # Menghapus hashtag (#hashtag)
    text = re.sub(r'\d+', '', text) # Menghapus angka
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    words = word_tokenize(text) #Tokenisasi
    words = [word for word in words if word not in stop_words]
    words = [stemmer.stem(word) for word in words]
    return ' '.join(words)

# Update Chart
def update_chart():
    chart_ax.clear()
    cursor = conn.cursor()
    cursor.execute("SELECT label, COUNT(*) FROM tweets GROUP BY label")
    label_counts = cursor.fetchall()

    sentiment_data = {label: count for label, count in label_counts}

    categories = ["positive", "neutral", "negative"]
    values = [sentiment_data.get(cat, 0) for cat in categories]
    colors = [POSITIVE_COLOR, NEUTRAL_COLOR, NEGATIVE_COLOR]
    
    cats = ["Positive", "Neutral", "Negative"]
    bars = chart_ax.bar(cats, values, color=colors, width=0.6)
    
    chart_ax.set_title("Sentiment Distribution", fontsize=16, color=TEXT_COLOR, pad=20)
    chart_ax.set_ylabel("Jumlah Sentimen", fontsize=12, color=TEXT_COLOR)
    
    for bar in bars:
        height = bar.get_height()
        chart_ax.text(
            bar.get_x() + bar.get_width()/2.,
            height + 0.3,
            f'{height:.0f}',
            ha='center', 
            va='bottom',
            color=TEXT_COLOR,
            fontsize=12,
            fontweight='bold',
            fontfamily='sans-serif'
        )
    
    chart_ax.set_facecolor("#f8fafc")
    chart_fig.patch.set_facecolor("#f8fafc")
    for spine in chart_ax.spines.values():
        spine.set_visible(False)
    
    chart_ax.grid(axis='y', linestyle='--', alpha=0.3)
    chart_ax.set_ylim(bottom=0)
    chart_fig.tight_layout(pad=3.0)
    chart_canvas.draw()

# Analyze Sentiment
def analyze_text():
    text = input_box.get("1.0", "end-1c").strip()
    if not text or text == "Type something here...":
        return
    prep_text = clean_text(text)

    # Predict sentiment 
    prediction = model.predict([prep_text])[0]
    probabilities = model.predict_proba([prep_text])[0]
    #Input Data ke Database
    insert_data(text, prep_text, prediction)
    # Kategori Sentimen
    categories = ["negative", "neutral", "positive"]
    colors = [NEGATIVE_COLOR, NEUTRAL_COLOR, POSITIVE_COLOR]
    emojis = ["😟", "😐", "😊"]

    index = categories.index(prediction)
    color = colors[index]
    emoji = emojis[index]

    # Confidence score
    neg_conf, neu_conf, pos_conf = [round(p * 100, 2) for p in probabilities]
    confidence = max(neg_conf, neu_conf, pos_conf)
    
    # Update UI
    result_emoji.configure(text=emoji)
    result_category.configure(text=prediction, text_color=color)
    confidence_bar.configure(progress_color=color)
    confidence_bar.set(confidence / 100)
    confidence_percent.configure(text=f"{confidence}%", text_color=color)

    positive_confidence.configure(text=f"{pos_conf:.1f}%")
    neutral_confidence.configure(text=f"{neu_conf:.1f}%")
    negative_confidence.configure(text=f"{neg_conf:.1f}%")

# Set Tampilan dan Warna Tema
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# Color Palet Model
BACKGROUND_COLOR = "#f0f2f5"
PRIMARY_COLOR = "#3b82f6"
POSITIVE_COLOR = "#10b981"
NEUTRAL_COLOR = "#6366f1"
NEGATIVE_COLOR = "#ef4444"
TEXT_COLOR = "#1e293b"
PLACEHOLDER_COLOR = "#64748b"

# Main Window
window = ctk.CTk()
window.title("Sentiment Analyzer")
window.geometry("900x550")
window.minsize(800, 500)
window.configure(fg_color=BACKGROUND_COLOR)

# Configure grid
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)


# Frame untuk Konten dan Chart
analysis_content = ctk.CTkFrame(window, fg_color="transparent")
chart_content = ctk.CTkFrame(window, fg_color="transparent")

# Active View saat ini
current_view = "analysis"

# Switch view
def switch_to_view(view):
    global current_view
    current_view = view
    
    # Update button
    if view == "analysis":
        analysis_btn.configure(
            fg_color=PRIMARY_COLOR,
            text_color="white",
            hover_color="#2563eb"
        )
        chart_btn.configure(
            fg_color="transparent",
            text_color=TEXT_COLOR,
            hover_color="#e2e8f0"
        )
        # Show analysis content
        chart_content.pack_forget()
        analysis_content.pack(fill="both", expand=True, padx=20, pady=(10, 20))
    else:
        chart_btn.configure(
            fg_color=PRIMARY_COLOR,
            text_color="white",
            hover_color="#2563eb"
        )
        analysis_btn.configure(
            fg_color="transparent",
            text_color=TEXT_COLOR,
            hover_color="#e2e8f0"
        )
        # Show chart content
        analysis_content.pack_forget()
        chart_content.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        # Update Chart
        update_chart()

# Menu Bar
menu_frame = ctk.CTkFrame(window, fg_color="white", corner_radius=20, height=60)
menu_frame.pack(padx=20, pady=(20, 10), anchor="center")

# Container menu
buttons_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
buttons_frame.pack(pady=10)

# Analysis button
analysis_btn = ctk.CTkButton(
    buttons_frame,
    text="Analysis",
    font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
    corner_radius=25,
    fg_color=PRIMARY_COLOR,
    text_color="white",
    hover_color="#2563eb",
    height=40,
    width=120,
    command=lambda: switch_to_view("analysis")
)
analysis_btn.pack(side="left", padx=10)

# Chart Button
chart_btn = ctk.CTkButton(
    buttons_frame,
    text="Chart",
    font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
    corner_radius=25,
    fg_color="transparent",
    text_color=TEXT_COLOR,
    hover_color="#e2e8f0",
    height=40,
    width=120,
    command=lambda: switch_to_view("chart")
)
chart_btn.pack(side="left", padx=10)

# ===== Section Menu Utama (Input + Hasil) Analisis=====
analysis_content.grid_columnconfigure(0, weight=5)
analysis_content.grid_columnconfigure(1, weight=1)
analysis_content.grid_rowconfigure(0, weight=1)

# Frame kiri(input)
input_frame = ctk.CTkFrame(analysis_content, corner_radius=20, fg_color="white", border_width=0)
input_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

# Configure input frame
input_frame.grid_columnconfigure(0, weight=1)
input_frame.grid_rowconfigure(2, weight=1)

#header
input_header = ctk.CTkLabel(
    input_frame,
    text="What's on your mind?",
    font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
    text_color=TEXT_COLOR
)
input_header.grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")

#subheader
input_subheader = ctk.CTkLabel(
    input_frame,
    text="Masukkan Teks, untuk di analisis sentimennya!",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color="#64748b"
)
input_subheader.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="w")

# Text input
input_box = ctk.CTkTextbox(
    input_frame,
    font=ctk.CTkFont(family="Helvetica", size=16),
    corner_radius=15,
    border_width=0,
    fg_color="#f8fafc",
    text_color=PLACEHOLDER_COLOR,
)
input_box.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
input_box.insert("1.0", "Type something here...")

is_placeholder = True

# Focus = Clear Placeholder
def on_focus_in(event):
    global is_placeholder
    if is_placeholder:
        input_box.delete("1.0", "end")
        input_box.configure(text_color=TEXT_COLOR)
        is_placeholder = False

# Focus Out = Show Placeholder
def on_focus_out(event):
    global is_placeholder
    if input_box.get("1.0", "end-1c").strip() == "":
        input_box.delete("1.0", "end")
        input_box.insert("1.0", "Type something here...")
        input_box.configure(text_color=PLACEHOLDER_COLOR) 
        is_placeholder = True

# Warna Text
def on_key_press(event):
    global is_placeholder
    if is_placeholder:
        input_box.delete("1.0", "end")
        input_box.configure(text_color=TEXT_COLOR)
        is_placeholder = False

# Bind Function/Event ke input Box
input_box.bind("<FocusIn>", on_focus_in)
input_box.bind("<FocusOut>", on_focus_out)
input_box.bind("<Key>", on_key_press)

# Analyze button
analyze_button = ctk.CTkButton(
    input_frame,
    text="Analyze Sentiment",
    font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
    corner_radius=30,
    height=50,
    fg_color=PRIMARY_COLOR,
    hover_color="#2563eb",
    command=analyze_text
)
analyze_button.grid(row=3, column=0, padx=20, pady=(10, 25), sticky="ew")

# Frame Kiri (results)
result_frame = ctk.CTkFrame(analysis_content, corner_radius=20, fg_color="white", border_width=0)
result_frame.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")

# Configure result frame
result_frame.grid_columnconfigure(0, weight=1)
result_frame.grid_rowconfigure(3, weight=1)

# Result header
result_header = ctk.CTkLabel(
    result_frame,
    text="Analysis Result",
    font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
    text_color=TEXT_COLOR
)
result_header.grid(row=0, column=0, padx=25, pady=(25, 20), sticky="w")

# Emoji and category frame
emoji_category_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
emoji_category_frame.grid(row=1, column=0, padx=25, pady=(10, 20), sticky="ew")

# Result emoji
result_emoji = ctk.CTkLabel(
    emoji_category_frame,
    text="😶",
    font=ctk.CTkFont(size=60),
)
result_emoji.grid(row=0, column=0, padx=(0, 15))

# Result category
result_category = ctk.CTkLabel(
    emoji_category_frame,
    text="Waiting for input...",
    font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
    text_color=NEUTRAL_COLOR
)
result_category.grid(row=0, column=1, sticky="w")

# Confidence section
confidence_section = ctk.CTkFrame(result_frame, fg_color="transparent")
confidence_section.grid(row=2, column=0, padx=25, pady=(0, 20), sticky="ew")
confidence_section.grid_columnconfigure(1, weight=1)

# Confidence label
confidence_label = ctk.CTkLabel(
    confidence_section,
    text="Confidence:",
    font=ctk.CTkFont(family="Helvetica", size=16),
    text_color=TEXT_COLOR
)
confidence_label.grid(row=0, column=0, sticky="w")

# Confidence bar
confidence_bar = ctk.CTkProgressBar(
    confidence_section,
    height=15,
    corner_radius=10,
    progress_color=NEUTRAL_COLOR,
    fg_color="#e2e8f0"
)
confidence_bar.grid(row=0, column=1, padx=(15, 15), sticky="ew")
confidence_bar.set(0)

# Confidence percentage
confidence_percent = ctk.CTkLabel(
    confidence_section,
    text="0%",
    font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
    text_color=NEUTRAL_COLOR
)
confidence_percent.grid(row=0, column=2)

# Add results table
table_frame = ctk.CTkFrame(result_frame, fg_color="#f8fafc", corner_radius=15)
table_frame.grid(row=3, column=0, padx=25, pady=(0, 25), sticky="nsew")

# Table headers
header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
header_frame.pack(fill="x", padx=15, pady=(15, 5))

#Kategori Sentimen
category_header = ctk.CTkLabel(
    header_frame,
    text="Category",
    font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
    text_color=TEXT_COLOR
)
category_header.pack(side="left", padx=(0, 50))

confidence_header = ctk.CTkLabel(
    header_frame,
    text="Confidence",
    font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
    text_color=TEXT_COLOR
)
confidence_header.pack(side="left")

# Pemisah
separator = ctk.CTkFrame(table_frame, height=1, fg_color="#cbd5e1")
separator.pack(fill="x", padx=15, pady=5)

# Positive
positive_row_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
positive_row_frame.pack(fill="x", padx=15, pady=5)

positive_label = ctk.CTkLabel(
    positive_row_frame,
    text="Positive",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color=POSITIVE_COLOR
)
positive_label.pack(side="left", padx=(0, 50))

positive_confidence = ctk.CTkLabel(
    positive_row_frame,
    text="0%",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color=TEXT_COLOR
)
positive_confidence.pack(side="left")

# Neutral
neutral_row_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
neutral_row_frame.pack(fill="x", padx=15, pady=5)

neutral_label = ctk.CTkLabel(
    neutral_row_frame,
    text="Neutral",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color=NEUTRAL_COLOR
)
neutral_label.pack(side="left", padx=(0, 50))

neutral_confidence = ctk.CTkLabel(
    neutral_row_frame,
    text="0%",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color=TEXT_COLOR
)
neutral_confidence.pack(side="left")

# Negative
negative_row_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
negative_row_frame.pack(fill="x", padx=15, pady=5)

negative_label = ctk.CTkLabel(
    negative_row_frame,
    text="Negative",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color=NEGATIVE_COLOR
)
negative_label.pack(side="left", padx=(0, 50))

negative_confidence = ctk.CTkLabel(
    negative_row_frame,
    text="0%",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color=TEXT_COLOR
)
negative_confidence.pack(side="left")

# ===== CHART SECTION =====
chart_frame = ctk.CTkFrame(chart_content, corner_radius=20, fg_color="white", border_width=0)
chart_frame.pack(fill="both", expand=True, padx=0, pady=0)

# Chart header
chart_header = ctk.CTkLabel(
    chart_frame,
    text="Sentiment Distribution",
    font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
    text_color=TEXT_COLOR
)
chart_header.pack(pady=(25, 5))

# Chart description
chart_description = ctk.CTkLabel(
    chart_frame,
    text="Visual representation of sentiment analysis results",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color="#64748b"
)
chart_description.pack(pady=(0, 20))

# Matplotlib Figure
chart_fig = plt.Figure(figsize=(8, 5), dpi=100)
chart_ax = chart_fig.add_subplot(111)
chart_canvas = FigureCanvasTkAgg(chart_fig, master=chart_frame)
chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 25))

# Panggil Chart
update_chart()

# Highlight Active Menu
switch_to_view("analysis")

# Run
if __name__ == "__main__":
    confidence_bar.set(0)
    window.mainloop()