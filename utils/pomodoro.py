import json
from .timer import convert_seconds, start_count


pomodoro_thread = None

def get_pomodoro_thread(thread):
    global pomodoro_thread
    pomodoro_thread = thread
    return

def pomodoro_counter(s_hr_field, s_min_field, s_sec_field, b_hr_field, b_min_field, b_sec_field, s_num_field, event, session_time="00:30:00", break_time="00:10:00", sessions_number=4, break_start_callback=None, session_start_callback=None):
    global pomodoro_thread


    i=0
    while i < sessions_number:
        convert_seconds(session_time)
        start_count(session_time, s_hr_field, s_min_field, s_sec_field, event)
        
        s_num_field.configure(state='normal')
        s_num_field.delete(0, 'end')
        s_num_field.insert('end', str(sessions_number-(i+1)))
        s_num_field.configure(state='disabled')

        if i < sessions_number-1:
            if break_start_callback:
                break_start_callback()

            convert_seconds(break_time)
            start_count(break_time, b_hr_field, b_min_field, b_sec_field, event)

        if session_start_callback and i < sessions_number-1:
            session_start_callback(i+2)

 
        i+=1

    if pomodoro_thread:
        pomodoro_thread.terminate()
        pomodoro_thread = None


def save_pomodoro(session_time='00:30:00', break_time='00:10:00', sessions_number=4):
    try:
                
        data: list = json.load(open('pomodoro.json', 'r'))
        
        data.append({
            'session_time': session_time,
            'break_time': break_time,
            'sessions_number': sessions_number
        })

        with open('pomodoro.json', 'w') as file:
            json.dump(data, file, indent=2)
            print('file edited')

        return 1

    except FileNotFoundError:
        
        with open('pomodoro.json', 'w') as file:
            json.dump([
                {
                'session_time': session_time,
                'break_time': break_time,
                'sessions_number': sessions_number
                }
            ], file, indent=2)
        print('file created')
        
        return 1

def get_pomodoros():

    try:
        data = json.load(open('pomodoro.json', 'r'))
        return data

    except json.decoder.JSONDecodeError:
        return []
    
    except FileNotFoundError:
        return []
    