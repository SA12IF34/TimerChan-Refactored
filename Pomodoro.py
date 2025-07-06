import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from winsound import *
from utils.pomodoro import *

import threading
import ctypes

class ThreadChan(threading.Thread):

    def __init__(self, callback_func, thread_name, **kwargs):
        threading.Thread.__init__(self, **kwargs)

        self.callback_func = callback_func
        self.thread_name = thread_name
        self._is_running = True
        self.daemon = True 

    def get_id(self):
 
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
        
    def terminate(self, normal=True):
        thread_id = self.get_id()
        self._is_running = False
        if not self.is_alive():
            return
        
        self.callback_func(normal=normal)
        
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))

        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        
        # Wait for thread to actually terminate    
        self.join()

        


class Pomodoro:

    state = 'stopped' # started | stopped

    session_hour = '00'
    session_minute = '00'
    session_second = '00'

    break_hour = '00'
    break_minute = '00'
    break_second = '00'

    session_number = 0

    pomodoro_event = None
    pomodoro_thread = None

    def __init__(self, root):
        self.root = root

        self.main_color = "#383838"
        self.secondary_color = "#242424"
        self.font_color = "#ffffff"

        self.page = ctk.CTkFrame(root, fg_color='transparent')
        self.page.pack(fill='both', expand=True)

        self.page.grid_rowconfigure(0, weight=1)

        self.page.grid_columnconfigure(0, weight=1)
        self.page.grid_columnconfigure(1, weight=1)
        self.page.grid_columnconfigure(2, weight=1)

        # Main Container
        self.container = ctk.CTkFrame(self.page, fg_color='transparent')
        self.container.grid(column=0, columnspan=2, row=0, sticky='wens')

        self.title = ctk.CTkLabel(self.container, text='Pomodoro', text_color=self.font_color, font=('Arial', 20), height=1, anchor='center')
        self.title.pack(side='top',pady=(20, 10))

        self.pomodoro_container = ctk.CTkFrame(self.container, fg_color='transparent')
        self.pomodoro_container.pack(side='top', fill='both', expand=True)

        def validate_input(event):
            widget:ctk.CTkEntry = event.widget
            if len(widget.get()) > 2:
                widget.delete(2, ctk.END)
                widget.xview(0)
                
            return True


        self.session_label = ctk.CTkLabel(self.pomodoro_container, text='Session Time', text_color=self.font_color, font=('Arial', 18), height=1)
        self.session_label.pack(side='top', padx=20, pady=10, anchor='w')

        self.session_container = ctk.CTkFrame(self.pomodoro_container, fg_color='transparent', height=1)
        self.session_container.pack(side='top', anchor='w', padx=20, pady=(0, 20))

        entry_kwargs = {
            'font': ('Arial', 20),
            'fg_color': self.secondary_color,
            'text_color': self.font_color,
            'width': 45,
            'height': 45,
            'border_width': 2,
            'border_color': 'gray',
            'corner_radius': 10,
            'justify': 'center',
            'placeholder_text': '00',
        }

        entry_pack_kwargs = {
            'side': 'left',
            'padx': 5,
            'pady': 5,
            'anchor': 'w'
        }

        self.session_h_entry = ctk.CTkEntry(self.session_container, **entry_kwargs)
        self.session_m_entry = ctk.CTkEntry(self.session_container, **entry_kwargs)
        self.session_s_entry = ctk.CTkEntry(self.session_container, **entry_kwargs)

        self.session_h_entry.pack(**entry_pack_kwargs)
        ctk.CTkLabel(self.session_container, text=':', text_color=self.font_color, font=('Arial', 26), height=1).pack(side='left', padx=5, pady=5)
        self.session_m_entry.pack(**entry_pack_kwargs)
        ctk.CTkLabel(self.session_container, text=':', text_color=self.font_color, font=('Arial', 26), height=1).pack(side='left', padx=5, pady=5)
        self.session_s_entry.pack(**entry_pack_kwargs)

        
        self.session_h_entry.bind('<KeyRelease>', validate_input)
        self.session_m_entry.bind('<KeyRelease>', validate_input)
        self.session_s_entry.bind('<KeyRelease>', validate_input)

        self.break_label = ctk.CTkLabel(self.pomodoro_container, text='Break Time', text_color=self.font_color, font=('Arial', 18), height=1)
        self.break_label.pack(side='top', padx=20, pady=10, anchor='w')

        self.break_container = ctk.CTkFrame(self.pomodoro_container, fg_color='transparent', height=1)
        self.break_container.pack(side='top', anchor='w', padx=20, pady=(0, 20))

        self.break_h_entry = ctk.CTkEntry(self.break_container, **entry_kwargs)
        self.break_m_entry = ctk.CTkEntry(self.break_container, **entry_kwargs)
        self.break_s_entry = ctk.CTkEntry(self.break_container, **entry_kwargs)

        self.break_h_entry.pack(**entry_pack_kwargs)
        ctk.CTkLabel(self.break_container, text=':', text_color=self.font_color, font=('Arial', 26), height=1).pack(side='left', padx=5, pady=5)
        self.break_m_entry.pack(**entry_pack_kwargs)
        ctk.CTkLabel(self.break_container, text=':', text_color=self.font_color, font=('Arial', 26), height=1).pack(side='left', padx=5, pady=5)
        self.break_s_entry.pack(**entry_pack_kwargs)

        self.break_h_entry.bind('<KeyRelease>', validate_input)
        self.break_m_entry.bind('<KeyRelease>', validate_input)
        self.break_s_entry.bind('<KeyRelease>', validate_input)

        self.session_number_container = ctk.CTkFrame(self.pomodoro_container, fg_color='transparent', height=1)
        self.session_number_container.pack(side='top', anchor='w', padx=20, pady=10)

        self.session_number_label = ctk.CTkLabel(self.session_number_container, text='Number of Sessions', text_color=self.font_color, font=('Arial', 18), height=1)
        self.session_number_label.pack(side='left', padx=5, pady=10, anchor='w')

        self.session_number_entry = ctk.CTkEntry(self.session_number_container, font=('Arial', 20), fg_color=self.secondary_color, text_color=self.font_color, width=45, height=45, border_width=2, border_color='gray', corner_radius=10, justify='center', placeholder_text='0')
        self.session_number_entry.insert(ctk.END, '4')
        self.session_number_entry.pack(side='left', padx=5, pady=10, anchor='w')

        self.session_number_entry.bind('<KeyRelease>', validate_input)

        # Action Buttons
        self.actions_container = ctk.CTkFrame(self.pomodoro_container, fg_color='transparent', height=1)
        self.actions_container.pack(side='bottom', anchor='w', pady=(10, 30))

        btn_kwargs = {
            'master': self.actions_container,
            'font': ('Arial', 18),
            'fg_color': self.secondary_color,
            'hover_color': 'gray',
            'text_color': self.font_color,
            'width': 1,
            'corner_radius': 10,  
        }

        btn_pack_kwargs = {
            'side': 'left',
            'anchor': 'w',
            'padx': 15,
            'pady': 5,
            'ipady': 5,
            'ipadx': 10
        }

        self.pomodoro_btn = ctk.CTkButton(text='Start Pomodoro', command=self.pomodoro_action, **btn_kwargs)
        self.pomodoro_btn.pack(**btn_pack_kwargs)

        self.save_btn = ctk.CTkButton(text='Save', command=self.save_pomodoro, **btn_kwargs)
        self.save_btn.pack(**btn_pack_kwargs)



        # Saved Pomodoro Container
        self.saved_pomodoro_container = ctk.CTkFrame(self.page, fg_color=self.secondary_color, bg_color=self.secondary_color)
        self.saved_pomodoro_container.grid(column=2, row=0, sticky='ewns')

        self.saved_pomodoro_border = ctk.CTkFrame(self.saved_pomodoro_container, fg_color='gray', bg_color='gray', width=1)
        self.saved_pomodoro_border.pack(side='left', fill='y')

        self.saved_pomodoro_label = ctk.CTkLabel(self.saved_pomodoro_container, text='Saved Pomodoros', text_color=self.font_color, font=('Arial', 20), height=1, anchor='center')
        self.saved_pomodoro_label.pack(side='top', pady=(20, 10))

        self.get_saved_pomodoros()

        # self.root.master.master.protocol('WM_DELETE_WINDOW', self.on_close)


    def cleanup(self):
        if self.pomodoro_event:
            self.reset_pomodoro()
        

    # def on_close(self):
    #     if self.state == 'started' and self.pomodoro_event:
    #         self.root.master.master.withdraw()

    #     else:
    #         self.root.master.master.quit()
    #         self.root.master.master.destroy()
        
    #     return
    
    def pomodoro_action(self):
        if self.state == 'stopped':
            self.start_pomodoro()
        else:
            self.reset_pomodoro()
            
    def set_pomodoro(self):
        self.session_hour = self.session_h_entry.get() or '00'
        self.session_minute = self.session_m_entry.get() or '00'
        self.session_second = self.session_s_entry.get() or '00'

        self.break_hour = self.break_h_entry.get() or '00'
        self.break_minute = self.break_m_entry.get() or '00'
        self.break_second = self.break_s_entry.get() or '00'

        try:
            self.session_number = int(self.session_number_entry.get())
            if self.session_number < 1:
                CTkMessagebox(title='Invalid Input', message='Session number must be greater than 0', icon='cancel')
                return False
        except ValueError:
            CTkMessagebox(title='Invalid Input', message='Session number must be an integer', icon='cancel')
            return False

        if self.session_hour == '00' and self.session_minute == '00' and self.session_second == '00':
            CTkMessagebox(title='Invalid Input', message='Session time cannot be 0', icon='cancel')
            return False

        if self.break_hour == '00' and self.break_minute == '00' and self.break_second == '00':
            CTkMessagebox(title='Invalid Input', message='Break time cannot be 0', icon='cancel')
            return False
        

        return True

    def start_pomodoro(self):
        if not self.set_pomodoro():
            return

        self.state = 'started'
        self.pomodoro_btn.configure(text='Reset Pomodoro')

        self.pomodoro_event = threading.Event()
        self.pomodoro_thread = ThreadChan(
            target=pomodoro_counter,
            args=[
                self.session_h_entry,
                self.session_m_entry,
                self.session_s_entry,
                self.break_h_entry,
                self.break_m_entry,
                self.break_s_entry,
                self.session_number_entry,
                self.pomodoro_event,
                f'{self.session_hour}:{self.session_minute}:{self.session_second}',
                f'{self.break_hour}:{self.break_minute}:{self.break_second}',
                self.session_number,
                self.break_start_msg,
                self.session_start_msg
            ],
            callback_func=self.handle_reset_pomodoro,
            thread_name='pomodoro'
        )

        get_pomodoro_thread(self.pomodoro_thread)

        self.session_h_entry.configure(state='disabled')
        self.session_m_entry.configure(state='disabled')
        self.session_s_entry.configure(state='disabled')
        self.break_h_entry.configure(state='disabled')
        self.break_m_entry.configure(state='disabled')
        self.break_s_entry.configure(state='disabled')
        self.session_number_entry.configure(state='disabled')

        self.pomodoro_thread.start()
        self.pomodoro_event.set()

        return

    def break_start_msg(self):
        PlaySound('utils/alarm.wav', 1)
        CTkMessagebox(title='Break Time!', message='Break time started', icon='info')
        return
    
    def session_start_msg(self, session_number):
        PlaySound('utils/alarm.wav', 1)
        CTkMessagebox(title='Session Time!', message=f'Session {session_number} started', icon='info')
        return

    def handle_reset_pomodoro(self, normal=True):
        
        self.session_h_entry.configure(state='normal')
        self.session_m_entry.configure(state='normal')
        self.session_s_entry.configure(state='normal')

        self.break_h_entry.configure(state='normal')
        self.break_m_entry.configure(state='normal')
        self.break_s_entry.configure(state='normal')

        self.session_number_entry.configure(state='normal')

        for child in (self.session_h_entry, self.session_m_entry, self.session_s_entry, self.break_h_entry, self.break_m_entry, self.break_s_entry):
            child.delete(0, ctk.END)
            child.insert(ctk.END, '00')
            
        self.session_hour = '00'
        self.session_minute = '00'
        self.session_second = '00'

        self.break_hour = '00'
        self.break_minute = '00'
        self.break_second = '00'

        self.session_number = 0

        if self.state == 'started' and normal:
            PlaySound('utils/pomodoro-alarm.wav', 1)
            CTkMessagebox(title='Finished!', message='Pomodoro finished!', icon='check')


        self.state = 'stopped'
        self.pomodoro_btn.configure(text='Start Pomodoro')
        self.pomodoro_event = None
        self.pomodoro_thread = None

        return

    def reset_pomodoro(self):
        
        if self.pomodoro_event:
            if not self.pomodoro_event.is_set():
                self.pomodoro_event.set()

        self.pomodoro_thread.terminate(normal=False)


    def get_saved_pomodoros(self):
        
        for widget in self.saved_pomodoro_container.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.saved_pomodoro_border:
                widget.destroy()

        pomodoros = get_pomodoros()

        if pomodoros:
            for pomodoro in pomodoros:
                session_time = pomodoro['session_time']
                break_time = pomodoro['break_time']
                sessions_number = pomodoro['sessions_number']

                # Create a frame for each pomodoro
                pomodoro_frame = ctk.CTkFrame(self.saved_pomodoro_container, fg_color=self.main_color, bg_color=self.main_color, height=1)
                pomodoro_frame.pack(side='top', fill='x', padx=0, ipady=0)

                # Session time label
                session_label = ctk.CTkLabel(
                    pomodoro_frame, 
                    text=f'Session Time {session_time}', 
                    text_color=self.font_color, 
                    font=('Arial', 18), 
                    height=1
                )
                session_label.pack(side='top', anchor='w', padx=10, pady=10)

                # Break time label
                break_label = ctk.CTkLabel(
                    pomodoro_frame, 
                    text=f'Break Time {break_time}', 
                    text_color=self.font_color, 
                    font=('Arial', 18), 
                    height=1
                )
                break_label.pack(side='top', anchor='w', padx=10, pady=10)

                # Sessions number label
                sessions_label = ctk.CTkLabel(
                    pomodoro_frame, 
                    text=f'Sessions Number {sessions_number}', 
                    text_color=self.font_color, 
                    font=('Arial', 18), 
                    height=1
                )
                sessions_label.pack(side='top', anchor='w', padx=10, pady=10)

                # Bind click event to the frame and all its children
                pomodoro_frame.bind('<Button-1>', lambda event, st=session_time, bt=break_time, sn=sessions_number: self.load_pomodoro(st, bt, sn))
                for widget in (session_label, break_label, sessions_label):
                    widget.bind('<Button-1>', lambda event, st=session_time, bt=break_time, sn=sessions_number: self.load_pomodoro(st, bt, sn))
        return

    def load_pomodoro(self, session_time, break_time, sessions_number):
        session_time = session_time.split(':')
        break_time = break_time.split(':')

        self.session_h_entry.delete(0, ctk.END)
        self.session_m_entry.delete(0, ctk.END)
        self.session_s_entry.delete(0, ctk.END)

        self.break_h_entry.delete(0, ctk.END)
        self.break_m_entry.delete(0, ctk.END)
        self.break_s_entry.delete(0, ctk.END)

        self.session_number_entry.delete(0, ctk.END)

        self.session_h_entry.insert(ctk.END, session_time[0])
        self.session_m_entry.insert(ctk.END, session_time[1])
        self.session_s_entry.insert(ctk.END, session_time[2])

        self.break_h_entry.insert(ctk.END, break_time[0])
        self.break_m_entry.insert(ctk.END, break_time[1])
        self.break_s_entry.insert(ctk.END, break_time[2])

        self.session_number_entry.insert(ctk.END, sessions_number)

        return

    def save_pomodoro(self):
        
        if self.state == 'stopped':
            self.set_pomodoro()
        
        save_pomodoro(
            session_time=f'{self.session_hour}:{self.session_minute}:{self.session_second}',
            break_time=f'{self.break_hour}:{self.break_minute}:{self.break_second}',
            sessions_number=self.session_number
        )

        self.get_saved_pomodoros()

        return

