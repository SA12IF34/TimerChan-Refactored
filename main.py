import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image
import pystray
import threading

from Timer import Timer
from Pomodoro import Pomodoro

import os

class Main:
    timer_instance = None
    pomodoro_instance = None
    icon = None  # Add this line to store the tray icon

    def __init__(self):
        
        self.root = ctk.CTk()

        self.root.geometry('800x500')
        self.root.title('TimerChan')

        self.main_color = "#383838"
        self.secondary_color = "#242424"
        self.font_color = "#ffffff"

        self.layout = ctk.CTkFrame(self.root, fg_color=self.main_color, bg_color=self.main_color)
        self.layout.pack(expand=True, fill='both', side='left')
        self.layout.rowconfigure(0, weight=1)

        self.layout.columnconfigure(0, weight=1)
        self.layout.columnconfigure(1, weight=1)
        self.layout.columnconfigure(2, weight=1)
        self.layout.columnconfigure(3, weight=1)
        
        self.side_nav = ctk.CTkFrame(self.layout, width=1, fg_color=self.main_color)
        self.side_nav.grid(column=0, columnspan=1, row=0, sticky='wens')

        self.side_sep = ctk.CTkFrame(self.side_nav, bg_color=self.font_color, width=1)
        self.side_sep.pack(side='right', fill='y', pady=15)

        self.timer_button = ctk.CTkButton(self.side_nav, width=1, corner_radius=10, text='Timer', text_color=self.font_color, text_color_disabled=self.font_color, font=('Arial', 18), fg_color=self.main_color, hover_color=self.secondary_color, command=self.start_timer)
        self.pomodoro_button = ctk.CTkButton(self.side_nav, width=1, corner_radius=10, text='Pomodoro', text_color=self.font_color, text_color_disabled=self.font_color, font=('Arial', 18), fg_color=self.main_color, hover_color=self.secondary_color, command=self.start_pomodoro)
        
        self.timer_button.pack(side='top', ipady=5, padx=20, pady=(20, 10), fill='x')
        self.pomodoro_button.pack(side='top', ipady=5, padx=20, pady=(10, 20), fill='x')

        self.main_container = ctk.CTkFrame(self.layout, width=1, fg_color=self.main_color, bg_color=self.main_color)
        self.main_container.grid(column=1, columnspan=3, row=0, sticky='wens')


        def on_closing():
            if (self.timer_instance and self.timer_instance.state == 'started') or \
               (self.pomodoro_instance and self.pomodoro_instance.state == 'started'):
                self.root.withdraw()
            else:
                self.quit_app()

        def setup_tray():
            image = Image.open(os.path.join(os.path.dirname(__file__), 'utils/CustomTkinter_icon_Windows.ico'))

            menu = pystray.Menu(
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Exit", self.quit_app)
            )

            self.icon = pystray.Icon("TimerChan", image, "TimerChan", menu)
            self.icon.run()

        
        
        # Start tray icon in a separate thread
        tray_thread = threading.Thread(target=setup_tray, daemon=True)
        tray_thread.start()
    
        self.root.protocol('WM_DELETE_WINDOW', on_closing)

        self.start_timer()

    def start_timer(self):
        self.timer_button.configure(state='disabled', hover=False, fg_color=self.secondary_color)
        self.pomodoro_button.configure(state='normal', hover=True, fg_color=self.main_color)
        
        if self.pomodoro_instance:
            self.pomodoro_instance.cleanup()
            self.pomodoro_instance = None


        children = self.main_container.winfo_children()
        if len(children) > 0:
            for child in children:
                child.destroy()
        
        self.timer_instance = Timer(self.main_container)

        return


    def start_pomodoro(self):
        self.pomodoro_button.configure(state='disabled', hover=False, fg_color=self.secondary_color)
        self.timer_button.configure(state='normal', hover=True, fg_color=self.main_color)

        if self.timer_instance:
            self.timer_instance.cleanup()
            self.timer_instance = None

        children = self.main_container.winfo_children()
        if len(children) > 0:
            for child in children:
                child.destroy()
        
        self.pomodoro_instance = Pomodoro(self.main_container)
        return

    def show_window(self, icon=None):
        self.root.after(0, self.root.deiconify)
        self.root.lift()
        self.root.focus_force()

    def quit_app(self):
        if self.timer_instance:
            self.timer_instance.cleanup()
        if self.pomodoro_instance:
            self.pomodoro_instance.cleanup()
        self.icon.stop()
        self.root.quit()

    def run(self):

        self.root.mainloop()


app = Main()

app.run()
