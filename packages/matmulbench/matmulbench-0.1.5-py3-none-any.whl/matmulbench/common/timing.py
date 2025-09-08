import time
start_time = None

def start_timer():
    global start_time
    # start_time = time.perf_counter()
    start_time = time.perf_counter_ns()

def end_timer():
    global start_time
    # end_time = time.perf_counter()
    end_time = time.perf_counter_ns()
    diff = end_time - start_time
    start_time = None
    # return round(diff, 6)
    return round(diff/1e9, 6)