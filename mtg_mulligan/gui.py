import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from mtg_mulligan.scryfall_cache import get_cached_image_path
from mtg_mulligan.uploader import upload_results


class MulliganApp:
    def __init__(
        self,
        decklist,
        draw_hand_func,
        save_result_func,
        results_file,
        username,
        deck_name,
    ):
        self.decklist = decklist
        self.draw_hand_func = draw_hand_func
        self.save_result_func = save_result_func
        self.results_file = results_file
        self.username = username
        self.deck_name = deck_name

        self.root = tk.Tk()
        self.root.title("MTG Mulligan Decision")

        self.current_hand = None
        self.image_refs = []
        self.card_labels = []
        self.hand_count = 0

        self.info_label = tk.Label(
            self.root,
            text=f"User: {self.username} | Deck: {self.deck_name} | Hands classified: 0"
        )
        self.info_label.pack(pady=5)

        self.cards_frame = tk.Frame(self.root)
        self.cards_frame.pack(padx=10, pady=10)

        for i in range(7):
            label = tk.Label(self.cards_frame, text="", compound="top")
            label.grid(row=0, column=i, padx=5, pady=5)
            self.card_labels.append(label)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Keep", width=12, command=self.keep_hand).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Mulligan", width=12, command=self.mulligan_hand).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Stop", width=12, command=self.stop_session).pack(side="left", padx=5)

        self.load_new_hand()

    def update_status(self):
        self.info_label.config(
            text=f"User: {self.username} | Deck: {self.deck_name} | Hands classified: {self.hand_count}"
        )

    def load_new_hand(self):
        self.current_hand = self.draw_hand_func(self.decklist)
        self.image_refs = []

        for i, card_name in enumerate(self.current_hand):
            img_path = get_cached_image_path(card_name)
            img = Image.open(img_path)
            img = img.resize((180, 250))
            tk_img = ImageTk.PhotoImage(img)
            self.image_refs.append(tk_img)

            self.card_labels[i].config(image=tk_img, text=card_name)

    def keep_hand(self):
        self.save_result_func(self.current_hand, "keep", self.results_file)
        self.hand_count += 1
        self.update_status()
        self.load_new_hand()

    def mulligan_hand(self):
        self.save_result_func(self.current_hand, "mulligan", self.results_file)
        self.hand_count += 1
        self.update_status()
        self.load_new_hand()

    def stop_session(self):
        if self.hand_count == 0:
            self.root.destroy()
            return

        success, message = upload_results(
            file_path=self.results_file,
            username=self.username,
            deck_name=self.deck_name,
        )

        if success:
            messagebox.showinfo("Upload", f"{message}\n\nSaved locally at:\n{self.results_file}")
        else:
            messagebox.showwarning(
                "Upload Failed",
                f"{message}\n\nYour results were still saved locally at:\n{self.results_file}"
            )

        self.root.destroy()

    def run(self):
        self.root.mainloop()