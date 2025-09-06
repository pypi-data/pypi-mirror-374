import os
import threading
import time
import winsound

_is_looping = False
_loop_thread = None

def _beep(frequency=440, duration=200):
    winsound.Beep(frequency, duration)

def _play_and_fallback(filepath, block=True):
    try:
        if not os.path.exists(filepath):
            _beep()
            return
        winsound.PlaySound(filepath, winsound.SND_FILENAME | (0 if block else winsound.SND_ASYNC))
    except Exception:
        _beep()

def play_sound(filepath):
    _play_and_fallback(filepath)

def _loop_worker(filepath):
    global _is_looping
    while _is_looping:
        _play_and_fallback(filepath)
        time.sleep(0.1)  # Small delay to prevent high CPU usage

def loop_sound(filepath):
    global _is_looping, _loop_thread
    if _is_looping:
        return
    
    _is_looping = True
    _loop_thread = threading.Thread(target=_loop_worker, args=(filepath,), daemon=True)
    _loop_thread.start()

def stop_loop():
    global _is_looping
    _is_looping = False

def sequence_sounds(filepaths, interval=1):
    for filepath in filepaths:
        _play_and_fallback(filepath)
        time.sleep(interval)