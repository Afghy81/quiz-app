import tkinter as tk
from tkinter import messagebox, ttk
import random
import time


class QuizApp:
    """Aplikasi kuis sederhana dengan seluruh logika di satu file."""

    WINDOW_BG = "#f4f7fb"
    CARD_BG = "#ffffff"
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1d4ed8"
    TEXT = "#1f2937"
    MUTED_TEXT = "#64748b"
    SUCCESS = "#15803d"
    ERROR = "#dc2626"
    WARNING = "#b45309"

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Quiz Interaktif - Tugas Akhir")
        self.window.geometry("700x500")
        self.window.minsize(620, 550)
        self.window.configure(bg=self.WINDOW_BG)
        self.window.protocol("WM_DELETE_WINDOW", self.tutup_aplikasi)

        # Data quiz. Urutan soal diacak setiap kali kuis dimulai.
        self.questions = [
            {
                "question": "Apa itu event-driven programming?",
                "options": [
                    "Program yang berjalan berurutan",
                    "Program yang merespons kejadian",
                    "Program tanpa GUI",
                    "Program berbasis web",
                ],
                "correct": 1,
            },
            {
                "question": "Widget tkinter yang digunakan untuk pilihan tunggal adalah...",
                "options": ["Entry", "Checkbutton", "Radiobutton", "Listbox"],
                "correct": 2,
            },
            {
                "question": "Method tkinter untuk menjalankan event loop adalah...",
                "options": ["start()", "mainloop()", "run_event()", "loop()"],
                "correct": 1,
            },
            {
                "question": "Apa fungsi IntVar() pada tkinter?",
                "options": [
                    "Menyimpan nilai integer yang terhubung ke widget",
                    "Mengatur ukuran jendela",
                    "Membuat animasi",
                    "Menghapus sebuah widget",
                ],
                "correct": 0,
            },
            {
                "question": "Event keyboard untuk tombol Enter ditulis sebagai...",
                "options": ["<Enter>", "<Return>", "<Submit>", "<KeyEnter>"],
                "correct": 1,
            },
            {
                "question": "Method yang tepat untuk menjalankan fungsi setelah jeda tertentu adalah...",
                "options": ["wait()", "pause()", "after()", "delay()"],
                "correct": 2,
            },
            {
                "question": "Komponen ttk yang cocok untuk menampilkan persentase kemajuan adalah...",
                "options": ["ttk.Progressbar", "ttk.Spinbox", "ttk.Separator", "ttk.Notebook"],
                "correct": 0,
            },
            {
                "question": "Apa manfaat state management dalam aplikasi kuis?",
                "options": [
                    "Mengubah warna monitor",
                    "Menyimpan kondisi dan kemajuan aplikasi",
                    "Mempercepat koneksi internet",
                    "Menghapus semua input pengguna",
                ],
                "correct": 1,
            },
            {
                "question": "Shortcut keyboard yang digunakan untuk melewati soal adalah...",
                "options": ["Tab", "Ctrl + S", "Esc", "Alt + F4"],
                "correct": 2,
            },
            {
                "question": "Manakah yang termasuk validasi jawaban?",
                "options": [
                    "Memastikan pilihan sudah dipilih sebelum submit",
                    "Mengubah judul jendela setiap detik",
                    "Mengacak warna tombol",
                    "Menutup aplikasi tanpa peringatan",
                ],
                "correct": 0,
            },
        ]

        # State management: semua kemajuan kuis disimpan pada atribut berikut.
        self.current_question = 0
        self.score = 0
        self.time_per_question = 30
        self.time_left = self.time_per_question
        self.selected_answer = tk.IntVar(value=-1)
        self.answers = []
        self.started_at = time.time()
        self.timer_id = None
        self.feedback_id = None
        self.quiz_finished = False
        self.question_locked = False
        self.option_buttons = []

        random.shuffle(self.questions)

        self.buat_interface()
        self.load_question()
        self.start_timer()

    def buat_interface(self):
        """Membuat seluruh tampilan utama aplikasi."""
        style = ttk.Style(self.window)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Quiz.Horizontal.TProgressbar",
            troughcolor="#dbe4f0",
            background=self.PRIMARY,
            lightcolor=self.PRIMARY,
            darkcolor=self.PRIMARY,
            bordercolor="#dbe4f0",
        )
        style.configure(
            "Score.Horizontal.TProgressbar",
            troughcolor="#dbe4f0",
            background=self.SUCCESS,
            lightcolor=self.SUCCESS,
            darkcolor=self.SUCCESS,
            bordercolor="#dbe4f0",
        )

        self.main_frame = tk.Frame(self.window, bg=self.WINDOW_BG)
        self.main_frame.pack(fill="both", expand=True, padx=26, pady=22)

        header = tk.Frame(self.main_frame, bg=self.WINDOW_BG)
        header.pack(fill="x")

        tk.Label(
            header,
            text="QUIZ INTERAKTIF",
            font=("Segoe UI", 20, "bold"),
            fg=self.TEXT,
            bg=self.WINDOW_BG,
        ).pack(side="left")

        self.score_label = tk.Label(
            header,
            text="Skor: 0 / 10",
            font=("Segoe UI", 11, "bold"),
            fg=self.PRIMARY,
            bg=self.WINDOW_BG,
        )
        self.score_label.pack(side="right", pady=6)

        self.question_progress = ttk.Progressbar(
            self.main_frame,
            style="Quiz.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=len(self.questions),
            length=500,
        )
        self.question_progress.pack(fill="x", pady=(12, 4))

        self.score_progress = ttk.Progressbar(
            self.main_frame,
            style="Score.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=len(self.questions),
            length=500,
        )
        self.score_progress.pack(fill="x", pady=(4, 4))

        self.progress_caption = tk.Label(
            self.main_frame,
            text="Progress soal: 0%  •  Progress skor: 0%",
            font=("Segoe UI", 9),
            fg=self.MUTED_TEXT,
            bg=self.WINDOW_BG,
            anchor="w",
        )
        self.progress_caption.pack(fill="x")

        self.quiz_frame = tk.Frame(self.main_frame, bg=self.WINDOW_BG)
        self.quiz_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.question_card = tk.Frame(
            self.quiz_frame,
            bg=self.CARD_BG,
            highlightthickness=2,
            highlightbackground="#e2e8f0",
        )
        self.question_card.pack(fill="both", expand=True)

        info_row = tk.Frame(self.question_card, bg=self.CARD_BG)
        info_row.pack(fill="x", padx=24, pady=(18, 4))

        self.question_number_label = tk.Label(
            info_row,
            text="Soal 1 dari 10",
            font=("Segoe UI", 10, "bold"),
            fg=self.PRIMARY,
            bg=self.CARD_BG,
        )
        self.question_number_label.pack(side="left")

        self.timer_label = tk.Label(
            info_row,
            text="Waktu: 30 detik",
            font=("Segoe UI", 10, "bold"),
            fg=self.SUCCESS,
            bg=self.CARD_BG,
        )
        self.timer_label.pack(side="right")

        self.question_label = tk.Label(
            self.question_card,
            text="",
            font=("Segoe UI", 15, "bold"),
            fg=self.TEXT,
            bg=self.CARD_BG,
            wraplength=600,
            justify="left",
            anchor="w",
        )
        self.question_label.pack(fill="x", padx=24, pady=(12, 10))

        self.options_frame = tk.Frame(self.question_card, bg=self.CARD_BG)
        self.options_frame.pack(fill="both", expand=True, padx=24)

        self.feedback_label = tk.Label(
            self.question_card,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg=self.MUTED_TEXT,
            bg=self.CARD_BG,
            anchor="w",
        )
        self.feedback_label.pack(fill="x", padx=24, pady=(2, 4))

        button_row = tk.Frame(self.question_card, bg=self.CARD_BG)
        button_row.pack(fill="x", padx=24, pady=(4, 18))

        self.skip_button = tk.Button(
            button_row,
            text="Lewati (Esc)",
            command=self.skip_question,
            font=("Segoe UI", 10),
            fg=self.MUTED_TEXT,
            bg="#eef2f7",
            activebackground="#e2e8f0",
            activeforeground=self.TEXT,
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
        )
        self.skip_button.pack(side="left")

        self.submit_button = tk.Button(
            button_row,
            text="Submit Jawaban (Enter)",
            command=self.submit_answer,
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg=self.PRIMARY,
            activebackground=self.PRIMARY_DARK,
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
        )
        self.submit_button.pack(side="right")

        self.help_label = tk.Label(
            self.main_frame,
            text="Pilih satu jawaban. Enter untuk submit • Esc untuk melewati soal",
            font=("Segoe UI", 9),
            fg=self.MUTED_TEXT,
            bg=self.WINDOW_BG,
        )
        self.help_label.pack(pady=(8, 0))

        # Keyboard shortcut dipasang pada window agar tetap aktif setelah klik widget.
        self.window.bind("<Return>", self._handle_enter)
        self.window.bind("<Escape>", self._handle_escape)

    def load_question(self):
        """Memuat soal aktif dan mengatur ulang state visualnya."""
        if self.current_question >= len(self.questions):
            self.show_result()
            return

        self.question_locked = False
        question = self.questions[self.current_question]
        self.selected_answer.set(-1)
        self.time_left = self.time_per_question

        self.question_number_label.config(
            text=f"Soal {self.current_question + 1} dari {len(self.questions)}"
        )
        self.question_label.config(text=question["question"])
        self.timer_label.config(text=f"Waktu: {self.time_left} detik", fg=self.SUCCESS)
        self.feedback_label.config(text="", fg=self.MUTED_TEXT, bg=self.CARD_BG)
        self.question_card.config(highlightbackground="#e2e8f0")

        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.option_buttons = []

        for index, option in enumerate(question["options"]):
            radio = tk.Radiobutton(
                self.options_frame,
                text=option,
                variable=self.selected_answer,
                value=index,
                font=("Segoe UI", 11),
                fg=self.TEXT,
                bg=self.CARD_BG,
                activebackground=self.CARD_BG,
                activeforeground=self.PRIMARY_DARK,
                selectcolor="#dbeafe",
                anchor="w",
                justify="left",
                wraplength=570,
                padx=8,
                pady=5,
                cursor="hand2",
            )
            radio.pack(fill="x", pady=1)
            self.option_buttons.append(radio)

        self.submit_button.config(state=tk.NORMAL, bg=self.PRIMARY)
        self.skip_button.config(state=tk.NORMAL)
        self._update_progress()

    def start_timer(self):
        """Menjalankan countdown satu detik sekali untuk soal aktif."""
        if self.quiz_finished or self.question_locked:
            return

        self.timer_label.config(text=f"Waktu: {self.time_left} detik")
        if self.time_left <= 5:
            self.timer_label.config(fg=self.ERROR)
        elif self.time_left <= 10:
            self.timer_label.config(fg=self.WARNING)
        else:
            self.timer_label.config(fg=self.SUCCESS)

        if self.time_left == 0:
            self._finish_current_question(
                status="timeout",
                message="Waktu habis! Soal otomatis dilewati.",
            )
            return

        self.time_left -= 1
        self.timer_id = self.window.after(1000, self.start_timer)

    def submit_answer(self):
        """Memvalidasi pilihan, menilai jawaban, lalu menampilkan feedback."""
        if self.quiz_finished or self.question_locked:
            return

        selected = self.selected_answer.get()
        if selected < 0:
            self.feedback_label.config(
                text="Pilih salah satu jawaban terlebih dahulu sebelum submit.",
                fg=self.ERROR,
                bg="#fef2f2",
            )
            self.question_card.config(highlightbackground="#fca5a5")
            messagebox.showwarning(
                "Jawaban belum dipilih",
                "Silakan pilih salah satu opsi terlebih dahulu.",
                parent=self.window,
            )
            return

        question = self.questions[self.current_question]
        is_correct = selected == question["correct"]
        if is_correct:
            self.score += 1
            message = "Benar! Jawaban kamu tepat."
            status = "correct"
        else:
            correct_text = question["options"][question["correct"]]
            message = f"Belum tepat. Jawaban benar: {correct_text}"
            status = "incorrect"

        self._finish_current_question(status=status, message=message, selected=selected)

    def skip_question(self):
        """Melewati soal tanpa menambah skor."""
        if self.quiz_finished or self.question_locked:
            return

        self._finish_current_question(
            status="skipped",
            message="Soal dilewati. Tidak ada poin yang ditambahkan.",
            selected=-1,
        )

    def _finish_current_question(self, status, message, selected=-1):
        """Mengunci soal aktif, menyimpan state, dan menjadwalkan soal berikutnya."""
        if self.question_locked or self.quiz_finished:
            return

        self.question_locked = True
        self._cancel_timer()

        question = self.questions[self.current_question]
        self.answers.append(
            {
                "question": question["question"],
                "selected": selected,
                "correct": question["correct"],
                "status": status,
            }
        )

        for radio in self.option_buttons:
            radio.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED, bg="#93c5fd")
        self.skip_button.config(state=tk.DISABLED)
        self._update_progress()
        self._animate_feedback(status, message)

        # Jeda singkat membuat feedback terlihat sebelum soal berganti.
        self.feedback_id = self.window.after(950, self._next_question)

    def _next_question(self):
        self.feedback_id = None
        if self.quiz_finished:
            return
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.show_result()
            return
        self.load_question()
        self.start_timer()

    def _animate_feedback(self, status, message):
        """Animasi flash sederhana untuk feedback benar, salah, skip, atau timeout."""
        palettes = {
            "correct": (["#dcfce7", "#86efac", "#dcfce7"], self.SUCCESS),
            "incorrect": (["#fee2e2", "#fca5a5", "#fee2e2"], self.ERROR),
            "skipped": (["#fef3c7", "#fcd34d", "#fef3c7"], self.WARNING),
            "timeout": (["#fef3c7", "#fcd34d", "#fef3c7"], self.WARNING),
        }
        colors, text_color = palettes.get(status, (["#e2e8f0"], self.TEXT))
        self.feedback_label.config(text=message, fg=text_color)
        self.question_card.config(highlightbackground=text_color)

        def pulse(step=0):
            if step >= len(colors) or not self.question_card.winfo_exists():
                self.feedback_label.config(bg=self.CARD_BG)
                self.question_card.config(highlightbackground=text_color)
                return
            self.feedback_label.config(bg=colors[step])
            self.question_card.config(highlightbackground=text_color)
            self.window.after(130, lambda: pulse(step + 1))

        pulse()

    def _update_progress(self):
        """Memperbarui progress soal dan progress skor secara real-time."""
        answered_count = len(self.answers)
        score_percent = (self.score / len(self.questions)) * 100
        question_percent = (answered_count / len(self.questions)) * 100

        self.score_label.config(
            text=f"Skor: {self.score} / {len(self.questions)} ({score_percent:.0f}%)"
        )
        self.question_progress.config(value=answered_count)
        self.score_progress.config(value=self.score)
        self.progress_caption.config(
            text=f"Progress soal: {question_percent:.0f}%  •  Progress skor: {score_percent:.0f}%"
        )

    def show_result(self):
        """Menampilkan ringkasan hasil setelah semua soal selesai."""
        self.quiz_finished = True
        self._cancel_timer()
        if self.feedback_id is not None:
            self.window.after_cancel(self.feedback_id)
            self.feedback_id = None

        self.quiz_frame.pack_forget()
        self.help_label.pack_forget()

        self.result_frame = tk.Frame(self.main_frame, bg=self.CARD_BG)
        self.result_frame.pack(fill="both", expand=True, pady=(16, 0))

        percentage = (self.score / len(self.questions)) * 100
        if percentage >= 80:
            headline = "Luar biasa!"
            color = self.SUCCESS
        elif percentage >= 60:
            headline = "Hasil yang bagus!"
            color = self.PRIMARY
        else:
            headline = "Tetap semangat belajar!"
            color = self.WARNING

        tk.Label(
            self.result_frame,
            text="KUIS SELESAI",
            font=("Segoe UI", 12, "bold"),
            fg=self.MUTED_TEXT,
            bg=self.CARD_BG,
        ).pack(pady=(38, 4))
        tk.Label(
            self.result_frame,
            text=headline,
            font=("Segoe UI", 24, "bold"),
            fg=color,
            bg=self.CARD_BG,
        ).pack(pady=2)
        tk.Label(
            self.result_frame,
            text=f"{self.score} dari {len(self.questions)} jawaban benar ({percentage:.0f}%)",
            font=("Segoe UI", 14),
            fg=self.TEXT,
            bg=self.CARD_BG,
        ).pack(pady=(4, 14))

        skipped = sum(answer["status"] in ("skipped", "timeout") for answer in self.answers)
        duration = max(0, int(time.time() - self.started_at))
        minutes, seconds = divmod(duration, 60)
        tk.Label(
            self.result_frame,
            text=f"Soal dilewati: {skipped}  •  Durasi: {minutes:02d}:{seconds:02d}",
            font=("Segoe UI", 10),
            fg=self.MUTED_TEXT,
            bg=self.CARD_BG,
        ).pack()

        ttk.Progressbar(
            self.result_frame,
            style="Score.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=len(self.questions),
            value=self.score,
            length=380,
        ).pack(pady=24)

        tk.Button(
            self.result_frame,
            text="Mulai Lagi",
            command=self.restart_quiz,
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg=self.PRIMARY,
            activebackground=self.PRIMARY_DARK,
            activeforeground="white",
            relief="flat",
            padx=22,
            pady=9,
            cursor="hand2",
        ).pack()

    def restart_quiz(self):
        """Mengembalikan state ke awal agar kuis bisa dimainkan ulang."""
        if hasattr(self, "result_frame"):
            self.result_frame.destroy()

        self.current_question = 0
        self.score = 0
        self.time_left = self.time_per_question
        self.answers = []
        self.started_at = time.time()
        self.quiz_finished = False
        self.question_locked = False
        random.shuffle(self.questions)

        self.quiz_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.help_label.pack(pady=(8, 0))
        self.load_question()
        self.start_timer()

    def _handle_enter(self, _event=None):
        if not self.quiz_finished:
            self.submit_answer()
        return "break"

    def _handle_escape(self, _event=None):
        if not self.quiz_finished:
            self.skip_question()
        return "break"

    def _cancel_timer(self):
        if self.timer_id is not None:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None

    def tutup_aplikasi(self):
        self._cancel_timer()
        if self.feedback_id is not None:
            self.window.after_cancel(self.feedback_id)
            self.feedback_id = None
        self.window.destroy()

    def jalankan(self):
        """Memulai event loop tkinter."""
        self.window.mainloop()


if __name__ == "__main__":
    app = QuizApp()
    app.jalankan()
