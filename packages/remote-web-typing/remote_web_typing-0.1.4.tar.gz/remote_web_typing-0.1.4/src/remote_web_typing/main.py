import threading
import time
import pyautogui
import pyperclip
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)
copied_text = ""

# Default typing speed (seconds between keystrokes)
typing_speed = 0.2
typing_cancelled = False  # flag to cancel typing
typing_lock = threading.Lock()

HTML_TEMPLATE = """
<!doctype html>
<title>Remote Typing</title>
<h2>Copied Text:</h2>
<p>{{ copied_text }}</p>

<h2>Type Solution:</h2>
<form method="POST">
  <textarea name="solution" rows="4" cols="50"></textarea><br>
  <input type="submit" value="Send to Laptop">
</form>

<h2>Typing Speed:</h2>
<form method="POST" action="/set_speed">
  <label for="speed">Choose speed:</label>
  <select name="speed">
    <option value="0.05" {% if typing_speed == 0.05 %}selected{% endif %}>Fast (0.05s)</option>
    <option value="0.2" {% if typing_speed == 0.2 %}selected{% endif %}>Normal (0.2s)</option>
    <option value="0.5" {% if typing_speed == 0.5 %}selected{% endif %}>Slow (0.5s)</option>
  </select>
  <input type="submit" value="Set Speed">
</form>

<h2>Controls:</h2>
<form method="POST" action="/cancel">
  <input type="submit" value="Cancel Typing" style="background-color:red; color:white; padding:5px 15px; border:none; border-radius:5px;">
</form>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    global copied_text
    if request.method == "POST":
        solution_text = request.form.get("solution", "").strip()
        if solution_text:
            threading.Thread(target=type_solution_safe, args=(solution_text,), daemon=True).start()
        return redirect(url_for("home"))
    return render_template_string(HTML_TEMPLATE, copied_text=copied_text, typing_speed=typing_speed)


@app.route("/set_speed", methods=["POST"])
def set_speed():
    global typing_speed
    try:
        typing_speed = float(request.form.get("speed", "0.2"))
    except ValueError:
        typing_speed = 0.2
    return redirect(url_for("home"))


@app.route("/cancel", methods=["POST"])
def cancel_typing():
    global typing_cancelled
    typing_cancelled = True
    return redirect(url_for("home"))


def type_solution_safe(text):
    global typing_cancelled
    with typing_lock:
        typing_cancelled = False  # reset before starting
        time.sleep(1)  # Give time to focus target window
        try:
            for char in text:
                if typing_cancelled:
                    print("Typing cancelled!")
                    break
                pyautogui.write(char)
                time.sleep(typing_speed)
        except Exception as e:
            print(f"Error typing text: {e}")


def clipboard_watcher():
    global copied_text
    last_value = ""
    while True:
        try:
            current_value = pyperclip.paste()
            if current_value != last_value:
                last_value = current_value
                copied_text = current_value
        except Exception as e:
            print(f"Clipboard error: {e}")
        time.sleep(0.5)


def main():
    """Entry point for console script"""
    threading.Thread(target=clipboard_watcher, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
