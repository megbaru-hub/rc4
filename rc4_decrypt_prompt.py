#!/usr/bin/env python3
"""
RC4 Decryptor Prompt - Interactive Password Prompt for Encrypted Files
Author: megbaru dessie
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

# Local import
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import rc4Decryptor

DEFAULT_KEY = "backtohomebutstillmissthesummercamp#INSA#AASTU2018E.C"


class DecryptPromptApp(tk.Tk):
    def __init__(self, target_file: str = None):
        super().__init__()
        self.target_file = target_file
        
        self.title("Unlock Encrypted File - RC4")
        self.geometry("520x330")
        self.minsize(480, 300)
        self.resizable(True, True)

        # Style
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Header
        header = tk.Frame(self, bg="#0f172a", height=60)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="🔐 Unlock Encrypted File", font=("Helvetica", 13, "bold"), bg="#0f172a", fg="white")
        lbl_title.pack(side="left", padx=16, pady=12)

        # Main Body
        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)

        # File display
        file_frame = ttk.LabelFrame(body, text=" Encrypted File ", padding=8)
        file_frame.pack(fill="x", pady=(0, 10))

        display_name = os.path.basename(self.target_file) if self.target_file else "No file selected"
        file_size = ""
        if self.target_file and os.path.isfile(self.target_file):
            sz = os.path.getsize(self.target_file)
            if sz < 1024:
                file_size = f" ({sz} bytes)"
            elif sz < 1024 * 1024:
                file_size = f" ({sz / 1024:.1f} KB)"
            else:
                file_size = f" ({sz / (1024 * 1024):.2f} MB)"

        self.lbl_file = ttk.Label(file_frame, text=f"📄 {display_name}{file_size}", font=("Helvetica", 10, "bold"))
        self.lbl_file.pack(anchor="w")

        # Password Entry
        key_frame = ttk.LabelFrame(body, text=" Enter Decryption Key ", padding=8)
        key_frame.pack(fill="x", pady=(0, 12))

        self.key_var = tk.StringVar(value=DEFAULT_KEY)
        self.entry_key = ttk.Entry(key_frame, textvariable=self.key_var, show="•", font=("Courier", 10))
        self.entry_key.pack(fill="x", pady=(0, 6))
        self.entry_key.focus_set()

        opt_frame = ttk.Frame(key_frame)
        opt_frame.pack(fill="x")

        self.show_key_var = tk.BooleanVar(value=False)
        chk_show = ttk.Checkbutton(opt_frame, text="Show Key Characters", variable=self.show_key_var, command=self.toggle_show)
        chk_show.pack(side="left")

        btn_default = ttk.Button(opt_frame, text="Use Default Key", command=lambda: self.key_var.set(DEFAULT_KEY))
        btn_default.pack(side="right")

        # Buttons
        btn_box = ttk.Frame(body)
        btn_box.pack(fill="x", pady=6)

        btn_open = tk.Button(btn_box, text="🔓 Decrypt & Open File", command=lambda: self.decrypt(open_after=True), bg="#10b981", fg="white", font=("Helvetica", 10, "bold"), padx=12, pady=6, cursor="hand2")
        btn_open.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_decrypt_only = tk.Button(btn_box, text="🔓 Decrypt Only", command=lambda: self.decrypt(open_after=False), bg="#0284c7", fg="white", font=("Helvetica", 10, "bold"), padx=12, pady=6, cursor="hand2")
        btn_decrypt_only.pack(side="left", fill="x", expand=True, padx=4)

        btn_cancel = ttk.Button(btn_box, text="Cancel", command=self.destroy)
        btn_cancel.pack(side="right", padx=(4, 0))

        # Status
        self.status_var = tk.StringVar(value="Enter the password/key and click Decrypt.")
        lbl_status = ttk.Label(self, textvariable=self.status_var, relief="groove", padding=5, font=("Helvetica", 8))
        lbl_status.pack(fill="x", side="bottom")

        # Enter key triggers Decrypt & Open
        self.bind("<Return>", lambda e: self.decrypt(open_after=True))

    def toggle_show(self):
        self.entry_key.configure(show="" if self.show_key_var.get() else "•")

    def decrypt(self, open_after: bool = False):
        if not self.target_file or not os.path.isfile(self.target_file):
            messagebox.showerror("Error", "Target encrypted file not found.")
            return

        key = self.key_var.get().strip()
        if not key:
            messagebox.showerror("Error", "Please enter the decryption key.")
            return

        target_file = self.target_file
        # Determine output file name
        if target_file.endswith(".rc4"):
            output_file = target_file[:-4]
            # Decrypt to stripped name
            try:
                with open(target_file, "rb") as f:
                    ciphertext = f.read()
                S = rc4Decryptor.ksa(key.encode("utf-8"))
                plaintext = rc4Decryptor.prga(S, ciphertext)
                with open(output_file, "wb") as f:
                    f.write(plaintext)
                # Remove .rc4 file
                os.remove(target_file)
                target_file = output_file
            except Exception as e:
                messagebox.showerror("Decryption Error", str(e))
                return
        else:
            try:
                rc4Decryptor.decrypt_file(target_file, key.encode("utf-8"))
            except Exception as e:
                messagebox.showerror("Decryption Error", str(e))
                return

        self.status_var.set(f"[+] Successfully decrypted {os.path.basename(target_file)}")

        if open_after:
            try:
                subprocess.Popen(["xdg-open", target_file])
            except Exception as e:
                pass
            self.destroy()
        else:
            messagebox.showinfo("Success", f"File decrypted successfully:\n\n{target_file}")
            self.destroy()


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if not target:
        # Ask for file
        import tkinter.filedialog as fd
        root = tk.Tk()
        root.withdraw()
        target = fd.askopenfilename(title="Select Encrypted File to Unlock")
        root.destroy()
        if not target:
            sys.exit(0)

    app = DecryptPromptApp(target)
    app.mainloop()


if __name__ == "__main__":
    main()
