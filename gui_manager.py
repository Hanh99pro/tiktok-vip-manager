import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

ACCOUNTS = {
    "1": "minhanhbg9866",
    "2": "thamvongnhungluoibieng9x",
    "3": "lammyjqjco2",
}


def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)


def start_bot():
    account = account_var.get()
    folder = folder_entry.get()
    wait = wait_entry.get()

    if not account:
        messagebox.showerror("Lỗi", "Bạn chưa chọn nick TikTok")
        return

    if not folder:
        messagebox.showerror("Lỗi", "Bạn chưa chọn folder")
        return

    if not wait.isdigit():
        messagebox.showerror("Lỗi", "Khoảng cách phải là số giây")
        return

    log_box.insert(tk.END, f"Đang chạy nick: {ACCOUNTS[account]}\n")
    log_box.insert(tk.END, f"Folder: {folder}\n")
    log_box.insert(tk.END, f"Khoảng cách: {wait} giây\n")
    log_box.insert(tk.END, "Bot đang chạy...\n\n")

    env = os.environ.copy()
    env["SELECTED_ACCOUNT"] = account
    # env["SELECTED_FOLDER"] = folder
    topic_name = os.path.basename(folder)
    env["SELECTED_TOPIC"] = topic_name
    env["WAIT_SECONDS"] = wait

    subprocess.Popen(
        ["python", "vip_manager.py"],
        env=env
    )


root = tk.Tk()
root.title("TikTok VIP Manager")
root.geometry("600x500")

title = tk.Label(root, text="TikTok VIP Manager", font=("Arial", 20, "bold"))
title.pack(pady=15)

tk.Label(root, text="Chọn nick TikTok").pack()

account_var = tk.StringVar()

for key, name in ACCOUNTS.items():
    tk.Radiobutton(
        root,
        text=f"{key}. {name}",
        variable=account_var,
        value=key
    ).pack(anchor="w", padx=40)

tk.Label(root, text="Chọn folder chủ đề").pack(pady=(15, 0))

folder_frame = tk.Frame(root)
folder_frame.pack(pady=5)

folder_entry = tk.Entry(folder_frame, width=50)
folder_entry.pack(side=tk.LEFT, padx=5)

tk.Button(folder_frame, text="Browse", command=browse_folder).pack(side=tk.LEFT)

tk.Label(root, text="Khoảng cách giữa mỗi video (giây)").pack(pady=(15, 0))

wait_entry = tk.Entry(root, width=20)
wait_entry.insert(0, "300")
wait_entry.pack()

tk.Button(
    root,
    text="START",
    bg="green",
    fg="white",
    font=("Arial", 14, "bold"),
    command=start_bot
).pack(pady=20)

log_box = tk.Text(root, height=10, width=70)
log_box.pack(pady=10)

root.mainloop()