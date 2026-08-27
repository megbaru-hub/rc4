#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Ensure script directory is in Python path for local imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import rc4Encrypt
import rc4Decryptor

DEFAULT_KEY = "backtohomebutstillmissthesummercamp#INSA#AASTU2018E.C"

class RC4App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RC4 Stream Cipher Tool")
        self.geometry("520x340")
        self.resizable(False, False)
        self.configure(padx=20, pady=15)

        # Header Title
        title_label = ttk.Label(self, text="RC4 File Encryptor & Decryptor", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=(0, 12))

        # Target File Frame
        file_frame = ttk.LabelFrame(self, text=" Target File ", padding=10)
        file_frame.pack(fill="x", pady=5)

        self.file_entry = ttk.Entry(file_frame, width=38)
        default_file = os.path.join(script_dir, "file.txt")
        if os.path.exists(default_file):
            self.file_entry.insert(0, default_file)
        self.file_entry.pack(side="left", padx=(0, 6), fill="x", expand=True)

        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side="right")

        # Secret Key Frame
        key_frame = ttk.LabelFrame(self, text=" Secret Key ", padding=10)
        key_frame.pack(fill="x", pady=8)

        self.key_entry = ttk.Entry(key_frame, width=48)
        self.key_entry.insert(0, DEFAULT_KEY)
        self.key_entry.pack(fill="x")

        # Action Buttons Frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=12)

        encrypt_btn = ttk.Button(btn_frame, text="🔒 Encrypt File", command=self.do_encrypt, width=18)
        encrypt_btn.grid(row=0, column=0, padx=8)

        decrypt_btn = ttk.Button(btn_frame, text="🔓 Decrypt File", command=self.do_decrypt, width=18)
        decrypt_btn.grid(row=0, column=1, padx=8)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready. Select a file and choose an action.")
        status_label = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", padding=6)
        status_label.pack(fill="x", side="bottom")

    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select File to Encrypt or Decrypt")
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def do_encrypt(self):
        filepath = self.file_entry.get().strip()
        key = self.key_entry.get().strip()
        if not filepath:
            messagebox.showerror("Error", "Please specify a valid file path.")
            return
        if not key:
            messagebox.showerror("Error", "Key cannot be empty.")
            return

        try:
            rc4Encrypt.encrypt_file(filepath, key.encode())
            self.status_var.set(f"[+] Successfully encrypted: {os.path.basename(filepath)}")
            messagebox.showinfo("Success", f"File successfully encrypted:\n\n{filepath}")
        except Exception as e:
            self.status_var.set(f"[-] Error: {e}")
            messagebox.showerror("Encryption Error", str(e))

    def do_decrypt(self):
        filepath = self.file_entry.get().strip()
        key = self.key_entry.get().strip()
        if not filepath:
            messagebox.showerror("Error", "Please specify a valid file path.")
            return
        if not key:
            messagebox.showerror("Error", "Key cannot be empty.")
            return

        try:
            rc4Decryptor.decrypt_file(filepath, key.encode())
            self.status_var.set(f"[+] Successfully decrypted: {os.path.basename(filepath)}")
            messagebox.showinfo("Success", f"File successfully decrypted:\n\n{filepath}")
        except Exception as e:
            self.status_var.set(f"[-] Error: {e}")
            messagebox.showerror("Decryption Error", str(e))

if __name__ == "__main__":
    app = RC4App()
    app.mainloop()
