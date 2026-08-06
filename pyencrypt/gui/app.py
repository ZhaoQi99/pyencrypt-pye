import os
import queue
import shutil
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from pyencrypt.decrypt import decrypt_file
from pyencrypt.encrypt import can_encrypt, encrypt_file, encrypt_key, generate_so_file
from pyencrypt.generate import generate_aes_key
from pyencrypt.utils import check_key, format_size


def _format_eta(ratio: float, eta: float) -> str:
    percent = int(ratio * 100)
    eta = max(eta, 0.0)
    h, rem = divmod(int(eta), 3600)
    m, s = divmod(rem, 60)
    return f"{percent:>3d}%  {h:02d}:{m:02d}:{s:02d}"


def _do_encrypt(path: Path, key: str, without_loader: bool, on_log, on_progress):
    if path.is_file():
        new_path = Path(os.getcwd()) / path.with_suffix(".pye").name
        on_log(f"Encrypting file: {path.name}")
        encrypt_file(path, key, False, new_path)
        on_progress(1.0, 0.0)
        summary = f"Encrypted 1 file -> {new_path}"
    elif path.is_dir():
        work_dir = Path(os.getcwd()) / "encrypted" / path.name
        if work_dir.exists():
            shutil.rmtree(work_dir)
        shutil.copytree(path, work_dir)
        files = set(work_dir.glob("**/*.py"))
        total = len(files)
        count = 0
        total_size = 0
        start = time.perf_counter()
        for idx, file in enumerate(files, 1):
            if can_encrypt(file):
                total_size += file.stat().st_size
                encrypt_file(file, key, True, file.with_suffix(".pye"))
                count += 1
            elapsed = time.perf_counter() - start
            eta = elapsed / idx * (total - idx) if idx else 0.0
            on_progress(idx / (total or 1), eta)
        elapsed = time.perf_counter() - start
        summary = (
            f"🔐 Encrypted {count} file(s) ({format_size(total_size)}) "
            f"in {elapsed:.2f}s"
        )
    else:
        raise ValueError(f"{path} is not a valid path")

    if not without_loader:
        on_log("Generating loader...")
        cipher_key, d, n = encrypt_key(key.encode())
        loader = generate_so_file(cipher_key, d, n, license=False)
        summary += f"\nloader: {loader.name}"

    return summary


def _do_decrypt(path: Path, key: str, on_log, on_progress):
    if path.is_file():
        new_path = path.with_suffix(".py")
        on_log(f"Decrypting file: {path.name}")
        decrypt_file(path, key, False, new_path)
        on_progress(1.0, 0.0)
        return f"Decrypted 1 file -> {new_path}"
    elif path.is_dir():
        files = list(path.glob("**/*.pye"))
        total = len(files)
        total_size = 0
        start = time.perf_counter()
        on_log(f"{total} file(s) can be decrypted")
        for idx, file in enumerate(files, 1):
            total_size += file.stat().st_size
            decrypt_file(file, key, False, file.with_suffix(".py"))
            elapsed = time.perf_counter() - start
            eta = elapsed / idx * (total - idx) if idx else 0.0
            on_progress(idx / (total or 1), eta)
        elapsed = time.perf_counter() - start
        return (
            f"Decrypted {total} file(s) ({format_size(total_size)}) "
            f"in {elapsed:.2f}s"
        )
    else:
        raise ValueError(f"{path} is not a valid path")


class App:
    def __init__(self, root: "tk.Tk"):
        self.root = root
        root.title("pyencrypt")
        root.geometry("640x620")
        root.minsize(560, 520)

        self._queue: "queue.Queue" = queue.Queue()

        pad = {"padx": 12, "pady": 6}
        frm = ttk.Frame(root, padding=16)
        frm.pack(fill="both", expand=True)

        # action: encrypt / decrypt
        self.action_var = tk.StringVar(value="encrypt")
        action_row = ttk.Frame(frm)
        action_row.pack(fill="x", **pad)
        ttk.Label(action_row, text="Action", width=16).pack(side="left")
        ttk.Radiobutton(
            action_row,
            text="Encrypt",
            value="encrypt",
            variable=self.action_var,
            command=self._on_action_change,
        ).pack(side="left")
        ttk.Radiobutton(
            action_row,
            text="Decrypt",
            value="decrypt",
            variable=self.action_var,
            command=self._on_action_change,
        ).pack(side="left", padx=(12, 0))

        # target type: file / folder
        self.target_var = tk.StringVar(value="file")
        target_row = ttk.Frame(frm)
        target_row.pack(fill="x", **pad)
        ttk.Label(target_row, text="Target", width=16).pack(side="left")
        ttk.Radiobutton(
            target_row, text="File", value="file", variable=self.target_var
        ).pack(side="left")
        ttk.Radiobutton(
            target_row, text="Folder", value="folder", variable=self.target_var
        ).pack(side="left", padx=(12, 0))

        # path
        path_row = ttk.Frame(frm)
        path_row.pack(fill="x", **pad)
        ttk.Label(path_row, text="Path", width=16).pack(side="left")
        self.path_var = tk.StringVar()
        ttk.Entry(path_row, textvariable=self.path_var).pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        ttk.Button(path_row, text="Select...", command=self._pick_path).pack(
            side="left"
        )

        key_row = ttk.Frame(frm)
        key_row.pack(fill="x", **pad)
        ttk.Label(key_row, text="Key", width=16).pack(side="left")
        self.key_var = tk.StringVar()
        ttk.Entry(key_row, textvariable=self.key_var).pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        self.gen_btn = ttk.Button(key_row, text="Generate", command=self._gen_key)
        self.gen_btn.pack(side="left")

        # options
        self.without_loader = tk.BooleanVar(value=False)
        self.loader_chk = ttk.Checkbutton(
            frm, text="Do not generate loader", variable=self.without_loader
        )
        self.loader_chk.pack(anchor="w", **pad)

        # start button
        self.start_btn = ttk.Button(frm, text="Encrypt", command=self._start)
        self.start_btn.pack(fill="x", **pad)

        # progress bar
        self.progress_row = ttk.Frame(frm)
        self.progress = ttk.Progressbar(
            self.progress_row, mode="determinate", maximum=1.0
        )
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(
            self.progress_row, textvariable=self.status_var, width=14, anchor="e"
        )
        self.status_label.pack(side="left")
        self._progress_pad = pad

        # log
        ttk.Label(frm, text="Log").pack(anchor="w", padx=12)
        log_frame = ttk.Frame(frm)
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        self.log_text = tk.Text(log_frame, height=10, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.root.after(80, self._drain_queue)

    def _on_action_change(self):
        is_encrypt = self.action_var.get() == "encrypt"
        self.start_btn.configure(text="Encrypt" if is_encrypt else "Decrypt")
        self.loader_chk.configure(state="normal" if is_encrypt else "disabled")

    def _log(self, msg: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _drain_queue(self):
        try:
            while True:
                kind, value = self._queue.get_nowait()
                if kind == "log":
                    self._log(value)
                elif kind == "progress":
                    ratio, eta = value
                    self.progress["value"] = ratio
                    self.status_var.set(_format_eta(ratio, eta))
                elif kind == "done":
                    self.start_btn.configure(state="normal")
        except queue.Empty:
            pass
        self.root.after(80, self._drain_queue)

    def _pick_path(self):
        if self.target_var.get() == "file":
            path = filedialog.askopenfilename(title="Select file")
        else:
            path = filedialog.askdirectory(title="Select folder")
        if path:
            self.path_var.set(path)

    def _gen_key(self):
        self.key_var.set(generate_aes_key().decode())

    def _start(self):
        path_str = self.path_var.get().strip()
        key = self.key_var.get().strip()
        if not path_str:
            self._log("⚠️  Please select a file or folder first")
            return
        if not key:
            self._log("⚠️  Please input or generate a key first")
            return
        if not check_key(key):
            self._log("⚠️  Invalid encryption key")
            return
        self.start_btn.configure(state="disabled")
        self.progress["value"] = 0
        self.status_var.set("")
        self.progress_row.pack(fill="x", after=self.start_btn, **self._progress_pad)
        threading.Thread(
            target=self._worker,
            args=(
                self.action_var.get(),
                Path(path_str),
                key,
                self.without_loader.get(),
            ),
            daemon=True,
        ).start()

    def _worker(self, action: str, path: Path, key: str, no_loader: bool):
        def on_log(msg):
            self._queue.put(("log", msg))

        def on_progress(ratio, eta=0.0):
            self._queue.put(("progress", (ratio, eta)))

        on_progress(0.0, 0.0)
        try:
            if action == "encrypt":
                on_log("🔐 Encrypting...")
                summary = _do_encrypt(path, key, no_loader, on_log, on_progress)
            else:
                on_log("🔓 Decrypting...")
                summary = _do_decrypt(path, key, on_log, on_progress)
            on_log(summary)
            on_log("✅ Done")
        except Exception as exc:  # noqa: BLE001
            on_log("❌ Error: " + str(exc))
        finally:
            self._queue.put(("done", None))


def run():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    run()
