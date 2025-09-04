import sys
import threading
from flask import Flask, request

# 检查tkinter是否可用
try:
    import tkinter as tk
except ImportError:
    print("❌ 错误: tkinter 不可用")
    print("请安装tkinter支持：")
    print("macOS: brew install python-tk")
    print("Linux: sudo apt-get install python3-tk")
    print("Windows: 重新安装Python")
    sys.exit(1)

app = Flask(__name__)
logs = []


@app.route("/log", methods=["POST"])
def log():
    global logs
    logs.append(request.json.get("msg"))
    if len(logs) > 50:
        logs.pop(0)
    return {"status": "ok"}


def run_flask():
    app.run(port=8765)


def run_ui():
    root = tk.Tk()
    root.title("DeskLog")
    root.geometry("400x200+1000+40")  # 放右上角
    root.configure(bg="black")

    text = tk.Text(root, bg="black", fg="lime", font=("Menlo", 12))
    text.pack(expand=True, fill="both")

    def update_logs():
        text.delete(1.0, tk.END)
        for line in logs[-10:]:
            text.insert(tk.END, line + "\n")
        root.after(500, update_logs)

    root.after(500, update_logs)
    root.attributes("-topmost", True)  # 置顶
    root.overrideredirect(True)  # 去边框
    root.mainloop()


def start():
    threading.Thread(target=run_flask, daemon=True).start()
    run_ui()
