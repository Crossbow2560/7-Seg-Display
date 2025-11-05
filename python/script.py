import pygame
import sys
import threading
import queue
import subprocess
import os
import time

pygame.init()

# --- Window setup ---
WIDTH, HEIGHT = 300, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("7-Segment Display Simulation")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (60, 0, 0)

# --- Segment coordinates ---
# Positions of segments: 1 to 7
segment_coords = {
    1: ((80, 50, 140, 20)),   # top
    2: ((220, 70, 20, 120)),  # top-right
    3: ((220, 210, 20, 120)), # bottom-right
    4: ((80, 330, 140, 20)),  # bottom
    5: ((60, 210, 20, 120)),  # bottom-left
    6: ((60, 70, 20, 120)),   # top-left
    7: ((80, 190, 140, 20)),  # middle
}

# Each segment is drawn as a rectangle
def draw_segment(num, on):
    x, y, w, h = segment_coords[num]
    color = RED if on else DARK_RED
    pygame.draw.rect(WIN, color, (x, y, w, h), border_radius=5)

# Function to set segments based on binary input
def set_segments(state):
    """
    state: 7-character string (e.g. "1001010")
    1 = ON, 0 = OFF
    Segment order: 1 (top), 2 (top-right), 3 (bottom-right),
                   4 (bottom), 5 (bottom-left), 6 (top-left), 7 (center)
    """
    WIN.fill(BLACK)
    for i, s in enumerate(state, start=1):
        draw_segment(i, s == '1')
    pygame.display.update()


def get_user_input(prompt="Enter 7-bit binary (e.g. 1001010): "):
    """
    Prompt the user for a 7-bit binary string and validate it.

    Returns:
        str: 7-character string of '0'/'1' on success
        None: if the user cancels (empty line) or EOF is encountered
    """
    try:
        user_input = input(prompt)
    except EOFError:
        # Input stream closed; signal EOF to caller
        return "__EOF__"

    if user_input is None:
        return None

    user_input = user_input.strip()
    if user_input == "":
        # empty input used as cancel
        return None

    if len(user_input) == 7 and all(c in "01" for c in user_input):
        return user_input

    print("Invalid input! Must be 7 bits of 0s and 1s.")
    return None

def filterCode(x):
    if x == '0':
        return False
    return True

def inputFromVerilog():
    base_dir = os.path.dirname(os.path.abspath(__file__))      # ...\code\python
    code_dir = os.path.normpath(os.path.join(base_dir, ".."))  # ...\code
    main_dir = os.path.join(code_dir, "main")
    modules_dir = os.path.join(code_dir, "modules")
    sim_path = os.path.join(main_dir, "sim.vvp")
    seg = os.path.join(main_dir, "seg7v.v")
    tb  = os.path.join(main_dir, "seg7v_tb.v")

    if not (os.path.exists(seg) and os.path.exists(tb)):
        print("Missing seg7v.v or seg7v_tb.v in", main_dir, file=sys.stderr)
        return

    # compile: run from main_dir so relative `\`include "../modules/..."` resolves
    cmd = ["iverilog", "-I", modules_dir, "-o", sim_path, seg, tb]
    try:
        compile_res = subprocess.run(cmd, cwd=main_dir, capture_output=True, text=True, check=True)
        if compile_res.stdout:
            print(compile_res.stdout)
        if compile_res.stderr:
            print(compile_res.stderr, file=sys.stderr)
    except FileNotFoundError:
        print("iverilog not found. Install Icarus Verilog and add it to PATH.", file=sys.stderr)
        return
    except subprocess.CalledProcessError as e:
        print("Compilation failed:\n", e.stderr or e.stdout, file=sys.stderr)
        return

    # run simulation from main_dir
    try:
        run_res = subprocess.run(["vvp", sim_path], cwd=main_dir, capture_output=True, text=True, timeout=10)
        print(run_res.stdout)
        result_list = list(filter(filterCode, run_res.stdout.split()[9:-6]))
        print(result_list)
        if run_res.stderr:
            print(run_res.stderr, file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("vvp timed out (testbench may not finish or no $finish).", file=sys.stderr)
    except FileNotFoundError:
        print("vvp not found. Install Icarus Verilog and add it to PATH.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print("Simulation failed:\n", e.stderr or e.stdout, file=sys.stderr)
    return result_list



def input_reader(q, prompt=""):
    """Background thread that reads user input from terminal and pushes valid
    7-bit patterns to the queue. On EOF it pushes a special '__EOF__' token
    and exits."""
    while True:
        v = get_user_input(prompt)
        if v == "__EOF__":
            # propagate EOF and exit thread
            q.put(v)
            break
        if v is None:
            # invalid or empty input — ignore and continue
            continue
        q.put(v)


def verilog_input_thread(q, delay=1):
    """Run inputFromVerilog(), enqueue parsed states (one per `delay` seconds)."""
    result_list = inputFromVerilog()
    if not result_list:
        return

    # If elements are full 7-bit strings, push them directly.
    if all(isinstance(x, str) and len(x) == 7 for x in result_list):
        for s in result_list:
            # treat '0000000' as an invalid marker (same behavior as grouped path)
            print(f"Current Input: {s}")
            if s == '0000000':
                print("Invalid Number (number must be in range 0-9)")
            q.put(s)
            time.sleep(delay)
        # finished iterating the returned list
        print(f"Verilog playback complete: processed {len(result_list)} states. Now quitting Program")
        q.put("__DONE__")
        return


def main_code():
    result_li = inputFromVerilog()
    for i in range(len(result_li)):
        pass

# --- Main loop ---
def main():
    clock = pygame.time.Clock()
    state = "0000000"  # All off
    set_segments(state)
    # queue for communicating input from terminal thread
    q = queue.Queue()
    t = threading.Thread(target=input_reader, args=(q,), daemon=True)
    t.start()
    # start Verilog input thread which will enqueue parsed states every second
    vt = threading.Thread(target=verilog_input_thread, args=(q,), daemon=True)
    vt.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Press Escape to quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # process any terminal input (non-blocking)
        try:
            while True:
                new_state = q.get_nowait()
                if new_state == "__EOF__":
                    # EOF on stdin — exit cleanly
                    pygame.quit()
                    sys.exit()

                if new_state == "__DONE__":
                    time.sleep(2)
                    pygame.quit()
                    sys.exit()
                # update display for valid 7-bit pattern
                state = new_state
                set_segments(state)
        except queue.Empty:
            pass

        clock.tick(30)

if __name__ == "__main__":
    main()
