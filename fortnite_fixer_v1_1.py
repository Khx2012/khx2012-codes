import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, colorchooser, filedialog
import threading
import os
import shutil
import psutil
import platform
import configparser

# ── CONFIG ────────────────────────────────────────────────────────────────
CONFIG_DIR = os.path.join(os.path.expandvars("%AppData%"), "FortniteCrashFixer")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.ini")

DEFAULTS = {
    "dark_mode": "false",
    "bg_color": "#f0f0f0",
    "fortnite_path": r"C:\Program Files\Epic Games\Fortnite",
    "auto_analyze": "false",
    "clear_shader_on_quick_fix": "true",
    "clear_launcher_on_quick_fix": "true",
}


class FortniteFixer_v1_2:
    def __init__(self, root):
        self.root = root
        self.is_running = False

        self.root.title("Fortnite Crash Fixer v1.1")
        self.root.geometry("800x640")

        self.cfg = self.load_config()
        self.build_ui()
        self.apply_theme()

        if self.get_bool("auto_analyze"):
            self.root.after(500, self.analyze)


    # ── CONFIG ─────────────────────────────
    def load_config(self):
        cfg = configparser.ConfigParser()

        try:
            if os.path.exists(CONFIG_FILE):
                cfg.read(CONFIG_FILE, encoding="utf-8")

            if "app" not in cfg:
                cfg["app"] = {k: str(v) for k, v in DEFAULTS.items()}

        except Exception:
            cfg["app"] = DEFAULTS.copy()

        os.makedirs(CONFIG_DIR, exist_ok=True)

        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                cfg.write(f)

        return cfg

    def save_config(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            self.cfg.write(f)

    def get(self, key):
        try:
            return self.cfg.get("app", key)
        except:
            return DEFAULTS.get(key, "")

    def get_bool(self, key):
        try:
            return self.cfg.getboolean("app", key)
        except:
            return DEFAULTS.get(key, "false").lower() == "true"

    def set(self, key, value):
        if isinstance(value, bool):
            value = "true" if value else "false"
        self.cfg.set("app", key, str(value))

    # ── UI ────────────────────────────────────────────────────────────────────
    def build_ui(self):
        bar = tk.Frame(self.root, bg="#2c2c2c", height=36)
        bar.pack(fill=tk.X, side=tk.TOP)
        bar.pack_propagate(False)

        tk.Label(bar, text="🎮 Fortnite Crash Fixer v1.2",
                 bg="#2c2c2c", fg="white",
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)

        tk.Button(bar, text="❌ Exit", command=self.root.quit,
                  bg="#2c2c2c", fg="white", relief="flat").pack(side=tk.RIGHT, padx=5)
        tk.Button(bar, text="📖 Help & FAQ", command=self.show_help,
                  bg="#2c2c2c", fg="white", relief="flat").pack(side=tk.RIGHT, padx=5)
        tk.Button(bar, text="🎨 Color", command=self.pick_color,
                  bg="#2c2c2c", fg="white", relief="flat").pack(side=tk.RIGHT, padx=5)

        self.dark_btn = tk.Button(bar, text="🌙 Dark Mode",
                                  command=self.toggle_dark_mode,
                                  bg="#2c2c2c", fg="white", relief="flat")
        self.dark_btn.pack(side=tk.RIGHT, padx=5)

        tk.Button(bar, text="⚙️ Settings", command=self.show_settings,
                  bg="#2c2c2c", fg="#FFD700", relief="flat",
                  font=("Arial", 9, "bold")).pack(side=tk.RIGHT, padx=8)

        ttk.Label(self.root, text="🎮 Fortnite Crash Fixer",
                  font=("Arial", 18, "bold")).pack(pady=15)

        self.status_label = ttk.Label(self.root, text="Ready",
                                     font=("Arial", 10), foreground="green")
        self.status_label.pack()

        btn = ttk.Frame(self.root)
        btn.pack(pady=15)

        ttk.Button(btn, text="🔍 Analyze System",
                   command=self.analyze).pack(fill=tk.X, pady=3, padx=10)
        ttk.Button(btn, text="⚡ Quick Fix (Recommended)",
                   command=self.quick_fix).pack(fill=tk.X, pady=3, padx=10)
        ttk.Button(btn, text="🔧 Clear Shader Cache",
                   command=self.clear_cache).pack(fill=tk.X, pady=3, padx=10)
        ttk.Button(btn, text="💾 Increase Virtual Memory",
                   command=self.increase_memory).pack(fill=tk.X, pady=3, padx=10)
        ttk.Button(btn, text="💻 System Info",
                   command=self.show_system_info).pack(fill=tk.X, pady=3, padx=10)

        ttk.Label(self.root, text="Output:",
                  font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10)

        self.output = scrolledtext.ScrolledText(self.root, height=10)
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Label(self.root,
                  text="Version 1.1  |  Not affiliated with Epic Games",
                  font=("Arial", 7), foreground="gray").pack(pady=3)

    # ── THEME ─────────────────────────────────────────────────────────────────
    def apply_theme(self):
        dark = self.get_bool("dark_mode")

        bg = "#1e1e1e" if dark else self.get("bg_color")
        fg = "white" if dark else "black"

        self.root.configure(bg=bg)

        if hasattr(self, "output"):
            self.output.configure(
                bg="#2d2d2d" if dark else "white",
                fg=fg
            )

    def toggle_dark_mode(self):
        self.set("dark_mode", not self.get_bool("dark_mode"))
        self.save_config()
        self.apply_theme()

    def pick_color(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.set("bg_color", c)
            self.save_config()
            self.apply_theme()

    # ── LOGGING ───────────────────────────────────────────────────────────────
    def log(self, msg):
        self.output.insert(tk.END, str(msg) + "\n")
        self.output.see(tk.END)

    def log_safe(self, msg):
        self.root.after(0, lambda: self.log(msg))

    def status_safe(self, msg, color="green"):
        self.root.after(0, lambda: self.status_label.config(text=msg, foreground=color))
    # ── ANALYZE ────────────────────────────────────────
    def analyze(self):
        if self.is_running:
            return

        self.is_running = True
        self.root.after(0, lambda: self.output.delete(1.0, tk.END))

        def run():
            try:
                self.log_safe("=" * 50)
                self.log_safe("FORTNITE SYSTEM ANALYSIS")
                self.log_safe("=" * 50)

                # OS
                os_name = f"{platform.system()} {platform.release()}"
                self.log_safe(f"✓ OS: {os_name}")

                # RAM
                vm = psutil.virtual_memory()
                total_ram = vm.total / (1024**3)
                avail_ram = vm.available / (1024**3)

                self.log_safe(f"✓ RAM: {total_ram:.1f} GB total ({avail_ram:.1f} GB available)")

                if avail_ram < 4:
                    self.log_safe("⚠️ RAM WARNING: Less than 4GB available — consider restarting PC first")

                # Disk
                disk = psutil.disk_usage(os.path.splitdrive(os.getcwd())[0] + "\\")
                free_disk = disk.free / (1024**3)

                self.log_safe(f"✓ Disk: {free_disk:.1f} GB free on C:")

                # Fortnite check
                self.log_safe("\nChecking Fortnite...")
                path = self.get("fortnite_path")

                if os.path.isdir(path):
                    self.log_safe(f"✓ Fortnite found at: {path}")
                else:
                    self.log_safe("❌ Fortnite NOT found")

                # Logs
                self.log_safe("\nChecking crash logs...")
                log_dir = os.path.expandvars(r"%LocalAppData%\FortniteGame\Saved\Logs")

                if os.path.isdir(log_dir):
                    logs = [x for x in os.listdir(log_dir) if x.lower().endswith(".log")]
                    if logs:
                        self.log_safe(f"⚠️ Found {len(logs)} crash logs")
                    else:
                        self.log_safe("✓ No crash logs found")
                else:
                    self.log_safe("⚠️ Log folder not found")

                self.log_safe("\n" + "=" * 50)
                self.log_safe("Analysis Complete!")
                self.log_safe("=" * 50)

                self.status_safe("Analysis completed successfully", "green")

            except Exception as e:
                self.log_safe(f"ERROR: {e}")
                self.status_safe("Error occurred", "red")

            finally:
                self.is_running = False

        threading.Thread(target=run, daemon=True).start()

    # ── QUICK FIX ────────────────────────────────────────
    def quick_fix(self):
        if self.is_running:
            return

        if not messagebox.askyesno("Confirm", "Apply Quick Fix?"):
            return

        self.is_running = True
        self.root.after(0, lambda: self.output.delete(1.0, tk.END))

        do_shader = self.get_bool("clear_shader_on_quick_fix")
        do_launcher = self.get_bool("clear_launcher_on_quick_fix")

        def run():
            try:
                self.log_safe("=== QUICK FIX ===")

                if do_shader:
                    cache = os.path.expandvars(r"%LocalAppData%\FortniteGame\Saved\ShaderCache")

                    if os.path.exists(cache):
                        try:
                           shutil.rmtree(cache)
                           self.log_safe("✓ Shader cache cleared")
                        except Exception as e:
                           self.log_safe(f"⚠️ Failed to clear shader cache: {e}")
                    else:
                       self.log_safe("✓ Shader cache not found (nothing to clear)")

                if do_launcher:
                    launcher = os.path.expandvars(r"%LocalAppData%\EpicGamesLauncher\Saved\webcache")

                    if os.path.exists(launcher):
                        try:
                            shutil.rmtree(launcher)
                            self.log_safe("✓ Launcher cache cleared")
                        except Exception as e:
                            self.log_safe(f"⚠️ Failed to clear launcher cache: {e}")
                    else:
                        self.log_safe("✓ Launcher cache not found (nothing to clear)")
               
                self.status_safe("Fix complete", "green")
                self.root.after(0, lambda: messagebox.showinfo("Done", "Quick Fix completed"))

            except Exception as e:
                self.log_safe(f"ERROR: {e}")
                self.status_safe("Error occurred", "red")

            finally:
                self.is_running = False

        threading.Thread(target=run, daemon=True).start()
    # ── CLEAR CACHE (FIXED: error logging) ────────────────────────────────────
    def clear_cache(self):
        if not messagebox.askyesno("Confirm", "Clear shader cache?"):
            return

        cache = os.path.expandvars(r"%LocalAppData%\FortniteGame\Saved\ShaderCache")

        def run():
            try:
                if os.path.isdir(cache):
                    shutil.rmtree(cache)
                    os.makedirs(cache, exist_ok=True)
                    self.log_safe("Cache cleared")
                else:
                    self.log_safe("Cache folder not found")
            except Exception as e:
                self.log_safe(f"Error clearing cache: {e}")

        threading.Thread(target=run, daemon=True).start()

    # ── SYSTEM INFO ───────────────────────────────────────────────────────────
    def show_system_info(self):
        self.output.delete(1.0, tk.END)

        vm = psutil.virtual_memory()
        disk = psutil.disk_usage(os.path.splitdrive(os.getcwd())[0] + "\\")

        self.log(f"OS: {platform.system()} {platform.release()}")
        self.log(f"RAM Used: {vm.used//(1024**3)}GB")
        self.log(f"RAM Free: {vm.available//(1024**3)}GB")
        self.log(f"Disk Free: {disk.free//(1024**3)}GB")
        self.log(f"CPU: {psutil.cpu_percent(interval=0.3)}%")

    # ── MEMORY GUIDE ─────────────────────────────
    def increase_memory(self):
        self.root.after(0, lambda: self.output.delete(1.0, tk.END))
        steps = [
            "Right click This PC → Properties",
            "Advanced system settings",
            "Performance → Settings",
            "Virtual Memory → Change",
            "Set to 16384MB",
            "Restart PC"
        ]
        for s in steps:
            self.log_safe(s)

    
   # ── HELP ─────────────────────────────────────
    def show_help(self):
        win = tk.Toplevel(self.root)
        win.title("Help & FAQ")
        win.geometry("520x500")

        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Arial", 9))
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        txt.insert(tk.END, """
FORTNITE CRASH FIXER v1.2 — HELP & FAQ

BUTTONS
=======
🔍 Analyze System     — Scans RAM, disk, Fortnite path and crash logs
⚡ Quick Fix          — Clears shader and launcher cache automatically
🔧 Clear Shader Cache — Manually clears only the shader cache
💾 Increase Memory    — Step-by-step guide to increase virtual memory
💻 System Info        — Shows full PC specs

FAQ
===
Q: Will this delete my skins or progress?
A: No. Only cache files are cleared. Account data is never touched.

Q: Why does antivirus flag this?
A: PyInstaller apps get flagged by default. Source code is on GitHub.

Q: Fortnite is installed in a custom folder?
A: Open ⚙️ Settings and set the path with the Browse button.

Q: Still crashing after fixes?
A: Try updating your GPU drivers and verifying files in Epic Launcher.
   Visit epicgames.com/help for further support.

COMMON CRASH CAUSES
===================
1. Corrupted shader cache   → Clear Shader Cache
2. Low available RAM        → Increase Virtual Memory
3. Outdated GPU drivers     → Update manually (NVIDIA/AMD)
4. Low disk space           → Free up 50+ GB on C:
5. Corrupted game files     → Verify files in Epic Launcher

TIPS
====
✓ Close Fortnite before applying fixes
✓ Restart your PC after fixes
✓ Keep Windows and GPU drivers updated
""")

    txt.config(state=tk.DISABLED)

    btn = ttk.Frame(win)
    btn.pack(pady=5)

    ttk.Button(btn, text="Privacy", command=self.show_privacy).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn, text="Disclaimer", command=self.show_disclaimer).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn, text="Close", command=win.destroy).pack(side=tk.LEFT, padx=5)
  
    # ── DISCLAIMER ────────────────────────────────────────────────────────────
    def show_disclaimer(self):
        win = tk.Toplevel(self.root)
        win.title("Disclaimer")
        win.geometry("450x260")

        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)

        txt.insert(tk.END,
"""
NOT AFFILIATED WITH EPIC GAMES

Use at your own risk.
Only deletes cache files.
No account or game file modification.
""")
        txt.config(state=tk.DISABLED)
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=5)

    # ── PRIVACY ───────────────────────────────────────────────────────────────
    def show_privacy(self):
        win = tk.Toplevel(self.root)
        win.title("Privacy Policy")
        win.geometry("450x260")

        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)

        txt.insert(tk.END,
"""
PRIVACY POLICY

- No data collection
- No internet access
- Settings stored locally in AppData
""")
        txt.config(state=tk.DISABLED)
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=5)

    
       # ── SETTINGS ──────────────────────────────────────────────────────────────
    def show_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("420x350")

        auto = tk.BooleanVar(value=self.get_bool("auto_analyze"))
        dark = tk.BooleanVar(value=self.get_bool("dark_mode"))
        shader = tk.BooleanVar(value=self.get_bool("clear_shader_on_quick_fix"))
        launcher = tk.BooleanVar(value=self.get_bool("clear_launcher_on_quick_fix"))
        path = tk.StringVar(value=self.get("fortnite_path"))

        # ── TITLE ──
        ttk.Label(win, text="⚙️ Settings",
                  font=("Arial", 14, "bold")).pack(pady=10)

        # ── BASIC OPTIONS ──
        ttk.Checkbutton(win, text="Auto-analyze system on startup",
                        variable=auto).pack(anchor="w", padx=20)

        ttk.Checkbutton(win, text="Dark mode",
                        variable=dark).pack(anchor="w", padx=20, pady=(0,10))

        # ── QUICK FIX OPTIONS ──
        ttk.Label(win, text="Quick Fix options:",
                  font=("Arial", 10, "bold")).pack(anchor="w", padx=20)

        ttk.Checkbutton(win, text="Clear shader cache",
                        variable=shader).pack(anchor="w", padx=30)

        ttk.Checkbutton(win, text="Clear launcher cache",
                        variable=launcher).pack(anchor="w", padx=30, pady=(0,10))

        # ── PATH SECTION ──
        ttk.Label(win, text="Fortnite install path:",
                  font=("Arial", 10, "bold")).pack(anchor="w", padx=20)

        path_frame = ttk.Frame(win)
        path_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Entry(path_frame, textvariable=path).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5)
        )

        def browse():
            f = filedialog.askdirectory()
            if f:
                path.set(f)

        ttk.Button(path_frame, text="Browse", command=browse).pack(side=tk.LEFT)

        # ── SAVE FUNCTION ──
        def save():
            self.set("auto_analyze", auto.get())
            self.set("dark_mode", dark.get())
            self.set("clear_shader_on_quick_fix", shader.get())
            self.set("clear_launcher_on_quick_fix", launcher.get())
            self.set("fortnite_path", path.get())
            self.save_config()
            self.apply_theme()
            win.destroy()

        # ── BUTTONS ──
        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="💾 Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=win.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔒 Privacy Policy", command=self.show_privacy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⚠️ Disclaimer", command=self.show_disclaimer).pack(side=tk.LEFT, padx=5)

# ── RUN ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FortniteFixer_v1_2(root)
    root.mainloop()