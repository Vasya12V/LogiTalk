from customtkinter import *
from socket import *
import threading

set_appearance_mode("System")
set_default_color_theme("blue")


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("700x480")
        self.minsize(550, 400)
        self.title("LogiTalk")

        self.username = "Vasya"
        self.menu_open = True

        # --- Основний контейнер для меню (зліва) ---
        self.sidebar_frame = CTkFrame(self, width=200, corner_radius=0, fg_color=("gray90", "gray14"))
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Елементи сайдбару
        self.logo_label = CTkLabel(self.sidebar_frame, text="💬 LogiTalk", font=("Segoe UI", 16, "bold"))
        self.logo_label.pack(pady=(20, 20), padx=15, anchor="w")

        self.user_title = CTkLabel(self.sidebar_frame, text="Ваше ім'я:", font=("Segoe UI", 12), text_color=("gray50", "gray60"))
        self.user_title.pack(padx=15, anchor="w")

        self.name_entry = CTkEntry(self.sidebar_frame, height=35, corner_radius=8, font=("Segoe UI", 12))
        self.name_entry.insert(0, self.username)
        self.name_entry.pack(padx=15, pady=(5, 10), fill="x")
        self.name_entry.bind("<KeyRelease>", self.update_username)

        # --- Основна область чату (праворуч) ---
        self.chat_container = CTkFrame(self, fg_color="transparent")
        self.chat_container.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Поле виведення повідомлень
        self.chat_field = CTkTextbox(
            self.chat_container, font=("Segoe UI", 13),
            state="disabled", corner_radius=10, border_spacing=10
        )
        self.chat_field.pack(side="top", fill="both", expand=True, pady=(0, 12))

        # Нижня панель введення (інпут + кнопка)
        self.bottom_frame = CTkFrame(self.chat_container, fg_color="transparent", height=40)
        self.bottom_frame.pack(side="bottom", fill="x")

        self.send_button = CTkButton(
            self.bottom_frame, text="Надіслати", width=100, height=40,
            command=self.send_message, corner_radius=8,
            font=("Segoe UI", 13, "bold")
        )
        self.send_button.pack(side="right", padx=(10, 0))

        self.message_entry = CTkEntry(
            self.bottom_frame, height=40, placeholder_text="Введіть повідомлення...",
            font=("Segoe UI", 13), corner_radius=8
        )
        self.message_entry.pack(side="left", fill="x", expand=True)
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        # --- Підключення до сокета ---
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            hello = f"TEXT@{self.username}@[SYSTEM]{self.username} приєднався(лася) до чату!\n"
            self.sock.send(hello.encode("utf-8"))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"[Система] Не вдалося підключитися до сервера: {e}")

    def update_username(self, event=None):
        new_name = self.name_entry.get().strip()
        if new_name:
            self.username = new_name

    def send_message(self):
        message = self.message_entry.get().strip()
        if message:
            self.add_message(f"Я: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
            self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    handle_line(self, line.strip())
            except:
                break
        try:
            self.sock.close()
        except:
            pass

    def add_message(self, text):
        self.chat_file_state = "normal"
        self.chat_field.configure(state="normal")
        self.chat_field.insert(END, text + "\n")
        self.chat_field.see(END)
        self.chat_field.configure(state="disabled")


def handle_line(self, line):
    if not line:
        return
    parts = line.split("@", 3)
    msg_type = parts[0]
    if msg_type == "TEXT":
        if len(parts) >= 3:
            author = parts[1]
            message = parts[2]
            if author != self.username:
                self.add_message(f"{author}: {message}")
    elif msg_type == "IMAGE":
        if len(parts) >= 4:
            author = parts[1]
            filename = parts[2]
            if author != self.username:
                self.add_message(f"{author} надіслав(ла) зображення: {filename}")
    else:
        self.add_message(line)


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()