#!/usr/bin/env python3
"""
RC4 Stream Cipher - Interactive Graphical User Interface
Author: megbaru dessie
"""

import os
import sys
import time
import base64
import hashlib
import secrets
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Ensure script directory is in Python path for local imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import rc4Encrypt
import rc4Decryptor

DEFAULT_KEY = "backtohomebutstillmissthesummercamp#INSA#AASTU2018E.C"


def get_file_info(filepath: str):
    """Returns existence, formatted size, and SHA-256 of file."""
    if not filepath or not os.path.exists(filepath):
        return False, "File not found", "-"
    if not os.path.isfile(filepath):
        return False, "Is a directory", "-"
    
    size = os.path.getsize(filepath)
    if size < 1024:
        size_str = f"{size} bytes"
    elif size < 1024 * 1024:
        size_str = f"{size / 1024:.2f} KB ({size} bytes)"
    else:
        size_str = f"{size / (1024 * 1024):.2f} MB ({size} bytes)"

    try:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return True, size_str, hasher.hexdigest()[:24] + "..."
    except Exception as e:
        return False, size_str, f"Error: {e}"


def get_file_preview(filepath: str, max_bytes: int = 512):
    """Returns text or formatted hex preview of file."""
    if not filepath or not os.path.isfile(filepath):
        return "[File does not exist or invalid path selected]"
    try:
        with open(filepath, "rb") as f:
            data = f.read(max_bytes)
        
        if len(data) == 0:
            return "[Empty File - 0 bytes]"

        # Try decoding as utf-8
        try:
            text = data.decode("utf-8")
            if text.isprintable() or any(c in "\n\r\t" for c in text):
                return f"[Plaintext Preview - {len(data)} bytes shown]:\n\n{text}"
        except UnicodeDecodeError:
            pass

        # Fallback to formatted hex dump
        hex_dump = []
        for i in range(0, min(len(data), 128), 16):
            chunk = data[i:i+16]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            hex_dump.append(f"{i:04x}  {hex_part:<48}  |{ascii_part}|")
        return f"[Binary / Ciphertext Hex Dump - {len(data)} bytes]:\n\n" + "\n".join(hex_dump)
    except Exception as e:
        return f"[Error reading preview: {e}]"


class ModernRC4App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RC4 Stream Cipher Suite")
        self.geometry("720x600")
        self.minsize(660, 540)

        # Style configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        self.style.configure("TNotebook", background="#f1f5f9")
        self.style.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[14, 6])

        # Header Banner
        header_frame = tk.Frame(self, bg="#0f172a", height=60)
        header_frame.pack(fill="x", side="top")
        
        title_lbl = tk.Label(header_frame, text="🔒 RC4 Stream Cipher Suite", font=("Helvetica", 14, "bold"), bg="#0f172a", fg="#ffffff")
        title_lbl.pack(side="left", padx=18, pady=12)

        subtitle_lbl = tk.Label(header_frame, text="File & Stream Cryptography System", font=("Helvetica", 9), bg="#0f172a", fg="#94a3b8")
        subtitle_lbl.pack(side="right", padx=18, pady=15)

        # Bottom Status Bar (Initialized first)
        self.status_var = tk.StringVar(value="Ready. Select a file or enter text to begin.")
        status_bar = tk.Label(self, textvariable=self.status_var, relief="groove", anchor="w", font=("Helvetica", 9), bg="#e2e8f0", fg="#334155", padx=10, pady=5)
        status_bar.pack(fill="x", side="bottom")

        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=8)

        # Tab 1: File Encryptor/Decryptor
        self.tab_file = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_file, text=" 📁 File Cipher ")
        self.init_file_tab()

        # Tab 2: Text Playground
        self.tab_text = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_text, text=" ✍️ Text Playground ")
        self.init_text_tab()

        # Tab 3: S-Box Visualizer & Tests
        self.tab_diag = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_diag, text=" ⚙️ S-Box & Tests ")
        self.init_diag_tab()

    # =========================================================================
    # TAB 1: ENHANCED FILE CIPHER TAB
    # =========================================================================
    def init_file_tab(self):
        # 1. Enhanced Target File Frame
        file_frame = ttk.LabelFrame(self.tab_file, text=" 📂 Select Target File ", padding=10)
        file_frame.pack(fill="x", pady=(0, 6))

        # Row 1: File path Combobox with Dropdown History + Browse Button
        row1 = ttk.Frame(file_frame)
        row1.pack(fill="x", pady=(0, 6))

        self.file_path_var = tk.StringVar()
        default_file = os.path.join(script_dir, "file.txt")
        self.file_path_var.set(default_file if os.path.exists(default_file) else "")

        # Build list of common/recent files
        self.recent_files = [default_file]
        for f in [os.path.join(script_dir, "check.txt"), os.path.expanduser("~/Downloads/check.txt")]:
            if os.path.exists(f) and f not in self.recent_files:
                self.recent_files.append(f)

        self.combo_file = ttk.Combobox(row1, textvariable=self.file_path_var, values=self.recent_files, font=("Courier", 9))
        self.combo_file.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.combo_file.bind("<<ComboboxSelected>>", lambda e: self.on_file_changed())

        btn_browse = tk.Button(row1, text="📁 Browse...", command=self.browse_target_file, bg="#2563eb", fg="white", font=("Helvetica", 9, "bold"), padx=10, pady=3, relief="raised", cursor="hand2")
        btn_browse.pack(side="right")

        # Row 2: Quick Action Helper Buttons
        row2 = ttk.Frame(file_frame)
        row2.pack(fill="x")

        btn_default = ttk.Button(row2, text="📄 Default (file.txt)", command=self.load_default_file)
        btn_default.pack(side="left", padx=(0, 6))

        btn_new_sample = ttk.Button(row2, text="➕ Create Sample File", command=self.create_sample_file)
        btn_new_sample.pack(side="left", padx=(0, 6))

        btn_reload = ttk.Button(row2, text="🔄 Reload File", command=self.on_file_changed)
        btn_reload.pack(side="right")

        # 2. File Metadata Badge Card
        self.badge_card = tk.Frame(self.tab_file, bg="#1e293b", padx=12, pady=6)
        self.badge_card.pack(fill="x", pady=(0, 6))

        self.lbl_badge_icon = tk.Label(self.badge_card, text="🟢", font=("Helvetica", 10), bg="#1e293b", fg="#4ade80")
        self.lbl_badge_icon.pack(side="left", padx=(0, 8))

        self.file_info_var = tk.StringVar(value="Analyzing file...")
        self.lbl_badge_text = tk.Label(self.badge_card, textvariable=self.file_info_var, font=("Courier", 8), bg="#1e293b", fg="#f8fafc", anchor="w")
        self.lbl_badge_text.pack(side="left", fill="x", expand=True)

        # 3. Secret Key Configuration Frame
        key_frame = ttk.LabelFrame(self.tab_file, text=" 🔑 Secret Encryption Key ", padding=8)
        key_frame.pack(fill="x", pady=(0, 6))

        self.key_var = tk.StringVar(value=DEFAULT_KEY)
        self.show_key_var = tk.BooleanVar(value=True)

        self.entry_key = ttk.Entry(key_frame, textvariable=self.key_var, font=("Courier", 9))
        self.entry_key.pack(fill="x", pady=(0, 6))

        key_btn_frame = ttk.Frame(key_frame)
        key_btn_frame.pack(fill="x")

        chk_show = ttk.Checkbutton(key_btn_frame, text="Show Key Characters", variable=self.show_key_var, command=self.toggle_key_visibility)
        chk_show.pack(side="left")

        btn_key_default = ttk.Button(key_btn_frame, text="Reset Default", command=lambda: self.key_var.set(DEFAULT_KEY))
        btn_key_default.pack(side="right", padx=2)

        btn_random_key = ttk.Button(key_btn_frame, text="🎲 Generate Random Key", command=self.generate_random_key)
        btn_random_key.pack(side="right", padx=2)

        # 4. Action Buttons (Encrypt / Decrypt)
        btn_container = ttk.Frame(self.tab_file)
        btn_container.pack(fill="x", pady=6)

        btn_encrypt = tk.Button(btn_container, text="🔒 Encrypt File", command=self.encrypt_selected_file, bg="#0284c7", fg="white", font=("Helvetica", 10, "bold"), relief="raised", padx=14, pady=7, cursor="hand2")
        btn_encrypt.pack(side="left", expand=True, fill="x", padx=(0, 4))

        btn_decrypt = tk.Button(btn_container, text="🔓 Decrypt File", command=self.decrypt_selected_file, bg="#10b981", fg="white", font=("Helvetica", 10, "bold"), relief="raised", padx=14, pady=7, cursor="hand2")
        btn_decrypt.pack(side="right", expand=True, fill="x", padx=(4, 0))

        # 5. Live File Preview & Hex Dump Display
        preview_frame = ttk.LabelFrame(self.tab_file, text=" 👁️ Live File Content & Hex Dump Preview ", padding=6)
        preview_frame.pack(fill="both", expand=True, pady=(2, 0))

        self.txt_preview = tk.Text(preview_frame, height=7, font=("Courier", 8), bg="#0f172a", fg="#38bdf8", insertbackground="white", wrap="none")
        self.txt_preview.pack(fill="both", expand=True, side="left")

        scroll_preview = ttk.Scrollbar(preview_frame, orient="vertical", command=self.txt_preview.yview)
        scroll_preview.pack(side="right", fill="y")
        self.txt_preview.configure(yscrollcommand=scroll_preview.set)

        # Trace file changes for auto-update
        self.file_path_var.trace_add("write", lambda *args: self.on_file_changed())
        self.on_file_changed()

    def on_file_changed(self):
        filepath = self.file_path_var.get().strip()
        exists, size_info, hash_val = get_file_info(filepath)
        
        if exists:
            self.lbl_badge_icon.configure(text="🟢", fg="#4ade80")
            self.file_info_var.set(f"Status: Ready  |  Size: {size_info}  |  SHA-256: {hash_val}")
        else:
            self.lbl_badge_icon.configure(text="🔴", fg="#ef4444")
            self.file_info_var.set(f"Status: Missing File  |  Path: {os.path.basename(filepath) if filepath else 'None'}")

        # Update preview box
        preview = get_file_preview(filepath)
        self.txt_preview.delete("1.0", tk.END)
        self.txt_preview.insert("1.0", preview)

    def load_default_file(self):
        default_file = os.path.join(script_dir, "file.txt")
        if not os.path.exists(default_file):
            with open(default_file, "w", encoding="utf-8") as f:
                f.write("This is the Orginal text file before encrypted.\n")
        self.file_path_var.set(default_file)
        self.status_var.set(f"Loaded default sample file: {default_file}")

    def create_sample_file(self):
        filename = filedialog.asksaveasfilename(
            title="Create Sample Test File",
            initialdir=script_dir,
            initialfile="sample_test.txt",
            defaultextension=".txt",
            filetypes=[("Text Files (*.txt)", "*.txt"), ("All Files (*.*)", "*.*")]
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("RC4 symmetric cipher sample verification file created for testing.\n")
            if filename not in self.recent_files:
                self.recent_files.append(filename)
                self.combo_file.configure(values=self.recent_files)
            self.file_path_var.set(filename)
            self.status_var.set(f"Created new test file: {os.path.basename(filename)}")
            messagebox.showinfo("File Created", f"Sample file created:\n\n{filename}")

    def browse_target_file(self):
        f = filedialog.askopenfilename(
            title="Select File to Encrypt or Decrypt",
            filetypes=[("All Files (*.*)", "*.*"), ("Text Files (*.txt)", "*.txt"), ("Binary Files (*.bin;*.dat)", "*.bin;*.dat")]
        )
        if f:
            if f not in self.recent_files:
                self.recent_files.append(f)
                self.combo_file.configure(values=self.recent_files)
            self.file_path_var.set(f)
            self.status_var.set(f"Selected file: {f}")

    def toggle_key_visibility(self):
        if self.show_key_var.get():
            self.entry_key.configure(show="")
        else:
            self.entry_key.configure(show="•")

    def generate_random_key(self):
        new_key = secrets.token_hex(16)
        self.key_var.set(new_key)
        self.status_var.set(f"Generated new random 128-bit key ({new_key[:8]}...)")

    def encrypt_selected_file(self):
        filepath = self.file_path_var.get().strip()
        key = self.key_var.get().strip()
        if not filepath or not os.path.isfile(filepath):
            messagebox.showerror("Error", "Please select a valid existing file.")
            return
        if not key:
            messagebox.showerror("Error", "Encryption key cannot be empty.")
            return

        t0 = time.perf_counter()
        try:
            rc4Encrypt.encrypt_file(filepath, key.encode())
            elapsed = (time.perf_counter() - t0) * 1000
            self.on_file_changed()
            self.status_var.set(f"[+] Encrypted '{os.path.basename(filepath)}' in {elapsed:.2f} ms.")
            messagebox.showinfo("Encryption Complete", f"Successfully encrypted:\n\n{filepath}\nProcessing time: {elapsed:.2f} ms")
        except Exception as e:
            self.status_var.set(f"[-] Encryption failed: {e}")
            messagebox.showerror("Encryption Error", str(e))

    def decrypt_selected_file(self):
        filepath = self.file_path_var.get().strip()
        key = self.key_var.get().strip()
        if not filepath or not os.path.isfile(filepath):
            messagebox.showerror("Error", "Please select a valid existing file.")
            return
        if not key:
            messagebox.showerror("Error", "Decryption key cannot be empty.")
            return

        t0 = time.perf_counter()
        try:
            rc4Decryptor.decrypt_file(filepath, key.encode())
            elapsed = (time.perf_counter() - t0) * 1000
            self.on_file_changed()
            self.status_var.set(f"[+] Decrypted '{os.path.basename(filepath)}' in {elapsed:.2f} ms.")
            messagebox.showinfo("Decryption Complete", f"Successfully decrypted:\n\n{filepath}\nProcessing time: {elapsed:.2f} ms")
        except Exception as e:
            self.status_var.set(f"[-] Decryption failed: {e}")
            messagebox.showerror("Decryption Error", str(e))

    # =========================================================================
    # TAB 2: TEXT PLAYGROUND TAB
    # =========================================================================
    def init_text_tab(self):
        lbl_intro = tk.Label(self.tab_text, text="Type or paste text below to see live RC4 stream transformation in real time:", font=("Helvetica", 9), fg="#475569")
        lbl_intro.pack(anchor="w", pady=(0, 6))

        # Plaintext frame
        frame_input = ttk.LabelFrame(self.tab_text, text=" Input Plaintext ", padding=6)
        frame_input.pack(fill="both", expand=True, pady=3)

        self.txt_input = tk.Text(frame_input, height=5, font=("Helvetica", 9), wrap="word")
        self.txt_input.insert("1.0", "Hello World! This is an interactive RC4 stream cipher test.")
        self.txt_input.pack(fill="both", expand=True)

        # Key & Format options
        opts_frame = ttk.Frame(self.tab_text)
        opts_frame.pack(fill="x", pady=5)

        ttk.Label(opts_frame, text="Key:").pack(side="left", padx=(0, 4))
        self.txt_play_key = ttk.Entry(opts_frame, width=28)
        self.txt_play_key.insert(0, DEFAULT_KEY)
        self.txt_play_key.pack(side="left", padx=(0, 10))

        self.fmt_var = tk.StringVar(value="Hex")
        ttk.Label(opts_frame, text="Format:").pack(side="left", padx=(0, 4))
        ttk.Radiobutton(opts_frame, text="Hex", value="Hex", variable=self.fmt_var).pack(side="left", padx=2)
        ttk.Radiobutton(opts_frame, text="Base64", value="Base64", variable=self.fmt_var).pack(side="left", padx=2)

        btn_run_text = tk.Button(opts_frame, text="⚡ Run Cipher", command=self.process_text_playground, bg="#6366f1", fg="white", font=("Helvetica", 9, "bold"), padx=10, pady=3, cursor="hand2")
        btn_run_text.pack(side="right")

        # Output frame
        frame_output = ttk.LabelFrame(self.tab_text, text=" Ciphertext Output / Restored Plaintext ", padding=6)
        frame_output.pack(fill="both", expand=True, pady=3)

        self.txt_output = tk.Text(frame_output, height=5, font=("Courier", 9), bg="#0f172a", fg="#4ade80", wrap="word")
        self.txt_output.pack(fill="both", expand=True)

        self.process_text_playground()

    def process_text_playground(self):
        plaintext = self.txt_input.get("1.0", tk.END).strip().encode("utf-8")
        key = self.txt_play_key.get().strip().encode("utf-8")
        if not key:
            key = b"default"

        S = rc4Encrypt.ksa(key)
        cipher_bytes = rc4Encrypt.prga(S, plaintext)

        fmt = self.fmt_var.get()
        if fmt == "Hex":
            out_str = cipher_bytes.hex(" ")
        else:
            out_str = base64.b64encode(cipher_bytes).decode("ascii")

        # Decrypt roundtrip check
        S_dec = rc4Decryptor.ksa(key)
        recovered = rc4Decryptor.prga(S_dec, cipher_bytes).decode("utf-8", errors="replace")

        result_display = f"Ciphertext ({fmt}):\n{out_str}\n\nRestored Plaintext via Inverse PRGA:\n{recovered}"
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", result_display)
        self.status_var.set(f"[+] Processed {len(plaintext)} bytes of text in playground.")

    # =========================================================================
    # TAB 3: S-BOX & VERIFICATION TESTS
    # =========================================================================
    def init_diag_tab(self):
        diag_top = ttk.Frame(self.tab_diag)
        diag_top.pack(fill="x", pady=(0, 6))

        btn_run_verify = tk.Button(diag_top, text="▶ Run 8-Stage Automated Test Suite", command=self.run_automated_tests, bg="#059669", fg="white", font=("Helvetica", 10, "bold"), padx=12, pady=6, cursor="hand2")
        btn_run_verify.pack(side="left")

        btn_show_sbox = ttk.Button(diag_top, text="Inspect KSA S-Box State", command=self.inspect_sbox)
        btn_show_sbox.pack(side="right")

        # Log Display
        log_frame = ttk.LabelFrame(self.tab_diag, text=" Verification Output & S-Box State Matrix ", padding=6)
        log_frame.pack(fill="both", expand=True)

        self.txt_diag_log = tk.Text(log_frame, font=("Courier", 9), bg="#0f172a", fg="#e2e8f0", insertbackground="white")
        self.txt_diag_log.pack(fill="both", expand=True, side="left")

        scroll_diag = ttk.Scrollbar(log_frame, orient="vertical", command=self.txt_diag_log.yview)
        scroll_diag.pack(side="right", fill="y")
        self.txt_diag_log.configure(yscrollcommand=scroll_diag.set)

        self.inspect_sbox()

    def inspect_sbox(self):
        key = self.key_var.get().strip().encode("utf-8")
        if not key:
            key = DEFAULT_KEY.encode()

        S = rc4Encrypt.ksa(key)
        lines = [
            f"--- RC4 Key Scheduling Algorithm (KSA) Permutation State ---",
            f"Key: {key.decode(errors='replace')}",
            f"Key Length: {len(key)} bytes",
            f"State Array S [256 bytes]:\n"
        ]

        for r in range(0, 256, 16):
            row_vals = " ".join(f"{S[r+c]:02x}" for c in range(16))
            lines.append(f"0x{r:02x}: {row_vals}")

        self.txt_diag_log.delete("1.0", tk.END)
        self.txt_diag_log.insert("1.0", "\n".join(lines))
        self.status_var.set("Displayed 256-byte S-box permutation matrix.")

    def run_automated_tests(self):
        import subprocess
        verify_script = os.path.join(script_dir, "verify.sh")
        if not os.path.isfile(verify_script):
            self.txt_diag_log.insert(tk.END, "\n[-] verify.sh not found.\n")
            return

        self.txt_diag_log.delete("1.0", tk.END)
        self.txt_diag_log.insert("1.0", "[*] Executing 8-stage automated test suite...\n\n")
        self.update_idletasks()

        try:
            res = subprocess.run(["bash", verify_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            import re
            clean_output = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', res.stdout)
            self.txt_diag_log.insert(tk.END, clean_output)
            self.status_var.set("Automated test suite completed.")
        except Exception as e:
            self.txt_diag_log.insert(tk.END, f"\n[-] Error running verify.sh: {e}\n")


if __name__ == "__main__":
    app = ModernRC4App()
    app.mainloop()
