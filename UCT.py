import os
import sys
import time
import logging
import ctypes
import shutil
import subprocess
import threading
import webbrowser
from queue import Queue, Empty
from pathlib import Path

import psutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText


class USBCheckerApp:
    """USB Checker Tool - Analyze, repair, benchmark, and backup USB drives."""
    
    # Constants
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 500
    LOG_FILE = "usb_checker.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    BENCHMARK_SIZE = 100 * 1024 * 1024  # 100 MB
    CHUNK_SIZE = 1024 * 1024  # 1 MB
    
    def __init__(self, root):
        self.root = root
        self.root.title("USB Checker (UCT)")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#2e2e2e")
        self.center_window(self.root)
        
        # State variables
        self.selected_drive = tk.StringVar()
        self.process_queue = Queue()
        self.is_running = False
        self.drive_mapping = {}  # Maps display text to drive letter
        
        # Setup
        self.setup_logging()
        self.setup_styles()
        self.create_widgets()
        self.check_queue()
        self.refresh_drives()
    
    def setup_logging(self):
        """Set up logging to a file with a maximum size of 10 MB."""
        # Check if the log file exceeds the maximum size
        if os.path.exists(self.LOG_FILE) and os.path.getsize(self.LOG_FILE) > self.LOG_MAX_SIZE:
            os.remove(self.LOG_FILE)
        
        logging.basicConfig(
            filename=self.LOG_FILE,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("USB Checker started.")
    
    def setup_styles(self):
        """Configure custom styles for UI components."""
        self.style = ttk.Style()
        self.style.configure(
            "TButton",
            padding=5,
            relief="flat",
            background="#444",
            foreground="black",
            font=("Arial", 10, "bold")
        )
        self.style.map("TButton", background=[("active", "#666")])
    
    def create_widgets(self):
        """Create and arrange all UI widgets."""
        # Title
        title_frame = tk.Frame(self.root, bg="#2e2e2e")
        title_frame.pack(pady=5)
        tk.Label(
            title_frame,
            text="USB Checker (UCT)",
            font=("Arial", 16, "bold"),
            bg="#2e2e2e",
            fg="white"
        ).pack()
        
        # Drive selection
        drive_frame = tk.Frame(self.root, bg="#2e2e2e")
        drive_frame.pack(pady=5)
        
        self.drive_dropdown = ttk.Combobox(
            drive_frame,
            textvariable=self.selected_drive,
            state="readonly",
            width=25
        )
        self.drive_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(
            drive_frame,
            text="Refresh",
            command=self.refresh_drives,
            style="TButton"
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(refresh_btn, "Refresh the list of available USB drives")
        
        # Open Log File button
        log_btn = ttk.Button(
            drive_frame,
            text="Open Log File",
            command=self.open_log_file,
            style="TButton"
        )
        log_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(log_btn, "Open the application log file")
        
        # Action buttons
        button_frame = tk.Frame(self.root, bg="#2e2e2e")
        button_frame.pack(pady=5)
        
        buttons = [
            ("Analyze", self.analyze_usb, "Analyze the selected USB drive for storage and speed"),
            ("Repair", self.run_repair_in_thread, "Repair the selected USB drive"),
            ("Benchmark", self.run_benchmark_in_thread, "Measure the read/write speed of the USB drive"),
            ("Backup", self.run_backup_in_thread, "Backup data from the USB drive")
        ]
        
        for text, command, tooltip in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, style="TButton")
            btn.pack(side=tk.LEFT, padx=5)
            self.create_tooltip(btn, tooltip)
        
        # Output window
        self.result_display = ScrolledText(
            self.root,
            height=10,
            bg="#1e1e1e",
            fg="lime",
            font=("Consolas", 9),
            state="disabled",
            wrap=tk.WORD
        )
        self.result_display.pack(pady=5, padx=10, fill="both", expand=True)
        self.result_display.tag_configure("center", justify="center")
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.progress.pack(pady=5)
        
        # GitHub link
        github_frame = tk.Frame(self.root, bg="#2e2e2e")
        github_frame.pack(pady=5)
        github_link = tk.Label(
            github_frame,
            text="Visit UCT on GitHub",
            fg="#4af",
            cursor="hand2",
            bg="#2e2e2e",
            font=("Arial", 9, "underline")
        )
        github_link.pack()
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/bl4k7en/UCT"))
    
    def center_window(self, window):
        """Center the given window on the screen."""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        tooltip = tk.Label(
            self.root,
            text=text,
            bg="#ffeb3b",
            fg="black",
            relief="solid",
            borderwidth=1,
            font=("Arial", 8)
        )
        tooltip.pack_forget()
        
        def enter(event):
            x = widget.winfo_rootx() - self.root.winfo_rootx()
            y = widget.winfo_rooty() - self.root.winfo_rooty() + widget.winfo_height()
            tooltip.place(x=x, y=y)
        
        def leave(event):
            tooltip.place_forget()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def check_queue(self):
        """Check the process queue for updates."""
        try:
            while True:
                message = self.process_queue.get_nowait()
                self.update_result_display(message)
        except Empty:
            pass
        self.root.after(100, self.check_queue)
    
    def open_log_file(self):
        """Open the log file in the default text editor."""
        if not os.path.exists(self.LOG_FILE):
            messagebox.showinfo("Info", "Log file does not exist yet.")
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(self.LOG_FILE)
            elif sys.platform == "darwin":
                subprocess.run(["open", self.LOG_FILE], check=False)
            else:
                subprocess.run(["xdg-open", self.LOG_FILE], check=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log file: {e}")
            logging.error(f"Error opening log file: {e}")
    
    def refresh_drives(self):
        """Refresh the list of available USB drives with additional information."""
        try:
            drives = []
            self.drive_mapping.clear()
            
            for partition in psutil.disk_partitions():
                if self.is_usb_drive(partition.device):
                    drive_letter = partition.device
                    drive_label = self.get_drive_label(drive_letter)
                    drive_info = f"{drive_letter} - {drive_label} ({partition.fstype})"
                    
                    drives.append(drive_info)
                    self.drive_mapping[drive_info] = drive_letter
            
            # Update dropdown
            self.drive_dropdown["values"] = drives
            if drives:
                self.drive_dropdown.set(drives[0])
            else:
                self.drive_dropdown.set("")
                self.process_queue.put("No USB drives found.\n")
            
            logging.info(f"Found {len(drives)} USB drive(s)")
        except Exception as e:
            self.process_queue.put(f"Error refreshing drives: {e}\n")
            logging.error(f"Error refreshing drives: {e}")
    
    def is_usb_drive(self, drive_letter):
        """Check if the drive is a USB drive (Windows only)."""
        if sys.platform != "win32":
            # For non-Windows platforms, check if 'removable' is in mount options
            try:
                for partition in psutil.disk_partitions(all=True):
                    if partition.device == drive_letter and "removable" in partition.opts.lower():
                        return True
                return False
            except Exception as e:
                logging.error(f"Error checking if drive is USB: {e}")
                return False
        
        try:
            # Windows: Check if the drive is removable
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_letter)
            return drive_type == 2  # DRIVE_REMOVABLE
        except Exception as e:
            logging.error(f"Error checking if drive is USB: {e}")
            return False
    
    def get_drive_label(self, drive_letter):
        """Get the label of the drive (if available)."""
        if sys.platform != "win32":
            return "No Label"
        
        try:
            volume_name_buffer = ctypes.create_unicode_buffer(1024)
            file_system_buffer = ctypes.create_unicode_buffer(1024)
            
            ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(drive_letter),
                volume_name_buffer,
                ctypes.sizeof(volume_name_buffer),
                None,
                None,
                None,
                file_system_buffer,
                ctypes.sizeof(file_system_buffer)
            )
            
            label = volume_name_buffer.value.strip()
            return label if label else "No Label"
        except Exception as e:
            logging.error(f"Error getting drive label: {e}")
            return "No Label"
    
    def validate_drive(self):
        """Validate the selected drive and return the drive letter."""
        drive_info = self.selected_drive.get()
        if not drive_info:
            messagebox.showwarning("Warning", "Please select a valid USB drive.")
            return None
        
        # Get drive letter from mapping
        drive_letter = self.drive_mapping.get(drive_info)
        if not drive_letter:
            messagebox.showwarning("Warning", "Invalid drive selection.")
            return None
        
        # Verify drive exists
        if not os.path.exists(drive_letter):
            messagebox.showwarning("Warning", f"The drive {drive_letter} is not available.")
            return None
        
        return drive_letter
    
    def analyze_usb(self):
        """Analyze the selected USB drive."""
        drive = self.validate_drive()
        if not drive:
            self.process_queue.put("No drive selected.\n")
            return
        
        try:
            usage = shutil.disk_usage(drive)
            partitions = psutil.disk_partitions()
            drive_info = next((p for p in partitions if p.device == drive), None)
            
            message = f"Drive: {drive}\n"
            if drive_info:
                message += f"File System: {drive_info.fstype}\n"
            
            message += (
                f"Total: {usage.total / (1024**3):.2f} GB\n"
                f"Used: {usage.used / (1024**3):.2f} GB\n"
                f"Free: {usage.free / (1024**3):.2f} GB\n"
                f"Usage: {(usage.used / usage.total * 100):.1f}%\n"
            )
            
            self.process_queue.put(message)
            logging.info(f"Analyzed drive: {drive}")
        except Exception as e:
            self.process_queue.put(f"Error analyzing drive: {e}\n")
            logging.error(f"Error analyzing drive: {e}")
    
    def run_repair_in_thread(self):
        """Run the USB repair process in a separate thread."""
        if self.is_running:
            self.process_queue.put("Another operation is already running.\n")
            return
        
        drive = self.validate_drive()
        if not drive:
            return
        
        # Confirm action
        response = messagebox.askyesno(
            "Confirm Repair",
            f"Do you want to repair drive {drive}?\nThis may take several minutes."
        )
        if not response:
            return
        
        self.is_running = True
        self.progress["value"] = 0
        thread = threading.Thread(target=self.repair_usb, args=(drive,), daemon=True)
        thread.start()
    
    def repair_usb(self, drive):
        """Repair the selected USB drive using chkdsk (Windows only)."""
        if sys.platform != "win32":
            self.process_queue.put("Repair function is only available on Windows.\n")
            self.is_running = False
            return
        
        try:
            # Check for admin privileges
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.process_queue.put("Error: Administrator privileges required for repair.\n")
                return
            
            drive_letter = drive.rstrip("\\").rstrip("/")[0]
            if not drive_letter.isalpha():
                self.process_queue.put(f"Invalid drive letter: {drive_letter}\n")
                return
            
            # Run chkdsk
            chkdsk_path = os.path.join(os.getenv("SystemRoot", "C:\\Windows"), "System32", "chkdsk.exe")
            self.process_queue.put(f"Running chkdsk on {drive_letter}:...\n")
            
            process = subprocess.Popen(
                [chkdsk_path, f"{drive_letter}:", "/f"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Read output
            for line in iter(process.stdout.readline, ""):
                if line.strip():
                    self.process_queue.put(line)
                    if self.progress["value"] < 90:
                        self.progress["value"] += 5
            
            process.wait()
            
            if process.returncode == 0:
                self.process_queue.put("\nRepair completed successfully.\n")
            else:
                stderr = process.stderr.read()
                self.process_queue.put(f"\nRepair completed with warnings.\n{stderr}\n")
            
            self.progress["value"] = 100
            logging.info(f"Repaired drive: {drive}")
        except Exception as e:
            self.process_queue.put(f"Error during repair: {e}\n")
            logging.error(f"Error during repair: {e}")
        finally:
            self.is_running = False
    
    def run_benchmark_in_thread(self):
        """Run the USB benchmark process in a separate thread."""
        if self.is_running:
            self.process_queue.put("Another operation is already running.\n")
            return
        
        drive = self.validate_drive()
        if not drive:
            return
        
        # Check if drive has enough space
        try:
            usage = shutil.disk_usage(drive)
            if usage.free < self.BENCHMARK_SIZE * 1.5:  # 150 MB free space required
                messagebox.showwarning(
                    "Insufficient Space",
                    "Not enough free space on the drive for benchmark test."
                )
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check drive space: {e}")
            return
        
        self.is_running = True
        self.progress["value"] = 0
        self.process_queue.put("Starting benchmark... This may take a few moments.\n")
        thread = threading.Thread(target=self.benchmark_usb, args=(drive,), daemon=True)
        thread.start()
    
    def benchmark_usb(self, drive):
        """Benchmark the selected USB drive."""
        test_file = None
        try:
            self.process_queue.put("Running write test...\n")
            test_file = os.path.join(drive, "uct_benchmark_test.bin")
            
            # Write test
            start_time = time.time()
            with open(test_file, "wb") as f:
                f.write(os.urandom(self.BENCHMARK_SIZE))
            write_time = time.time() - start_time
            write_speed = (self.BENCHMARK_SIZE / (1024 * 1024)) / write_time
            
            self.progress["value"] = 50
            self.process_queue.put("Running read test...\n")
            
            # Read test
            start_time = time.time()
            with open(test_file, "rb") as f:
                while f.read(self.CHUNK_SIZE):
                    pass
            read_time = time.time() - start_time
            read_speed = (self.BENCHMARK_SIZE / (1024 * 1024)) / read_time
            
            # Results
            self.process_queue.put(f"\nBenchmark Results:\n")
            self.process_queue.put(f"Write Speed: {write_speed:.2f} MB/s\n")
            self.process_queue.put(f"Read Speed: {read_speed:.2f} MB/s\n")
            
            self.progress["value"] = 100
            logging.info(f"Benchmarked {drive} - Write: {write_speed:.2f} MB/s, Read: {read_speed:.2f} MB/s")
        except Exception as e:
            self.process_queue.put(f"Error during benchmark: {e}\n")
            logging.error(f"Error during benchmark: {e}")
        finally:
            # Clean up test file
            if test_file and os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except Exception as e:
                    logging.warning(f"Failed to remove test file: {e}")
            self.is_running = False
    
    def run_backup_in_thread(self):
        """Run the USB backup process in a separate thread."""
        if self.is_running:
            self.process_queue.put("Another operation is already running.\n")
            return
        
        drive = self.validate_drive()
        if not drive:
            return
        
        backup_folder = filedialog.askdirectory(title="Select Backup Destination Folder")
        if not backup_folder:
            return
        
        self.is_running = True
        self.progress["value"] = 0
        thread = threading.Thread(target=self.backup_usb, args=(drive, backup_folder), daemon=True)
        thread.start()
    
    def backup_usb(self, drive, backup_folder):
        """Backup data from the selected USB drive."""
        try:
            self.process_queue.put("Starting backup...\n")
            
            # Count total files for progress tracking
            total_files = sum(len(files) for _, _, files in os.walk(drive))
            if total_files == 0:
                self.process_queue.put("No files found to backup.\n")
                return
            
            copied_files = 0
            
            # Copy files
            for root, dirs, files in os.walk(drive):
                # Skip system directories
                dirs[:] = [d for d in dirs if not d.startswith('$') and d != 'System Volume Information']
                
                relative_path = os.path.relpath(root, drive)
                dest_path = os.path.join(backup_folder, relative_path)
                os.makedirs(dest_path, exist_ok=True)
                
                for file in files:
                    try:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_path, file)
                        shutil.copy2(src_file, dest_file)
                        copied_files += 1
                        
                        # Update progress
                        progress = int((copied_files / total_files) * 100)
                        self.progress["value"] = progress
                        
                        if copied_files % 10 == 0:  # Update every 10 files
                            self.process_queue.put(f"Copied {copied_files}/{total_files} files...\n")
                    except Exception as e:
                        logging.warning(f"Failed to copy {src_file}: {e}")
                        continue
            
            self.process_queue.put(f"\nBackup completed: {copied_files} files copied.\n")
            self.progress["value"] = 100
            logging.info(f"Backed up {drive} to {backup_folder} - {copied_files} files")
            messagebox.showinfo("Backup Complete", f"Successfully backed up {copied_files} files.")
        except Exception as e:
            self.process_queue.put(f"Error during backup: {e}\n")
            logging.error(f"Error during backup: {e}")
        finally:
            self.is_running = False
    
    def update_result_display(self, text):
        """Update the result display with new text."""
        self.result_display.config(state="normal")
        self.result_display.insert(tk.END, text)
        self.result_display.see(tk.END)
        self.result_display.config(state="disabled")


def check_admin_privileges():
    """Check if the application is running with administrator privileges."""
    if sys.platform == "win32":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    return True  # Assume admin on non-Windows platforms


def restart_as_admin():
    """Restart the application with administrator privileges."""
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart as administrator: {e}")


def main():
    """Main entry point for the application."""
    # Check for administrator privileges (required for repair function)
    if sys.platform == "win32" and not check_admin_privileges():
        response = messagebox.askyesno(
            "Administrator Privileges",
            "Some features require administrator privileges.\n"
            "Do you want to restart the application as administrator?"
        )
        if response:
            restart_as_admin()
            sys.exit()
    
    # Minimize console window on Windows
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(),
                6  # SW_MINIMIZE
            )
        except:
            pass
    
    # Create and run the application
    root = tk.Tk()
    app = USBCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
