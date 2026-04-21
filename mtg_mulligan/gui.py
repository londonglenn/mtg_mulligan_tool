import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from mtg_mulligan.scryfall_cache import get_cached_image_path
from mtg_mulligan.uploader import upload_results
from mtg_mulligan.hand_generator import choose_play_draw

from mtg_mulligan.model_sync import initialize_model_bundle
from mtg_mulligan.predictor import predict_hand_for_app


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
        self.current_position = None

        self.root = tk.Tk()
        self.root.title("MTG Mulligan Decision")

        self.current_hand = None
        self.image_refs = []
        self.card_labels = []
        self.hand_count = 0

        self.model_feedback_enabled = tk.BooleanVar(value=False)
        self.model_bundle = None
        self.model_status_var = tk.StringVar(value="Model: checking...")
        self.feedback_visible = False

        self.info_label = tk.Label(
            self.root,
            text=f"User: {self.username} | Deck: {self.deck_name} | Hands classified: 0"
        )
        self.info_label.pack(pady=5)

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(pady=5)

        self.feedback_checkbox = tk.Checkbutton(
            self.controls_frame,
            text="Show Model Comparison",
            variable=self.model_feedback_enabled
        )
        self.feedback_checkbox.pack(side="left", padx=8)

        self.model_status_label = tk.Label(
            self.controls_frame,
            textvariable=self.model_status_var
        )
        self.model_status_label.pack(side="left", padx=8)

        self.cards_frame = tk.Frame(self.root)
        self.cards_frame.pack(padx=10, pady=10)

        for i in range(7):
            label = tk.Label(self.cards_frame, text="", compound="top")
            label.grid(row=0, column=i, padx=5, pady=5)
            self.card_labels.append(label)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.keep_button = tk.Button(
            self.button_frame,
            text="Keep",
            width=12,
            command=self.keep_hand
        )
        self.keep_button.pack(side="left", padx=5)

        self.mulligan_button = tk.Button(
            self.button_frame,
            text="Mulligan",
            width=12,
            command=self.mulligan_hand
        )
        self.mulligan_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(
            self.button_frame,
            text="Stop",
            width=12,
            command=self.stop_session
        )
        self.stop_button.pack(side="left", padx=5)

        self.feedback_frame = tk.Frame(self.root, bd=1, relief="solid")
        self.feedback_label = tk.Label(
            self.feedback_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=900
        )
        self.feedback_label.pack(padx=10, pady=10)

        self.next_button = tk.Button(
            self.feedback_frame,
            text="Next",
            width=12,
            command=self.next_hand
        )

        self.initialize_model()
        self.load_new_hand()

    def initialize_model(self):
        try:
            bundle = initialize_model_bundle()
            self.model_bundle = bundle

            if bundle is None:
                self.model_status_var.set("Model: unavailable")
                self.feedback_checkbox.config(state="disabled")
            else:
                status = bundle.get("status", "ready")
                version = bundle.get("bundle_version", "unknown")

                if status == "cached":
                    self.model_status_var.set(f"Model: cached ({version})")
                else:
                    self.model_status_var.set(f"Model: {version}")

        except Exception as e:
            self.model_bundle = None
            self.model_status_var.set("Model: unavailable")
            self.feedback_checkbox.config(state="disabled")
            print(f"Model initialization failed: {e}")

    def update_status(self):
        self.info_label.config(
            text=f"User: {self.username} | Deck: {self.deck_name} | "
                 f"Position: {self.current_position} | Hands classified: {self.hand_count}"
        )

    def clear_feedback(self):
        self.feedback_label.config(text="")
        self.keep_button.config(state="normal")
        self.mulligan_button.config(state="normal")

        if self.feedback_visible:
            self.feedback_frame.pack_forget()
            self.feedback_visible = False

    def load_new_hand(self):
        self.clear_feedback()

        self.current_hand = self.draw_hand_func(self.decklist)
        self.current_position = choose_play_draw()
        self.image_refs = []

        self.update_status()

        for i, card_name in enumerate(self.current_hand):
            img_path = get_cached_image_path(card_name)
            img = Image.open(img_path)
            img = img.resize((180, 250))
            tk_img = ImageTk.PhotoImage(img)
            self.image_refs.append(tk_img)

            self.card_labels[i].config(image=tk_img, text=card_name)

    def predict_current_hand(self):
        on_play_value = 1 if self.current_position == "play" else 0

        return predict_hand_for_app(
            hand=self.current_hand,
            on_play=on_play_value,
            bundle=self.model_bundle,
        )

    def submit_decision(self, decision: str):
        model_feedback = None

        if self.model_feedback_enabled.get() and self.model_bundle is not None:
            try:
                model_feedback = self.predict_current_hand()
            except Exception as e:
                print(f"Prediction failed: {e}")
                model_feedback = None

        self.save_result_func(
            self.current_hand,
            self.current_position,
            decision,
            self.results_file,
            model_feedback=model_feedback,
        )

        self.hand_count += 1
        self.update_status()

        if self.model_feedback_enabled.get() and model_feedback is not None:
            self.show_feedback(decision, model_feedback)
        else:
            self.load_new_hand()

    def show_feedback(self, human_decision: str, feedback: dict):
        model_label = feedback.get("pred_label", "UNKNOWN")
        prob_keep = feedback.get("prob_keep", 0.0)
        threshold = feedback.get("threshold", 0.5)
        logit_score = feedback.get("logit_score", None)
        reasons = feedback.get("reasons", [])

        reason_lines = "\n".join(f"• {reason}" for reason in reasons) if reasons else "• No explanation available"

        lines = [
            f"You chose: {human_decision.upper()}",
            f"Model chose: {model_label}",
            f"Keep probability: {prob_keep:.2%}",
            f"Threshold: {threshold:.3f}",
        ]

        if logit_score is not None:
            lines.append(f"Score: {logit_score:.3f}")

        lines.append("")
        lines.append("Why:")
        lines.append(reason_lines)

        self.feedback_label.config(text="\n".join(lines))

        self.keep_button.config(state="disabled")
        self.mulligan_button.config(state="disabled")

        if not self.feedback_visible:
            self.feedback_frame.pack(padx=10, pady=10, fill="x")
            self.next_button.pack(pady=(0, 10))
            self.feedback_visible = True

    def keep_hand(self):
        self.submit_decision("keep")

    def mulligan_hand(self):
        self.submit_decision("mulligan")

    def next_hand(self):
        self.clear_feedback()
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