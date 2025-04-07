import customtkinter as ctk

# Set appearance mode and color theme
ctk.set_appearance_mode("system")  # System follows OS theme
ctk.set_default_color_theme("blue")

# Define colors - Modern, vibrant palette
BACKGROUND_COLOR = "#f0f2f5"
PRIMARY_COLOR = "#3b82f6"
POSITIVE_COLOR = "#10b981"
NEUTRAL_COLOR = "#6366f1"
NEGATIVE_COLOR = "#ef4444"
TEXT_COLOR = "#1e293b"
PLACEHOLDER_COLOR = "#64748b"  # Darker gray for placeholder

# Create the main window
window = ctk.CTk()
window.title("Mood Analyzer")
window.geometry("900x550")
window.minsize(800, 500)
window.configure(fg_color=BACKGROUND_COLOR)

# Configure grid
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)

# Placeholder function for sentiment analysis
def analyze_text():
    # Get input text
    text = input_box.get("1.0", "end-1c").strip()
    if not text or text == "Type something here...":
        return
    
    # For demo purposes, we'll just update the UI with placeholder results
    # In a real app, this would call your sentiment analysis function
    
    # Update the category (randomly for demo)
    import random
    categories = ["Positive", "Neutral", "Negative"]
    colors = [POSITIVE_COLOR, NEUTRAL_COLOR, NEGATIVE_COLOR]
    emojis = ["😊", "😐", "😟"]
    
    # Pick a random result for demonstration
    index = random.randint(0, 2)
    category = categories[index]
    color = colors[index]
    emoji = emojis[index]
    confidence = random.randint(50, 100)
    
    # Update UI
    result_emoji.configure(text=emoji)
    result_category.configure(text=category, text_color=color)
    confidence_bar.configure(progress_color=color)
    confidence_bar.set(confidence / 100)
    confidence_percent.configure(text=f"{confidence}%", text_color=color)

# Create left frame (input)
input_frame = ctk.CTkFrame(window, corner_radius=20, fg_color="white", border_width=0)
input_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")

# Configure input frame
input_frame.grid_columnconfigure(0, weight=1)
input_frame.grid_rowconfigure(2, weight=1)

# Input header
input_header = ctk.CTkLabel(
    input_frame,
    text="What's on your mind?",
    font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
    text_color=TEXT_COLOR
)
input_header.grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")

# Input subheader
input_subheader = ctk.CTkLabel(
    input_frame,
    text="Express yourself and I'll analyze the mood",
    font=ctk.CTkFont(family="Helvetica", size=14),
    text_color="#64748b"
)
input_subheader.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="w")

# Text input with improved visibility
input_box = ctk.CTkTextbox(
    input_frame,
    font=ctk.CTkFont(family="Helvetica", size=16),
    corner_radius=15,
    border_width=0,
    fg_color="#f8fafc",
    text_color=PLACEHOLDER_COLOR,  # Start with placeholder color
)
input_box.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
input_box.insert("1.0", "Type something here...")

# Flag to track if we're showing placeholder text
is_placeholder = True

# Handle focus in - clear placeholder and set text to black
def on_focus_in(event):
    global is_placeholder
    if is_placeholder:
        input_box.delete("1.0", "end")
        input_box.configure(text_color=TEXT_COLOR)  # Change to black text
        is_placeholder = False

# Handle focus out - restore placeholder if empty
def on_focus_out(event):
    global is_placeholder
    if input_box.get("1.0", "end-1c").strip() == "":
        input_box.delete("1.0", "end")
        input_box.insert("1.0", "Type something here...")
        input_box.configure(text_color=PLACEHOLDER_COLOR)  # Change to placeholder color
        is_placeholder = True

# Handle key press - ensure text stays black when typing
def on_key_press(event):
    global is_placeholder
    if is_placeholder:
        input_box.delete("1.0", "end")
        input_box.configure(text_color=TEXT_COLOR)  # Change to black text
        is_placeholder = False

# Bind events to the text box
input_box.bind("<FocusIn>", on_focus_in)
input_box.bind("<FocusOut>", on_focus_out)
input_box.bind("<Key>", on_key_press)

# Analyze button
analyze_button = ctk.CTkButton(
    input_frame,
    text="Analyze Mood",
    font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
    corner_radius=30,
    height=50,
    fg_color=PRIMARY_COLOR,
    hover_color="#2563eb",
    command=analyze_text
)
analyze_button.grid(row=3, column=0, padx=20, pady=(10, 25), sticky="ew")

# Create right frame (results)
result_frame = ctk.CTkFrame(window, corner_radius=20, fg_color="white", border_width=0)
result_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")

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

# Separator
separator = ctk.CTkFrame(table_frame, height=1, fg_color="#cbd5e1")
separator.pack(fill="x", padx=15, pady=5)

# Table rows - Placeholder data
categories = [
    ("Positive", "0%", POSITIVE_COLOR),
    ("Neutral", "0%", NEUTRAL_COLOR),
    ("Negative", "0%", NEGATIVE_COLOR)
]

for category, confidence, color in categories:
    row_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
    row_frame.pack(fill="x", padx=15, pady=5)
    
    category_label = ctk.CTkLabel(
        row_frame,
        text=category,
        font=ctk.CTkFont(family="Helvetica", size=14),
        text_color=color
    )
    category_label.pack(side="left", padx=(0, 50))
    
    confidence_label = ctk.CTkLabel(
        row_frame,
        text=confidence,
        font=ctk.CTkFont(family="Helvetica", size=14),
        text_color=TEXT_COLOR
    )
    confidence_label.pack(side="left")

# Run the application
if __name__ == "__main__":
    # Initialize with empty progress
    confidence_bar.set(0)
    window.mainloop()