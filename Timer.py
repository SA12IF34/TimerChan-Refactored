import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from winsound import *
from utils.timer import *


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

        


class Timer:

    hours_count = '00'
    minutes_count = '00'
    seconds_count = '00'

    count_event = None
    count_thread = None

    state = 'stopped' # started | paused | stopped
 
    def __init__(self, root):
        self.root = root
        
        self.main_color = "#383838"
        self.secondary_color = "#242424"
        self.font_color = "#ffffff"

        self.page = ctk.CTkFrame(root, fg_color='transparent')
        self.page.pack(fill='both', expand=True)
        
        self.title = ctk.CTkLabel(self.page, width=1, height=1, text='Countdown Timer', font=('Arial', 20), text_color=self.font_color, anchor='center')
        self.title.pack(side='top', fill='x', pady=20)

        self.container = ctk.CTkFrame(self.page, fg_color='transparent')
        self.container.pack(side='bottom', fill='both', expand=True)
        
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        self.timer_container = ctk.CTkFrame(self.container, width=1, fg_color='transparent')
        self.timer_container.grid(column=0, row=0, sticky='n')

        timer_input_kwargs = {
            'font':('Arial', 90), 
            'width':125, 
            'height':20, 
            'fg_color': self.secondary_color,
            'corner_radius': 15,
            'border_width': 2,
            'border_color': 'gray',
            'justify': 'center'
        }


        def validate_input(event):
            widget:ctk.CTkEntry = event.widget
            if len(widget.get()) > 2:
                widget.delete(2, ctk.END)
                widget.xview(0)
                
            return True


        self.hours_input = ctk.CTkEntry(self.timer_container, **timer_input_kwargs)
        self.minutes_input = ctk.CTkEntry(self.timer_container, **timer_input_kwargs)
        self.seconds_input = ctk.CTkEntry(self.timer_container, **timer_input_kwargs)
    
        self.hours_input.bind('<KeyRelease>', validate_input)
        self.minutes_input.bind('<KeyRelease>', validate_input)
        self.seconds_input.bind('<KeyRelease>', validate_input)

        input_pack_kwargs = {
            'side':'left', 
            'anchor':'center', 
            'padx':5, 
            'pady':5,
        }

        self.hours_input.pack(**input_pack_kwargs)
        ctk.CTkLabel(self.timer_container, text=':', font=('Arial', 90), text_color=self.font_color, fg_color='transparent').pack(side='left', anchor='center', padx=5, pady=5)
        self.minutes_input.pack(**input_pack_kwargs)
        ctk.CTkLabel(self.timer_container, text=':', font=('Arial', 90), text_color=self.font_color, fg_color='transparent').pack(side='left', anchor='center', padx=5, pady=5)
        self.seconds_input.pack(**input_pack_kwargs)

        self.hours_input.insert(ctk.END, '00')
        self.minutes_input.insert(ctk.END, '00')
        self.seconds_input.insert(ctk.END, '00')


        self.actions_container = ctk.CTkFrame(self.container, width=1, fg_color='transparent')
        self.actions_container.grid(column=0, row=1, sticky='swen')

        btn_params = {
            'master': self.actions_container,
            'font': ('Arial', 18),
            'fg_color': self.secondary_color,
            'hover_color': 'gray' 
        }

        self.start_btn = ctk.CTkButton(text='Start Count', command=self.start_count, **btn_params)
        self.pause_btn = ctk.CTkButton(text='Pause Count', command=self.pause_count, **btn_params)
        self.reset_btn = ctk.CTkButton(text='Reset Count', command=self.reset_count, **btn_params)

        self.start_btn.pack(side='left', expand=True, anchor='center')
        self.pause_btn.pack(side='left', expand=True, anchor='center')
        self.reset_btn.pack(side='left', expand=True, anchor='center')

        # self.root.master.master.protocol('WM_DELETE_WINDOW', self.on_close)


    def cleanup(self):
        if self.count_thread:
            self.reset_count()

    # def on_close(self):
    #     if self.state == 'started':
    #         self.root.master.master.withdraw()

    #     else:
    #         self.root.master.master.quit()
    #         self.root.master.master.destroy()
        
    #     return

    def start_count(self):
        hours_val = self.hours_input.get()
        minutes_val = self.minutes_input.get()
        seconds_val = self.seconds_input.get()

        seconds_count = convert_seconds(f'{hours_val}:{minutes_val}:{seconds_val}')[0]

        if self.state == 'stopped' and seconds_count > 0:
            self.hours_count = hours_val
            self.minutes_count = minutes_val
            self.seconds_count = seconds_val

            self.count_event = threading.Event()
            self.count_thread = ThreadChan(
                target=start_count,
                args=(
                    f'{hours_val}:{minutes_val}:{seconds_val}',
                    self.hours_input,
                    self.minutes_input,
                    self.seconds_input,
                    self.count_event,
                ),
                callback_func=self.finish_count,
                thread_name='countdown'
            )

            get_count_thread(self.count_thread)
            
    
            self.hours_input.configure(state='disabled')
            self.minutes_input.configure(state='disabled')
            self.seconds_input.configure(state='disabled')
            self.count_thread.start()
            self.count_event.set()
            
            
            self.state = 'started'



        return

        

    def pause_count(self):
        hours_val = self.hours_input.get()
        minutes_val = self.minutes_input.get()
        seconds_val = self.seconds_input.get()

        seconds_count = convert_seconds(f'{hours_val}:{minutes_val}:{seconds_val}')[0]
        if seconds_count > 0:
            if self.state == 'started' and self.count_event and self.count_event.is_set():
                self.count_event.clear()

                self.pause_btn.configure(text='Resume Count')
                self.state = 'paused'
            elif self.state == 'paused' and self.count_event and not self.count_event.is_set():
                self.count_event.set()
                
                self.pause_btn.configure(text='Pause Count')
                self.state = 'started'

        return

    def finish_count(self, normal=True):
        

        self.hours_input.configure(state='normal')
        self.minutes_input.configure(state='normal')
        self.seconds_input.configure(state='normal')

        for widget in (self.hours_input, self.minutes_input, self.seconds_input):
            widget.delete(0, 'end')
            widget.insert(ctk.END, '00')

        self.hours_count = '00'
        self.minutes_count = '00'
        self.seconds_count = '00'

        if self.state == 'started' and normal:
                
            PlaySound('utils/alarm.wav', 1)
            CTkMessagebox(title='Finished!', message='Countdown finished!', icon='check')

        
        self.pause_btn.configure(text='Pause Count')

        self.count_event = None
        self.count_thread = None
        self.state = 'stopped'

        return

    async def play_sound(self):
        PlaySound('utils/alarm.wav', 1)
        return

    def reset_count(self):
        
        if self.count_event:
            if not self.count_event.is_set():
                self.count_event.set()

            self.count_thread.terminate(normal=False)

        
        return
        