import time


seconds = 0
hours_time = 0
minutes_time = 0
seconds_time = 0
hours_input = '00'
minutes_input = '00'
seconds_input = '00'
count_event = None
count_thread = None
stop_flag = False

def set_time(time):

    return time

def convert_seconds(countdown_amount):
    assert len(countdown_amount) > 0 and len(countdown_amount.split(':')) == 3
    
    global seconds
    global hours_time
    global minutes_time
    global seconds_time

    sliptted_time = countdown_amount.split(':')

    seconds = 0
    hours_time = 0
    minutes_time = 0
    seconds_time = 0

    for i in range(len(sliptted_time)):
        if int(sliptted_time[i]) == 0:
            continue

        int_time = int(sliptted_time[i])
        if i == 0:
            seconds += int_time*60*60
            hours_time = int_time*60*60
        elif i == 1:
            seconds += int_time*60
            minutes_time = int_time*60

        elif i == 2:
            seconds += int_time
            seconds_time = int_time

    return seconds, hours_time, minutes_time, seconds_time


def set_stop_flag(value):
    global stop_flag
    stop_flag = value
    return 0

def get_count_thread(thread):
    global count_thread
    count_thread = thread
    return

def countdown_seconds(seconds_range, countdown_amount):
    global seconds
    global seconds_input
    global count_event
    global count_thread
    global stop_flag

    for i in range(seconds_range):
        
        if stop_flag:
            return -1
        
        count_event.wait()
        if count_event.is_set():
            time.sleep(1)
            seconds -= 1

            if type(countdown_amount) == str:
                countdown_amount = countdown_amount.split(':')

            val = str(int(countdown_amount[2])-1)
            val = val if len(val) == 2 else '0'+val
            countdown_amount[2] = val
            countdown_amount = ':'.join(countdown_amount)
            
            seconds_input.configure(state='normal')
            seconds_input.delete(0, 'end')
            seconds_input.insert('end', val)
            seconds_input.configure(state='disabled')

            if seconds == 0:
                if count_thread is not None:
                    count_thread.terminate()
                    count_thread = None


def countdown_minutes(minutes_range, countdown_amount):
    global minutes_input
    global seconds_input
    global stop_flag

    for i in range(minutes_range):
        if stop_flag:
            return -1
        if type(countdown_amount) == str:
            countdown_amount = countdown_amount.split(':')
        
        minutes_range -= 1

        val = str(minutes_range)
        val = val if len(val) == 2 else '0'+val
        countdown_amount[1] = val
        countdown_amount[2] = '60'
        
        minutes_input.configure(state='normal')
        minutes_input.delete(0, 'end')
        minutes_input.insert('end', val)
        minutes_input.configure(state='disabled')

        seconds_input.configure(state='normal')
        seconds_input.delete(0, 'end')
        seconds_input.insert('end', '60')
        seconds_input.configure(state='disabled')

        countdown_seconds(60, countdown_amount)

def countdown_hours(hours_range, countdown_amount):
    global hours_input
    global minutes_input
    global stop_flag

    for i in range(hours_range):
        if stop_flag:
            return -1
        
        if type(countdown_amount) == str:
            countdown_amount = countdown_amount.split(':')

        hours_range -= 1
        val = str(hours_range)
        val = val if len(val) == 2 else '0'+val
        countdown_amount[0] = val
        countdown_amount[1] = '60'

        hours_input.configure(state='normal')
        hours_input.delete(0, 'end')
        hours_input.insert('end', val)
        hours_input.configure(state='disabled')

        minutes_input.configure(state='normal')
        minutes_input.delete(0, 'end')
        minutes_input.insert('end', '60')
        minutes_input.configure(state='disabled')

        countdown_minutes(60, countdown_amount)


def start_count(countdown_amount, h_input, m_input, s_input, event):
    global seconds
    global seconds_time
    global minutes_time
    global hours_time
    global hours_input
    global minutes_input
    global seconds_input
    global count_event
    global stop_flag

    hours_input = h_input
    minutes_input = m_input
    seconds_input = s_input

    count_event = event

    if seconds == 0:
        return -1
    
    if seconds_time > 0 and (seconds - seconds_time) == (hours_time+minutes_time):
        countdown_seconds(seconds_time, countdown_amount)
        
    if minutes_time > 0 and (seconds - minutes_time) == (hours_time):
        num_of_mins = int(minutes_time/60)

        countdown_minutes(num_of_mins, countdown_amount)
            
    if hours_time > 0 and (seconds - hours_time) == 0:
        num_of_hours = int((hours_time/60)/60)

        countdown_hours(num_of_hours, countdown_amount)

    if stop_flag:
        return -1



