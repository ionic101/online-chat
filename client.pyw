import tkinter as tk
import socket
from threading import Thread
from typing import List
import logging


class Client:
    def __init__(self):
        self.dark = '#222831'
        self.gray = '#393e46'
        self.blue = '#00adb5'
        self.white = '#eeeeee'

        self.window = tk.Tk()
        self.window.title('Online Chat')
        self.window.geometry('800x800')
        self.window.configure(background=self.gray)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.is_pressed_shift = False

        self.icon = tk.PhotoImage(file='send_icon.png')
        self.window.iconbitmap(r'logo.ico')

    def update_chat(self, message):
        if ':' in message:
            start = float(self.getting_text.index(tk.END)) - 1
            end = start+(message.index(':')+1)/10
            self.getting_text.configure(state='normal')
            self.getting_text.insert(tk.END, message)
            self.getting_text.configure(state='disabled')
            self.getting_text.tag_add('username', start, end)
            self.getting_text.see(tk.END)
        else:
            self.getting_text.configure(state='normal')
            self.getting_text.insert(tk.END, message)
            self.getting_text.configure(state='disabled')
            self.getting_text.see(tk.END)

    def listening_server(self):
        self.getting_text.tag_config('username', foreground=self.blue)
        while True:
            try:
                message = self.session.recv(1024).decode()
            except ConnectionResetError:
                logging.warning('lost conecction with server')
                self.clear_window()
                self.spawn_main_menu()
                break
            self.update_chat(message)

    def isValid_IP(self, ip_input: str):
        try:
            ip_address, port = ip_input.split(':')
            socket.inet_aton(ip_address)
            if int(port) >= 0 and int(port) <= 65535:
                return True
        except (socket.error, ValueError):
            return False

    def try_to_connect(self, username: str, ip: str, port: int):
        logging.info(f'try to connect to {ip}:{port}')
        try:
            self.session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.session.connect((ip, int(port)))
            self.session.send(username.encode('utf-8'))
            self.clear_window()
            self.spawn_chat()
            listen = Thread(target=self.listening_server, daemon=True)
            listen.start()
            logging.info(f'successful connection to {ip}:{port}')
        except ConnectionRefusedError:
            logging.info(f'failed connection to {ip}:{port}')
            self.clear_window()
            self.spawn_main_menu()
        except TimeoutError:
            logging.info(f'time out of connection to {ip}:{port}')
            self.clear_window()
            self.spawn_main_menu()

    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def start_connect(self):
        username = self.username_entry.get()
        ip = self.ip_entry.get()
        if username and ip:
            if self.isValid_IP(ip):
                ip, port = ip.split(':')
                self.clear_window()
                self.spawn_load_menu()
                session = Thread(
                    target=self.try_to_connect,
                    args=(username, ip, port),
                    daemon=True
                    )
                session.start()
            else:
                print('Данные не корректны')
        else:
            print('Поля должный быть заполнены')

    def spawn_main_menu(self):
        username_text = tk.Label(self.window)
        username_text.config(
            text='USERNAME',
            font=('Comic Sans MS', 20, 'bold'),
            background=self.gray,
            foreground=self.white
        )
        self.username_entry = tk.Entry(self.window)
        self.username_entry.config(
            background=self.dark,
            foreground=self.white,
            width=20,
            font=('Comic Sans MS', 20),
            borderwidth=0,
            highlightthickness=0,
            insertbackground=self.white
        )
        self.username_entry.insert(0, 'user')

        ip_text = tk.Label(self.window)
        ip_text.config(
            text='IP',
            font=('Comic Sans MS', 20, 'bold'),
            background=self.gray,
            foreground=self.white
        )
        self.ip_entry = tk.Entry(self.window)
        self.ip_entry.config(
            background=self.dark,
            foreground=self.white,
            width=20,
            font=('Comic Sans MS', 20),
            borderwidth=0,
            highlightthickness=0,
            insertbackground=self.white
        )
        self.ip_entry.insert(0, '127.0.0.1:7777')

        connect_button = tk.Button(self.window)
        connect_button.config(
            text='CONNECT',
            width=15,
            height=1,
            background=self.blue,
            foreground=self.dark,
            font=('Comic Sans MS', 20, 'bold'),
            borderwidth=0,
            highlightthickness=0,
            activebackground=self.dark,
            activeforeground=self.gray,
            command=self.start_connect
        )

        tk.Label(self.window, height=10, bg=self.gray).pack()
        username_text.pack(pady=5)
        self.username_entry.pack()
        tk.Label(self.window, height=2, bg=self.gray).pack()
        ip_text.pack(pady=5)
        self.ip_entry.pack()
        tk.Label(self.window, height=3, bg=self.gray).pack()
        connect_button.pack()

    def spawn_load_menu(self):
        load_text = tk.Label(self.window)
        load_text.config(
            text='connecting...',
            font=('Comic Sans MS', 40),
            background=self.gray,
            foreground=self.white
        )

        tk.Label(self.window, height=15, bg=self.gray).pack()
        load_text.pack()

    def press_shift(self, key):
        if key.keysym == 'Shift_L':
            self.is_pressed_shift = True

    def unpress_shift(self, key):
        if key.keysym == 'Shift_L':
            self.is_pressed_shift = False

    def send_message(self, *_):
        try:
            message = self.sending_text.get(1.0, tk.END).strip('\n').strip()
            if not self.is_pressed_shift and message:
                self.session.sendall(message.encode('utf-8'))
                self.sending_text.delete(1.0, tk.END)
            elif not message and not self.is_pressed_shift:
                self.sending_text.delete(1.0, tk.END)
        except Exception as error:
            logging.error(error)

    def spawn_chat(self):
        getting_frame = tk.Frame(self.window)
        getting_scroll = tk.Scrollbar(getting_frame)
        self.getting_text = tk.Text(getting_frame)
        self.getting_text.config(
            background=self.gray,
            foreground=self.white,
            font=('Comic Sans MS', 18),
            state='disabled',
            height=19,
            width=50,
            padx=17,
            pady=13,
            borderwidth=0,
            highlightthickness=0,
            insertbackground=self.white,
            wrap='word',
            yscrollcommand=getting_scroll.set
        )
        getting_scroll.config(
            command=self.getting_text.yview
        )

        sending_frame = tk.Frame(self.window, background=self.gray)
        sending_scroll = tk.Scrollbar(sending_frame)
        self.sending_text = tk.Text(sending_frame)
        self.sending_text.config(
            background=self.dark,
            foreground=self.white,
            width=43,
            height=2,
            padx=15,
            pady=10,
            font=('Comic Sans MS', 18),
            borderwidth=0,
            highlightthickness=0,
            insertbackground=self.white,
            wrap='word',
            yscrollcommand=sending_scroll.set
        )
        sending_scroll.config(command=self.sending_text.yview)

        sending_button = tk.Button(sending_frame)
        sending_button.config(
            background=self.gray,
            borderwidth=0,
            highlightthickness=0,
            activebackground=self.gray,
            image=self.icon,
            command=self.send_message
        )

        self.window.bind('<KeyPress>', self.press_shift)
        self.window.bind('<KeyRelease>', self.unpress_shift)
        self.window.bind('<Return>', self.send_message)
        self.getting_text.pack(side='left')
        getting_scroll.pack(side='left', fill='y')
        getting_frame.pack()

        self.sending_text.pack(side='left')
        sending_scroll.pack(side='left', fill='y')
        sending_button.pack(side='left', padx=20)
        sending_frame.pack(side='bottom', pady=35)

    def run(self):
        logging.info('start program')
        self.spawn_main_menu()
        self.window.mainloop()

    def close(self):
        logging.info('quit program\n')
        self.window.destroy()


logging.basicConfig(level=logging.INFO, filename="ClientLogs.log",
                    filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
Client().run()
