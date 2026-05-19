# Welcome to the Tarot Terminal App!  This was developed originally by Meghan Trainor as part of her Witchy Python Course
# and customised for Raspberry Pi and Thermal printing by Steph Piper
# You may need to adjust the card sizes below depending on your screen display used and artworks chosen.  
# Enjoy!

import os
import random
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading


# Floating Cards Animation

class FloatingCards(tk.Canvas):
    def __init__(self, master, image_paths, width=1200, height=800):
        super().__init__(master, width=width, height=height, bg="black", highlightthickness=0)

        self.width = width
        self.height = height

        self.cards = []
        self.photos = []

        for path in image_paths:
            img = Image.open(path)
            img = img.resize((220, 310))
            photo = ImageTk.PhotoImage(img)

            x = random.randint(0, width)
            y = random.randint(-height, height)

            card = self.create_image(x, y, image=photo)

            self.cards.append({
                "id": card,
                "x": x,
                "y": y,
                "speed": random.uniform(0.5, 2)
            })

            self.photos.append(photo)

        self.animate()

    def animate(self):

        for card in self.cards:

            card["y"] += card["speed"]

            if card["y"] > self.height + 200:
                card["y"] = -200
                card["x"] = random.randint(0, self.width)

            self.coords(card["id"], card["x"], card["y"])

        self.after(40, self.animate)
import pygame

class TarotApp:
    SIGNIFICANCES = ["Past", "Present", "Future"]
    # SIGNIFICANCES = ["Idea", "Process", "Aspiration"]
    # SIGNIFICANCES = ["Inner World", "Present World", "Outer World"]

    def __init__(
        self,
        root: tk.Tk,
        
        cards_file: str = "tarot-cards.txt",
        images_dir: str = "tarot_cards",
        save_file: str = "tarot-readings.txt",
        

    ):
        pygame.mixer.init()
        self.magic_sound = pygame.mixer.Sound("sounds/magic.wav")
        self.root = root
        self.root.after(100, self.enable_fullscreen)
        
        self.cards_file = cards_file
        self.images_dir = images_dir
        self.save_file = save_file
        self.card_back_img = None

        self.cards = self.load_cards(self.cards_file)
        self.setup_ui()
        
    def setup_ui(self):
        self.bg_app = "#E6E6E6"
        self.bg_panel = "#000000"
        self.fg_text = "#FFFFFF"
        self.fg_muted = "#FFFFFF"
        self.fg_buttons = "#562E91"

# !!! ADJUST TEXT & CARD SIZE HERE TO FIT YOUR SCREEN !!!

        self.font_title = ("Arial", 22, "bold")
        self.font_body = ("Arial", 12, "italic")
        self.font_small = ("Arial", 11)
        self.font_subtitle = ("Arial", 16, "bold")

        self.pad = 16
        self.card_size = (200, 310)
        self.wrap = 290

        self.reading = []
        self.photo_refs = []
        self.showing_reading = False

        back_path = os.path.join(self.images_dir, "cover", "cover.jpg")
        img = Image.open(back_path)
        img = img.resize(self.card_size)
        self.card_back_img = img

        self.root.title("Design Tarot Reading")
        self.root.configure(bg=self.bg_app)

        self.panel = tk.Frame(self.root, bg=self.bg_panel, bd=0, highlightthickness=0)

        self.panel.grid_rowconfigure(0, weight=1)
        self.panel.grid_rowconfigure(1, weight=0)
        self.panel.grid_columnconfigure(0, weight=1)

        self.content = tk.Frame(self.panel, bg=self.bg_panel)
        self.content.grid(row=0, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)

        self.cards_area = tk.Frame(self.content, bg=self.bg_panel)
        self.cards_area.grid(row=1, column=0, sticky="nsew", padx=self.pad, pady=(0, 10))
        self.content.grid_rowconfigure(1, weight=1)

        for col in range(3):
            self.cards_area.grid_columnconfigure(col, weight=1, uniform="cards")

        controls = tk.Frame(self.panel, bg=self.bg_panel)
        controls.grid(row=1, column=0, sticky="s", padx=self.pad, pady=(0, self.pad))

        self.draw_button = tk.Button(
            controls,
            text="Draw Cards",
            font=self.font_body,
            command=self.draw_button_action,
            bg=self.fg_buttons,
            fg=self.fg_text,
            bd=1,
            relief="solid",
            padx=14,
            pady=8
        )
        self.draw_button.grid(row=0, column=0, sticky="s")

        self.save_button = tk.Button(
            controls,
            text="Print Reading",
            font=self.font_body,
            command=self.save_reading,
            bg=self.fg_buttons,
            fg=self.fg_text,
            bd=1,
            relief="solid",
            padx=14,
            pady=8
        )
        self.save_button.grid(row=0, column=1, sticky="s", padx=(10, 0))
        self.save_button.configure(state="disabled")

        self.show_start_screen()
    
    def print_receipt(self, notes):
        import serial
        import time
        import textwrap
        print("PRINT FUNCTION CALLED")
        
        try:
            ser = serial.Serial("/dev/serial0", 9600, timeout=1)
            time.sleep(2)
            
            # --- Helper functions ---
            def write_line(text=""):
                ser.write((text + "\n").encode("ascii", errors="ignore"))
                time.sleep(0.05)

            def center(text, width=32):
                return text.center(width)
                
            # ascii art
            ascii_banner = [
              "   .---------.",
              "   |.-------.|",
              "   ||  o  o ||",
              "   ||  \_/  ||",
              "   ||-------'|",
              " .-^---------^-.",
              " | ORACLE 9000 |",
              " |_-----------_|",
            ]
            
            for line in ascii_banner: 
                write_line(center(line))
            write_line()

            # --- Header ---
            write_line(center("*** THE ORACLE 9000 ***"))
            write_line(center("----------------"))

            # --- Timestamp ---
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            write_line(center(timestamp))
            write_line()

            # --- Cards ---
            for i, card in enumerate(self.reading):
                sig = self.SIGNIFICANCES[i]
                meaning = self.cards.get(card, "")

                write_line(center(f"{sig}:"))
                write_line(card)

                for line in textwrap.wrap(meaning, 32):
                    write_line(line)

                write_line("-" * 32)


            # --- Footer ---
            write_line(center("Trust Your Path"))
            write_line("\n\n\n\n\n\n")

            ser.flush()
            ser.close()

        except Exception as e:
            print("Printer Error:", e)
            self.root.after(0, lambda: messagebox.showerror("Printer Error", str(e)))
            
    def wrap_text(self, text, width=32):
        import textwrap
        return textwrap.wrap(text, width)


        
# Start screen with floating cards        
    def show_start_screen(self):

        self.start_frame = tk.Frame(self.root, bg="black")
        self.start_frame.pack(fill="both", expand=True)

        image_paths = [
            "tarot_cards/The Fool.jpg",
            "tarot_cards/The Star.jpg",
            "tarot_cards/The Moon.jpg",
            "tarot_cards/The Magician.jpg",
            "tarot_cards/cover/cover.jpg",
            "tarot_cards/cover/cover.jpg",
            "tarot_cards/cover/cover.jpg"
        ]

        self.animation = FloatingCards(self.start_frame, image_paths)
        self.animation.pack(fill="both", expand=True)

        title = tk.Label(
            self.start_frame,
            text="✨ The Tarot Terminal ✨",
            font=("Arial", 32, "bold"),
            bg="black",
            fg="white"
        )
        title.place(relx=0.5, rely=0.25, anchor="center")

        start_button = tk.Button(
            self.start_frame,
            text="Begin Your Tarot Reading",
            font=("Arial", 16),
            command=self.start_app
        )

        start_button.place(relx=0.5, rely=0.75, anchor="center")


# Start app with cards

    def start_app(self):
        if hasattr(self, "start_frame") and self.start_frame.winfo_exists():
            self.start_frame.destroy()

        self.panel.pack(expand=True, fill="both", padx=0, pady=0)
        self.showing_reading = False
        self.draw_button.configure(text="Draw Cards")
        self.save_button.configure(state="disabled")
        self.render_placeholder()
        
    

    def load_cards(self, filepath: str) -> dict:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Could not find '{filepath}' next to this script.")
        cards = {}
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ": " not in line:
                    continue
                name, meaning = line.split(": ", 1)
                cards[name] = meaning
        if not cards:
            raise ValueError(f"No cards loaded from '{filepath}'. Check file format.")
        return cards

    def clear_cards_ui(self):
        for child in self.cards_area.winfo_children():
            child.destroy()
        self.photo_refs.clear()

    def render_placeholder(self):
        self.clear_cards_ui()

        try:
            back_path = os.path.join(self.images_dir, "cover", "cover.jpg")
            img = Image.open(back_path)
            img = img.resize(self.card_size)
            self.card_back = ImageTk.PhotoImage(img)
        except Exception:
            self.card_back = None

        for i in range(3):

            col = tk.Frame(self.cards_area, bg=self.bg_panel)
            col.grid(row=0, column=i, sticky="nsew", padx=10, pady=(6, 0))

            label = tk.Label(col, bg=self.bg_panel)

            if self.card_back:
                label.configure(image=self.card_back)
                label.image = self.card_back
            else:
                label.configure(text="Card Back")

            label.grid(row=0, column=0, pady=(0, 10))

        # Instruction text
        tk.Label(
            self.cards_area,
            text='Click "Draw Cards" to reveal your reading.',
            font=self.font_body,
            bg=self.bg_panel,
            fg=self.fg_muted
        ).grid(row=1, column=0, columnspan=3, pady=30)

    def try_load_photo(self, card_name: str):
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            path = os.path.join(self.images_dir, f"{card_name}{ext}")
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    img = img.resize(self.card_size)
                    return ImageTk.PhotoImage(img)
                except Exception:
                    return None
        return None
        


    def draw_cards(self):
        card_names = list(self.cards.keys())
        random.shuffle(card_names)
        self.reading = card_names[:3]
        self.showing_reading = True
        self.save_button.configure(state="normal")

        self.draw_button.configure(text="Return to Menu")
        self.clear_cards_ui()
        self.draw_button.configure(text="Consulting the Oracle...")
		
        #Play sound
        self.magic_sound.play()
		
        for i, card_name in enumerate(self.reading):
            self.root.after(i * 400, lambda i=i, card_name=card_name: self.render_card(i, card_name))
        self.root.after(1300, lambda: self.draw_button.configure(text="Return to Menu"))
            
    def draw_button_action(self):
        if self.showing_reading:
            self.return_to_menu()
        else:
            self.draw_cards()

    def return_to_menu(self):
        self.reading = []
        self.showing_reading = False

        self.clear_cards_ui()
        self.draw_button.configure(text="Draw Cards")
        self.save_button.configure(state="disabled")

        self.panel.pack_forget()

        if hasattr(self, "start_frame") and self.start_frame.winfo_exists():
            self.start_frame.destroy()

        self.show_start_screen()

    # Renders cards one by one
    def render_card(self, i, card_name):

        col = tk.Frame(self.cards_area, bg=self.bg_panel)
        col.grid(row=0, column=i, sticky="nsew", padx=10, pady=(6, 0))

        col.grid_rowconfigure(0, weight=0)
        col.grid_rowconfigure(1, weight=0)
        col.grid_rowconfigure(2, weight=0)
        col.grid_columnconfigure(0, weight=1)

        # image
        img_holder = tk.Label(col, bg=self.bg_panel)
        img_holder.grid(row=0, column=0, sticky="n", pady=(0, 10))

        self.flip_card(img_holder, card_name)

        # significance
        sig = self.SIGNIFICANCES[i] if i < len(self.SIGNIFICANCES) else f"Card {i+1}"

        tk.Label(
            col,
            text=f"Significance: {sig}",
            font=self.font_body,
            bg=self.bg_panel,
            fg=self.fg_text,
            wraplength=self.wrap,
            justify="center",
        ).grid(row=1, column=0, sticky="n", pady=(0, 6))

        # meaning
        tk.Label(
            col,
            text=self.cards.get(card_name, ""),
            font=self.font_small,
            bg=self.bg_panel,
            fg=self.fg_muted,
            wraplength=self.wrap,
            justify="left",
        ).grid(row=2, column=0, sticky="n")

    # Card flip animation
    def flip_card(self, label, card_name):

        front_img = Image.open(os.path.join(self.images_dir, f"{card_name}.jpg"))
        front_img = front_img.resize(self.card_size)

        steps = 10
        delay = 25

        def animate(step=0):
            if step <= steps:

                scale = 1 - (step / steps)
                width = max(1, int(self.card_size[0] * scale))

                img = self.card_back_img.resize((width, self.card_size[1]))
                photo = ImageTk.PhotoImage(img)

                label.configure(image=photo)
                label.image = photo

                self.root.after(delay, lambda: animate(step + 1))

            elif step == steps + 1:

                label.current_image = front_img
                animate(step + 2)

            elif step <= steps * 2 + 1:

                scale = (step - steps - 1) / steps
                width = max(1, int(self.card_size[0] * scale))

                img = label.current_image.resize((width, self.card_size[1]))
                photo = ImageTk.PhotoImage(img)

                label.configure(image=photo)
                label.image = photo

                self.root.after(delay, lambda: animate(step + 1))


        animate()
        
    def clear_notes(self):
        self.journal.delete("1.0", "end")

    def save_reading(self):
        notes = "Test note"
        if not self.reading:
            messagebox.showwarning("No Cards Drawn", "Draw cards before saving a reading.")
            return
        if not notes:
            messagebox.showwarning("Empty Entry", "Write a few notes before saving.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        sigs = self.SIGNIFICANCES if len(self.SIGNIFICANCES) >= 3 else ["Card 1", "Card 2", "Card 3"]
        header = f"[{timestamp}] {sigs[0]}={self.reading[0]} | {sigs[1]}={self.reading[1]} | {sigs[2]}={self.reading[2]}"

        try:
            with open(self.save_file, "a", encoding="utf-8") as f:
                f.write(header + "\n")
                f.write(notes + "\n")
                f.write("-" * 72 + "\n")

            print("DEBUG reading:", self.reading)
            
            threading.Thread(
                target=self.print_receipt,
                args=(notes,),
                daemon=True
            ).start()
            
            print(f"Saved to{self.save_file}'.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save reading:\n{e}")
    
    def enable_fullscreen(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()

        self.fullscreen = True
        self.root.geometry(f"{width}x{height}+0+0")
        self.root.overrideredirect(True)

        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.overrideredirect(False)
        self.root.attributes("-fullscreen", False)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.overrideredirect(self.fullscreen)
        self.root.attributes("-fullscreen", self.fullscreen)

if __name__ == "__main__":
    root = tk.Tk()
    app = TarotApp(root)
    root.mainloop()
