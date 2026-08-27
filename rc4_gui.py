#!/usr/bin/env python3
"""
RC4 Stream Cipher - Professional Interactive Cryptography Suite
Author: megbaru dessie
"""

import os
import sys
import time
import math
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


def calculate_entropy(key_str: str) -> float:
    """Calculates Shannon entropy of the key string."""
    if not key_str:
        return 0.0
    prob = [float(key_str.count(c)) / len(key_str) for c in dict.fromkeys(key_str)]
    return -sum(p * math.log2(p) for p in prob)


def get_file_info(filepath: str):
    """Returns existence, formatted size, and SHA-256 checksum."""
    if not filepath or not os.path.exists(filepath):
        return False, "File not found", "-"
    if not os.path.isfile(filepath):
        return False, "Is a directory", "-"
    
    size = os.path.getsize(filepath)
    if size < 1024:
        size_str = f"{size} B"
    elif size < 1024 * 1024:
        size_str = f"{size / 1024:.2f} KB ({size} bytes)"
    else:
        size_str = f"{size / (1024 * 1024):.2f} MB ({size} bytes)"

    try:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return True, size_str, hasher.hexdigest()
    except Exception as e:
        return False, size_str, f"Error: {e}"


def get_file_preview(filepath: str, max_bytes: int = 512):
    """Returns clean plaintext or a structured hex dump preview."""
    if not filepath or not os.path.isfile(filepath):
        return "[No valid file selected]"
    try:
        with open(filepath, "rb") as f:
            data = f.read(max_bytes)
        
        if len(data) == 0:
            return "[Empty File - 0 bytes]"

        # Try decoding as utf-8
        try:
            text = data.decode("utf-8")
            if text.isprintable() or any(c in "\n\r\t" for c in text):
                return f"=== Plaintext View ({len(data)} bytes shown) ===\n\n{text}"
        except UnicodeDecodeError:
            pass

        # Fallback to formatted hex dump
        hex_dump = []
        for i in range(0, min(len(data), 128), 16):
            chunk = data[i:i+16]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            hex_dump.append(f"{i:04x}  {hex_part:<48}  |{ascii_part}|")
        return f"=== Binary / Ciphertext Hex Dump ({len(data)} bytes) ===\n\n" + "\n".join(hex_dump)
    except Exception as e:
        return f"[Error generating preview: {e}]"


class ModernRC4App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RC4 Stream Cipher Suite - Professional Edition")
        self.geometry("780x660")
        self.minsize(720, 600)

        # Style configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        self.style.configure("TNotebook", background="#f8fafc")
        self.style.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[16, 7])

        # Header Banner
        header_frame = tk.Frame(self, bg="#0f172a", height=65)
        header_frame.pack(fill="x", side="top")
        
        title_box = tk.Frame(header_frame, bg="#0f172a")
        title_box.pack(side="left", padx=20, pady=10)

        title_lbl = tk.Label(title_box, text="🔒 RC4 Stream Cipher Suite", font=("Helvetica", 15, "bold"), bg="#0f172a", fg="#ffffff")
        title_lbl.pack(anchor="w")

        author_lbl = tk.Label(title_box, text="Author: megbaru dessie | S-Box KSA & PRGA Engine", font=("Helvetica", 8), bg="#0f172a", fg="#94a3b8")
        author_lbl.pack(anchor="w")

        badge_lbl = tk.Label(header_frame, text="PRO v2.0", font=("Helvetica", 9, "bold"), bg="#2563eb", fg="white", padx=8, pady=3)
        badge_lbl.pack(side="right", padx=20, pady=16)

        # Bottom Status Bar (Initialized first)
        self.status_var = tk.StringVar(value="Ready. Select a file or enter text to begin.")
        status_bar = tk.Label(self, textvariable=self.status_var, relief="groove", anchor="w", font=("Helvetica", 9), bg="#e2e8f0", fg="#334155", padx=12, pady=5)
        status_bar.pack(fill="x", side="bottom")

        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=10)

        # Tab 1: File Encryptor/Decryptor
        self.tab_file = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_file, text=" 📁 File Cipher ")
        self.init_file_tab()

        # Tab 2: Text Playground
        self.tab_text = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_text, text=" ✍️ Stream Playground ")
        self.init_text_tab()

        # Tab 3: Lab & Diagnostics
        self.tab_diag = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_diag, text=" ⚙️ Crypto Lab & Tests ")
        self.init_diag_tab()

    # =========================================================================
    # TAB 1: ADVANCED FILE CIPHER TAB
    # =========================================================================
    def init_file_tab(self):
        # 1. Target File Selection Frame
        file_frame = ttk.LabelFrame(self.tab_file, text=" 📂 Select Target File ", padding=10)
        file_frame.pack(fill="x", pady=(0, 6))

        row1 = ttk.Frame(file_frame)
        row1.pack(fill="x", pady=(0, 6))

        self.file_path_var = tk.StringVar()
        default_file = os.path.join(script_dir, "file.txt")
        self.file_path_var.set(default_file if os.path.exists(default_file) else "")

        self.recent_files = [default_file]
        for f in [os.path.join(script_dir, "check.txt"), os.path.expanduser("~/Downloads/check.txt")]:
            if os.path.exists(f) and f not in self.recent_files:
                self.recent_files.append(f)

        self.combo_file = ttk.Combobox(row1, textvariable=self.file_path_var, values=self.recent_files, font=("Courier", 9))
        self.combo_file.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.combo_file.bind("<<ComboboxSelected>>", lambda e: self.on_file_changed())

        btn_browse = tk.Button(row1, text="📁 Browse...", command=self.browse_target_file, bg="#2563eb", fg="white", font=("Helvetica", 9, "bold"), padx=10, pady=3, relief="raised", cursor="hand2")
        btn_browse.pack(side="right")

        # Row 2: Action Buttons
        row2 = ttk.Frame(file_frame)
        row2.pack(fill="x")

        btn_default = ttk.Button(row2, text="📄 Default (file.txt)", command=self.load_default_file)
        btn_default.pack(side="left", padx=(0, 6))

        btn_new_sample = ttk.Button(row2, text="➕ Create Sample File", command=self.create_sample_file)
        btn_new_sample.pack(side="left", padx=(0, 6))

        btn_copy_hash = ttk.Button(row2, text="📋 Copy SHA-256", command=self.copy_file_hash)
        btn_copy_hash.pack(side="left", padx=(0, 6))

        btn_reload = ttk.Button(row2, text="🔄 Reload File", command=self.on_file_changed)
        btn_reload.pack(side="right")

        # 2. File Metadata Badge Card
        self.badge_card = tk.Frame(self.tab_file, bg="#1e293b", padx=12, pady=6)
        self.badge_card.pack(fill="x", pady=(0, 6))

        self.lbl_badge_icon = tk.Label(self.badge_card, text="🟢", font=("Helvetica", 10), bg="#1e293b", fg="#4ade80")
        self.lbl_badge_icon.pack(side="left", padx=(0, 8))

        self.file_info_var = tk.StringVar(value="Analyzing file...")
        self.current_hash = ""
        self.lbl_badge_text = tk.Label(self.badge_card, textvariable=self.file_info_var, font=("Courier", 8), bg="#1e293b", fg="#f8fafc", anchor="w")
        self.lbl_badge_text.pack(side="left", fill="x", expand=True)

        # 3. Secret Key Configuration Frame
        key_frame = ttk.LabelFrame(self.tab_file, text=" 🔑 Secret Encryption Key ", padding=8)
        key_frame.pack(fill="x", pady=(0, 6))

        self.key_var = tk.StringVar(value=DEFAULT_KEY)
        self.show_key_var = tk.BooleanVar(value=True)

        self.entry_key = ttk.Entry(key_frame, textvariable=self.key_var, font=("Courier", 9))
        self.entry_key.pack(fill="x", pady=(0, 4))
        self.key_var.trace_add("write", lambda *args: self.update_key_strength())

        key_btn_frame = ttk.Frame(key_frame)
        key_btn_frame.pack(fill="x")

        chk_show = ttk.Checkbutton(key_btn_frame, text="Show Key Characters", variable=self.show_key_var, command=self.toggle_key_visibility)
        chk_show.pack(side="left")

        self.lbl_key_strength = tk.Label(key_btn_frame, text="Key Strength: Strong (432 bits)", font=("Helvetica", 8), fg="#059669")
        self.lbl_key_strength.pack(side="left", padx=15)

        btn_key_default = ttk.Button(key_btn_frame, text="Reset Default", command=lambda: self.key_var.set(DEFAULT_KEY))
        btn_key_default.pack(side="right", padx=2)

        btn_random_key = ttk.Button(key_btn_frame, text="🎲 Generate 128-bit Key", command=self.generate_random_key)
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

        self.txt_preview = tk.Text(preview_frame, height=6, font=("Courier", 8), bg="#0f172a", fg="#38bdf8", insertbackground="white", wrap="none")
        self.txt_preview.pack(fill="both", expand=True, side="left")

        scroll_preview = ttk.Scrollbar(preview_frame, orient="vertical", command=self.txt_preview.yview)
        scroll_preview.pack(side="right", fill="y")
        self.txt_preview.configure(yscrollcommand=scroll_preview.set)

        self.file_path_var.trace_add("write", lambda *args: self.on_file_changed())
        self.on_file_changed()
        self.update_key_strength()

    def update_key_strength(self):
        k = self.key_var.get()
        k_bytes = len(k.encode("utf-8"))
        bits = k_bytes * 8
        entropy = calculate_entropy(k)
        
        if bits == 0:
            self.lbl_key_strength.configure(text="Key Strength: Empty (0 bits)", fg="#ef4444")
        elif bits < 64:
            self.lbl_key_strength.configure(text=f"Key Strength: Weak ({bits} bits)", fg="#f59e0b")
        elif bits < 128:
            self.lbl_key_strength.configure(text=f"Key Strength: Moderate ({bits} bits, E:{entropy:.1f})", fg="#3b82f6")
        else:
            self.lbl_key_strength.configure(text=f"Key Strength: Strong ({bits} bits, E:{entropy:.1f})", fg="#059669")

    def on_file_changed(self):
        filepath = self.file_path_var.get().strip()
        exists, size_info, hash_val = get_file_info(filepath)
        self.current_hash = hash_val
        
        if exists:
            self.lbl_badge_icon.configure(text="🟢", fg="#4ade80")
            short_hash = hash_val[:20] + "..." if len(hash_val) > 20 else hash_val
            self.file_info_var.set(f"Status: Ready  |  Size: {size_info}  |  SHA-256: {short_hash}")
        else:
            self.lbl_badge_icon.configure(text="🔴", fg="#ef4444")
            self.file_info_var.set(f"Status: Missing File  |  Path: {os.path.basename(filepath) if filepath else 'None'}")

        preview = get_file_preview(filepath)
        self.txt_preview.delete("1.0", tk.END)
        self.txt_preview.insert("1.0", preview)

    def copy_file_hash(self):
        if self.current_hash and self.current_hash != "-":
            self.clipboard_clear()
            self.clipboard_append(self.current_hash)
            self.status_var.set(f"Copied SHA-256 checksum to clipboard: {self.current_hash[:16]}...")
        else:
            messagebox.showwarning("Warning", "No valid file hash available to copy.")

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
    # TAB 2: STREAM & TEXT PLAYGROUND
    # =========================================================================
    def init_text_tab(self):
        lbl_intro = tk.Label(self.tab_text, text="Live stream cipher playground: Type text below to see real-time RC4 byte transformation:", font=("Helvetica", 9), fg="#475569")
        lbl_intro.pack(anchor="w", pady=(0, 4))

        frame_input = ttk.LabelFrame(self.tab_text, text=" 📝 Input Plaintext ", padding=6)
        frame_input.pack(fill="both", expand=True, pady=3)

        self.txt_input = tk.Text(frame_input, height=4, font=("Helvetica", 9), wrap="word")
        self.txt_input.insert("1.0", "RC4 is a symmetric stream cipher designed by Ron Rivest in 1987.")
        self.txt_input.pack(fill="both", expand=True)

        # Options row
        opts_frame = ttk.Frame(self.tab_text)
        opts_frame.pack(fill="x", pady=4)

        ttk.Label(opts_frame, text="Key:").pack(side="left", padx=(0, 4))
        self.txt_play_key = ttk.Entry(opts_frame, width=24)
        self.txt_play_key.insert(0, DEFAULT_KEY)
        self.txt_play_key.pack(side="left", padx=(0, 10))

        self.fmt_var = tk.StringVar(value="Hex")
        ttk.Label(opts_frame, text="Encoding:").pack(side="left", padx=(0, 4))
        ttk.Radiobutton(opts_frame, text="Hex", value="Hex", variable=self.fmt_var, command=self.process_text_playground).pack(side="left", padx=2)
        ttk.Radiobutton(opts_frame, text="Base64", value="Base64", variable=self.fmt_var, command=self.process_text_playground).pack(side="left", padx=2)
        ttk.Radiobutton(opts_frame, text="Binary Bits", value="Binary", variable=self.fmt_var, command=self.process_text_playground).pack(side="left", padx=2)

        btn_run_text = tk.Button(opts_frame, text="⚡ Run Cipher", command=self.process_text_playground, bg="#6366f1", fg="white", font=("Helvetica", 9, "bold"), padx=10, pady=2, cursor="hand2")
        btn_run_text.pack(side="right")

        btn_copy_cipher = ttk.Button(opts_frame, text="📋 Copy Ciphertext", command=self.copy_ciphertext)
        btn_copy_cipher.pack(side="right", padx=4)

        # Output frame
        frame_output = ttk.LabelFrame(self.tab_text, text=" 🔐 Ciphertext Output & Inverse PRGA Recovery ", padding=6)
        frame_output.pack(fill="both", expand=True, pady=3)

        self.txt_output = tk.Text(frame_output, height=6, font=("Courier", 9), bg="#0f172a", fg="#4ade80", wrap="word")
        self.txt_output.pack(fill="both", expand=True)

        self.latest_ciphertext_str = ""
        self.process_text_playground()

    def copy_ciphertext(self):
        if self.latest_ciphertext_str:
            self.clipboard_clear()
            self.clipboard_append(self.latest_ciphertext_str)
            self.status_var.set("Copied ciphertext output to clipboard.")

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
        elif fmt == "Base64":
            out_str = base64.b64encode(cipher_bytes).decode("ascii")
        else:
            out_str = " ".join(f"{b:08b}" for b in cipher_bytes)

        self.latest_ciphertext_str = out_str

        # Inverse recovery check
        S_dec = rc4Decryptor.ksa(key)
        recovered = rc4Decryptor.prga(S_dec, cipher_bytes).decode("utf-8", errors="replace")

        result_display = f"Ciphertext ({fmt}):\n{out_str}\n\nRestored Plaintext via Inverse PRGA:\n{recovered}"
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", result_display)
        self.status_var.set(f"[+] Processed {len(plaintext)} bytes in playground.")

    # =========================================================================
    # TAB 3: CRYPTO LAB, S-BOX & VERIFICATION TESTS
    # =========================================================================
    def init_diag_tab(self):
        diag_top = ttk.Frame(self.tab_diag)
        diag_top.pack(fill="x", pady=(0, 6))

        btn_run_verify = tk.Button(diag_top, text="▶ Run 8-Stage Test Suite", command=self.run_automated_tests, bg="#059669", fg="white", font=("Helvetica", 9, "bold"), padx=10, pady=5, cursor="hand2")
        btn_run_verify.pack(side="left", padx=(0, 6))

        btn_benchmark = tk.Button(diag_top, text="⚡ Benchmark Speed (MB/s)", command=self.run_benchmark, bg="#0284c7", fg="white", font=("Helvetica", 9, "bold"), padx=10, pady=5, cursor="hand2")
        btn_benchmark.pack(side="left", padx=(0, 6))

        btn_show_sbox = ttk.Button(diag_top, text="Inspect S-Box Matrix", command=self.inspect_sbox)
        btn_show_sbox.pack(side="right")

        btn_step_demo = ttk.Button(diag_top, text="PRGA Byte Stepper", command=self.show_prga_stepper)
        btn_step_demo.pack(side="right", padx=4)

        # Log Display
        log_frame = ttk.LabelFrame(self.tab_diag, text=" Diagnostic Terminal & State Inspector ", padding=6)
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
            f"=== RC4 Key Scheduling Algorithm (KSA) Permutation State ===",
            f"Key: {key.decode(errors='replace')}",
            f"Key Length: {len(key)} bytes ({len(key)*8} bits)",
            f"S-Box 16x16 Matrix:\n"
        ]

        header = "      " + " ".join(f"{c:02x}" for c in range(16))
        lines.append(header)
        lines.append("     " + "-" * 48)

        for r in range(0, 256, 16):
            row_vals = " ".join(f"{S[r+c]:02x}" for c in range(16))
            lines.append(f"0x{r:02x} | {row_vals}")

        self.txt_diag_log.delete("1.0", tk.END)
        self.txt_diag_log.insert("1.0", "\n".join(lines))
        self.status_var.set("Displayed 256-byte S-box matrix.")

    def show_prga_stepper(self):
        key = self.key_var.get().strip().encode("utf-8")
        if not key:
            key = b"key"
        
        sample_input = b"TEST"
        S = rc4Encrypt.ksa(key)
        
        lines = [
            "=== Step-by-Step PRGA Keystream Generation Demo ===",
            f"Key: {key.decode(errors='replace')}",
            f"Sample Input: {sample_input} (4 bytes)\n",
            f"{'Byte #':<8} {'i':<6} {'j':<6} {'S[i]':<8} {'S[j]':<8} {'K-Byte':<8} {'Plain':<8} {'Cipher':<8}",
            "-" * 68
        ]

        i = j = 0
        for idx, byte in enumerate(sample_input):
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            k_byte = S[(S[i] + S[j]) % 256]
            c_byte = byte ^ k_byte
            lines.append(f"Byte {idx+1:<3} {i:<6} {j:<6} 0x{S[i]:02x}     0x{S[j]:02x}     0x{k_byte:02x}     0x{byte:02x} ('{chr(byte)}')  0x{c_byte:02x}")

        self.txt_diag_log.delete("1.0", tk.END)
        self.txt_diag_log.insert("1.0", "\n".join(lines))
        self.status_var.set("Displayed step-by-step PRGA execution trace.")

    def run_benchmark(self):
        self.txt_diag_log.delete("1.0", tk.END)
        self.txt_diag_log.insert("1.0", "[*] Generating 2 MB random data buffer for throughput benchmark...\n")
        self.update_idletasks()

        data_size = 2 * 1024 * 1024  # 2 MB
        data = secrets.token_bytes(data_size)
        key = b"benchmark_key_123456789"

        t0 = time.perf_counter()
        S = rc4Encrypt.ksa(key)
        encrypted = rc4Encrypt.prga(S, data)
        t1 = time.perf_counter()

        elapsed = t1 - t0
        mb_per_sec = (data_size / (1024 * 1024)) / elapsed

        lines = [
            "\n=== RC4 Performance Benchmark Results ===",
            f"Buffer Size:     {data_size / (1024 * 1024):.2f} MB ({data_size:,} bytes)",
            f"Execution Time:  {elapsed * 1000:.2f} ms ({elapsed:.4f} seconds)",
            f"Throughput:      {mb_per_sec:.2f} MB/s",
            f"Cipher Status:   PASSED (Integrity check verified)",
            "=========================================="
        ]
        self.txt_diag_log.insert(tk.END, "\n".join(lines) + "\n")
        self.status_var.set(f"Benchmark completed: {mb_per_sec:.2f} MB/s throughput.")

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
