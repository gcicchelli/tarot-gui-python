import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import random
import ephem
import datetime
import os

# --- Globals --- #
last_reading_type = None
last_reading_cards = []
three_card_widgets = []
single_card_window_id = None
moon_label_id = None
name_label_id = None
meaning_label_id = None
button_frame_id = None
three_card_positions = []  # Store (image, heading, name, meaning) window IDs
x_offsets = [-200, 0, 200]  # same horizontal spread
y_offsets = [40, 0, 40]     # makes the left & right dip, center stays high
y_base = 330

# --- Load deck --- #
with open("tarot_cards.json", "r") as f:
    tarot_deck = json.load(f)

# --- Moon Phase --- #
def get_moon_phase():
    today = ephem.Date(datetime.datetime.now(datetime.timezone.utc))
    tomorrow = ephem.Date(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1))
    moon = ephem.Moon(today)
    moon.compute(today)
    phase_today = moon.phase
    moon.compute(tomorrow)
    phase_tomorrow = moon.phase
    waxing = phase_tomorrow > phase_today

    if phase_today < 1:
        return "🌑 New Moon - Time to set intentions."
    elif phase_today < 49:
        return "🌒 Waxing Crescent - Growth and momentum are building." if waxing else "🌘 Waning Crescent - Rest and prepare for renewal."
    elif phase_today < 51:
        return "🌕 Full Moon - Illumination and fulfillment."
    elif phase_today < 99:
        return "🌔 Waxing Gibbous - Push through to fruition." if waxing else "🌖 Waning Gibbous - Release and reflect."
    else:
        return "🌕 Full Moon - Illumination and fulfillment."

# --- Clear 3-card display --- #
def clear_three_card_spread():
    for widget_id, widget in three_card_widgets:
        try:
            canvas.delete(widget_id)
            widget.destroy()
        except:
            pass
    three_card_widgets.clear()

# --- Draw Single Card --- #
def draw_card():
    clear_three_card_spread()
    canvas.itemconfigure(single_card_window_id, state='normal')
    name_label.config(text="")
    meaning_label.config(text="")
    image_label.config(image="", text="")

    card = random.choice(tarot_deck)
    name_label.config(text=card["name"])
    meaning_label.config(text=card["meaning"])

    try:
        img = Image.open(card["image"]).resize((300, 500))
        card_img = ImageTk.PhotoImage(img)
        image_label.config(image=card_img, text="")
        image_label.image = card_img
    except Exception as e:
        print("Error loading image:", e)
        image_label.config(text="🖼️ Image not found", image="")

    global last_reading_type, last_reading_cards
    last_reading_type = "Single Card"
    last_reading_cards = [card]

# --- Draw Three Cards --- #
def draw_three_cards():
    global last_reading_type, last_reading_cards
    image_label.config(image="", text="")
    canvas.itemconfigure(single_card_window_id, state='hidden')
    name_label.config(text="")
    meaning_label.config(text="")

    clear_three_card_spread()
    three_card_positions.clear()
    cards = random.sample(tarot_deck, 3)

    y_base = 330
    heading_y = [150, 120, 150]
    label_y = [540, 500, 540]
    meaning_y = [570, 530, 570]
    headings = ["Past", "Present", "Future"]

    for i, card in enumerate(cards):
        try:
            canvas_center = canvas.winfo_width() // 2
            x = canvas_center + x_offsets[i]
            y = y_base + y_offsets[i]

            img = Image.open(card["image"]).resize((200, 333))
            card_img = ImageTk.PhotoImage(img)
            image_label_ = tk.Label(canvas, image=card_img, borderwidth=0)
            image_label_.image = card_img
            image_id = canvas.create_window(x, y, window=image_label_)
            three_card_widgets.append((image_id, image_label_))

            heading_label = tk.Label(canvas, text=headings[i], font=("Georgia", 18, "italic"), fg="#2e003e", bg="#FFD700")
            heading_id = canvas.create_window(x, heading_y[i], window=heading_label)
            three_card_widgets.append((heading_id, heading_label))

            name_label_ = tk.Label(canvas, text=card["name"], font=("Georgia", 12, "bold"), fg="#2e003e", bg="#FFD700")
            name_id = canvas.create_window(x, label_y[i], window=name_label_)
            three_card_widgets.append((name_id, name_label_))

            meaning_label_ = tk.Label(canvas, text=card["meaning"], wraplength=160, justify="center", font=("Georgia", 10), fg="#2e003e", bg="#FFD700")
            meaning_id = canvas.create_window(x, meaning_y[i], window=meaning_label_)
            three_card_widgets.append((meaning_id, meaning_label_))

            three_card_positions.append((i, image_id, heading_id, name_id, meaning_id, y, heading_y[i] + y_offsets[i], label_y[i] + y_offsets[i], meaning_y[i] + y_offsets[i]))

        except Exception as e:
            print(f"Error with card {i+1}:", e)

    last_reading_type = "Three Card Spread"
    last_reading_cards = cards

def view_journal():
    journal_window = tk.Toplevel(root)
    journal_window.title("Tarot Reading Journal ✨")
    journal_window.geometry("500x600")

    scrollbar = tk.Scrollbar(journal_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_area = tk.Text(journal_window, wrap="word", yscrollcommand=scrollbar.set, font=("Georgia", 12))
    text_area.pack(expand=True, fill="both")
    scrollbar.config(command=text_area.yview)

    try:
        with open("reading_journal.txt", "r", encoding="utf-8") as file:
            content = file.read()
            text_area.insert(tk.END, content)
            text_area.config(state="disabled")
    except FileNotFoundError:
        text_area.insert(tk.END, "No journal entries yet.")

    def export_journal():
        try:
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            export_path = os.path.join(downloads_folder, "exported_readings.txt")

            with open("reading_journal.txt", "r", encoding="utf-8") as src, open(export_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())

            messagebox.showinfo("Export Successful", f"Your journal was exported to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred:\n{e}")

    export_button = tk.Button(journal_window, text="📤 Export to File", font=("Georgia", 12), command=export_journal, bg="#ffecb3")
    export_button.pack(pady=10)

# --- Save Reading --- #
def save_reading():
    if not last_reading_cards:
        print("No reading to save.")
        return

    try:
        with open("reading_journal.txt", "a", encoding="utf-8") as file:
            file.write("\n\n✨🌙✨ Tarot Reading ✨🌙✨\n")
            file.write(f"Date: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            file.write(f"Moon Phase: {get_moon_phase()}\n")
            file.write(f"Reading Type: {last_reading_type}\n\n")

            for i, card in enumerate(last_reading_cards):
                label = ""
                if last_reading_type == "Three Card Spread":
                    label = ["Past", "Present", "Future"][i] + ": "
                file.write(f"{label}{card['name']}\n")
                file.write(f"Meaning: {card['meaning']}\n\n")

            file.write("✨-------------------------✨\n\n")

        print("Reading saved to reading_journal.txt")
    except Exception as e:
        print("Error saving reading:", e)

# --- GUI Setup --- #
root = tk.Tk()
root.title("🔮Cicchelli Tarot Reader🔮")
root.geometry("600x800")
root.minsize(600, 800)
root.resizable(True, True)

bg_image_original = Image.open("background_app.png")
bg_image = bg_image_original.resize((600, 800))
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=600, height=800, highlightthickness=0)
canvas.pack(fill="both", expand=True)

bg_image_id = canvas.create_image(0, 0, image=bg_photo, anchor="nw")
canvas.bg_photo = bg_photo

def resize_background(event):
    new_width = event.width
    new_height = event.height

    resized_bg = bg_image_original.resize((new_width, new_height), Image.LANCZOS)
    bg_photo_resized = ImageTk.PhotoImage(resized_bg)
    canvas.itemconfig(bg_image_id, image=bg_photo_resized)
    canvas.bg_photo = bg_photo_resized

    center_x = new_width // 2

    canvas.coords(moon_label_id, center_x, 40)
    canvas.coords(name_label_id, center_x, 90)
    canvas.coords(single_card_window_id, center_x, 380)
    canvas.coords(meaning_label_id, center_x, 670)
    canvas.coords(button_frame_id, center_x, new_height - 60)

    if last_reading_type == "Three Card Spread":
        for i, image_id, heading_id, name_id, meaning_id, y, hy, ly, my in three_card_positions:
            x = new_width // 2 + x_offsets[i]
            canvas.coords(image_id, x, y)
            canvas.coords(heading_id, x, hy)
            canvas.coords(name_id, x, ly)
            canvas.coords(meaning_id, x, my)

canvas.bind("<Configure>", resize_background)

moon_label = tk.Label(root, text=get_moon_phase(), font=("Georgia", 14), fg="#2e003e", bg="#FFD700")
moon_label_id = canvas.create_window(300, 40, window=moon_label)

name_label = tk.Label(root, text="Click to draw a card!", font=("Georgia", 18, "bold"), fg="#2e003e", bg="#FFD700")
name_label_id = canvas.create_window(300, 90, window=name_label)

image_label = tk.Label(root, bg="#FFD700")
single_card_window_id = canvas.create_window(300, 380, window=image_label)

meaning_label = tk.Label(root, text="", wraplength=450, justify="center", font=("Georgia", 14), fg="#2e003e", bg="#FFD700")
meaning_label_id = canvas.create_window(300, 670, window=meaning_label)

button_frame = tk.Frame(canvas, bg="#FFD700", highlightthickness=0)

draw_button = tk.Button(button_frame, text="🃏 Draw a Card", font=("Georgia", 14), command=draw_card, bg="#d1c4e9")
draw_button.pack(side="left", padx=10, pady=5)

three_card_button = tk.Button(button_frame, text="🔮 3-Card Spread", font=("Georgia", 14), command=draw_three_cards, bg="#b39ddb")
three_card_button.pack(side="left", padx=10, pady=5)

save_button = tk.Button(button_frame, text="💾 Save Reading", font=("Georgia", 14), command=save_reading, bg="#c8e6c9")
save_button.pack(side="left", padx=10, pady=5)

view_button = tk.Button(button_frame, text="📓 View Journal", font=("Georgia", 14), command=view_journal, bg="#ffe082")
view_button.pack(side="left", padx=10, pady=5)

button_frame_id = canvas.create_window(300, 740, window=button_frame)
canvas.lift(button_frame_id)

root.mainloop()
