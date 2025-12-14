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
from datetime import datetime
import zipfile

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
        
        # Analyze button
        analyze_btn = ttk.Button(button_frame, text="Analyze", command=self.run_analyze_in_thread, style="TButton")
        analyze_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(analyze_btn, "Analyze the selected USB drive for storage and speed")
        
        # Repair dropdown menu
        repair_menu_btn = ttk.Menubutton(button_frame, text="Repair ▼", style="TButton")
        repair_menu_btn.pack(side=tk.LEFT, padx=5)
        
        repair_menu = tk.Menu(repair_menu_btn, tearoff=0, bg="#444", fg="white", activebackground="#666", activeforeground="white")
        repair_menu_btn.config(menu=repair_menu)
        
        repair_menu.add_command(
            label="Quick Repair",
            command=lambda: self.run_repair_in_thread(quick=True)
        )
        repair_menu.add_command(
            label="Deep Repair",
            command=lambda: self.run_repair_in_thread(quick=False)
        )
        
        self.create_tooltip(repair_menu_btn, "Repair the selected USB drive\nQuick: Fast file system fix (1-5 min)\nDeep: Full scan with bad sectors (hours)")
        
        # Backup button
        backup_btn = ttk.Button(button_frame, text="Backup", command=self.run_backup_in_thread, style="TButton")
        backup_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(backup_btn, "Create a ZIP backup of the USB drive")
        
        # Output window
        self.result_display = ScrolledText(
            self.root,
            height=8,
            bg="#1e1e1e",
            fg="lime",
            font=("Consolas", 8),
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
        """Create a tooltip for a widget that stays on top."""
        tooltip = tk.Toplevel(self.root)
        tooltip.withdraw()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_attributes("-topmost", True)
        
        label = tk.Label(
            tooltip,
            text=text,
            bg="#ffeb3b",
            fg="black",
            relief="solid",
            borderwidth=1,
            font=("Arial", 8),
            padx=5,
            pady=2
        )
        label.pack()
        
        def enter(event):
            x = widget.winfo_rootx() + 10
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def leave(event):
            tooltip.withdraw()
        
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
    
    def run_analyze_in_thread(self):
        """Run the USB analysis in a separate thread."""
        if self.is_running:
            self.process_queue.put("Another operation is already running.\n")
            return
        
        drive = self.validate_drive()
        if not drive:
            return
        
        # Check if drive has enough space for benchmark
        try:
            usage = shutil.disk_usage(drive)
            if usage.free < self.BENCHMARK_SIZE * 1.5:  # 150 MB free space required
                response = messagebox.askyesno(
                    "Insufficient Space for Speed Test",
                    "Not enough free space for speed benchmark.\n\n"
                    "Continue with storage analysis only?"
                )
                if not response:
                    return
                # Run only storage analysis
                self.analyze_usb(drive)
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check drive space: {e}")
            return
        
        self.is_running = True
        self.progress["value"] = 0
        thread = threading.Thread(target=self.analyze_usb_full, args=(drive,), daemon=True)
        thread.start()
    
    def analyze_usb(self, drive):
        """Analyze storage information of the selected USB drive."""
        try:
            usage = shutil.disk_usage(drive)
            partitions = psutil.disk_partitions()
            drive_info = next((p for p in partitions if p.device == drive), None)
            
            message = f"{'='*50}\n"
            message += f"STORAGE ANALYSIS\n"
            message += f"{'='*50}\n"
            message += f"Drive: {drive}\n"
            if drive_info:
                message += f"File System: {drive_info.fstype}\n"
            
            message += (
                f"Total: {usage.total / (1024**3):.2f} GB\n"
                f"Used: {usage.used / (1024**3):.2f} GB\n"
                f"Free: {usage.free / (1024**3):.2f} GB\n"
                f"Usage: {(usage.used / usage.total * 100):.1f}%\n"
                f"{'='*50}\n"
            )
            
            self.process_queue.put(message)
            
            # Detailed logging
            logging.info(f"Storage Analysis - Drive: {drive}")
            if drive_info:
                logging.info(f"File System: {drive_info.fstype}")
            logging.info(f"Total: {usage.total / (1024**3):.2f} GB")
            logging.info(f"Used: {usage.used / (1024**3):.2f} GB")
            logging.info(f"Free: {usage.free / (1024**3):.2f} GB")
            logging.info(f"Usage: {(usage.used / usage.total * 100):.1f}%")
        except Exception as e:
            self.process_queue.put(f"Error analyzing drive: {e}\n")
            logging.error(f"Error analyzing drive {drive}: {e}")
    
    def analyze_usb_full(self, drive):
        """Perform complete analysis including storage and speed benchmark."""
        test_file = None
        try:
            # First: Storage Analysis
            usage = shutil.disk_usage(drive)
            partitions = psutil.disk_partitions()
            drive_info = next((p for p in partitions if p.device == drive), None)
            
            message = f"{'='*50}\n"
            message += f"USB DRIVE ANALYSIS\n"
            message += f"{'='*50}\n"
            message += f"Drive: {drive}\n"
            if drive_info:
                message += f"File System: {drive_info.fstype}\n"
            
            message += (
                f"Total: {usage.total / (1024**3):.2f} GB\n"
                f"Used: {usage.used / (1024**3):.2f} GB\n"
                f"Free: {usage.free / (1024**3):.2f} GB\n"
                f"Usage: {(usage.used / usage.total * 100):.1f}%\n"
                f"{'='*50}\n"
            )
            
            self.process_queue.put(message)
            
            # Log storage analysis
            logging.info(f"Full Analysis Started - Drive: {drive}")
            if drive_info:
                logging.info(f"File System: {drive_info.fstype}")
            logging.info(f"Total: {usage.total / (1024**3):.2f} GB")
            logging.info(f"Used: {usage.used / (1024**3):.2f} GB")
            logging.info(f"Free: {usage.free / (1024**3):.2f} GB")
            logging.info(f"Usage: {(usage.used / usage.total * 100):.1f}%")
            
            self.progress["value"] = 20
            
            # Second: Speed Benchmark
            self.process_queue.put("Running speed benchmark...\n")
            self.process_queue.put("Testing write speed...\n")
            logging.info("Starting speed benchmark - Write test")
            
            test_file = os.path.join(drive, "uct_benchmark_test.bin")
            
            # Write test
            start_time = time.time()
            with open(test_file, "wb") as f:
                f.write(os.urandom(self.BENCHMARK_SIZE))
            write_time = time.time() - start_time
            write_speed = (self.BENCHMARK_SIZE / (1024 * 1024)) / write_time
            
            logging.info(f"Write test completed - Speed: {write_speed:.2f} MB/s, Time: {write_time:.2f}s")
            
            self.progress["value"] = 60
            self.process_queue.put("Testing read speed...\n")
            logging.info("Starting read test")
            
            # Read test
            start_time = time.time()
            with open(test_file, "rb") as f:
                while f.read(self.CHUNK_SIZE):
                    pass
            read_time = time.time() - start_time
            read_speed = (self.BENCHMARK_SIZE / (1024 * 1024)) / read_time
            
            logging.info(f"Read test completed - Speed: {read_speed:.2f} MB/s, Time: {read_time:.2f}s")
            
            # Results
            self.process_queue.put(f"\nSPEED BENCHMARK RESULTS\n")
            self.process_queue.put(f"{'='*50}\n")
            self.process_queue.put(f"Write Speed: {write_speed:.2f} MB/s\n")
            self.process_queue.put(f"Read Speed: {read_speed:.2f} MB/s\n")
            
            # Performance rating
            avg_speed = (write_speed + read_speed) / 2
            if avg_speed > 100:
                rating = "Excellent (USB 3.0+)"
            elif avg_speed > 30:
                rating = "Good (USB 3.0)"
            elif avg_speed > 10:
                rating = "Average (USB 2.0)"
            else:
                rating = "Slow (USB 2.0 or older)"
            
            self.process_queue.put(f"Performance: {rating}\n")
            self.process_queue.put(f"{'='*50}\n")
            
            logging.info(f"Performance Rating: {rating}")
            logging.info(f"Average Speed: {avg_speed:.2f} MB/s")
            logging.info(f"Analysis completed successfully for {drive}")
            
            self.progress["value"] = 100
        except Exception as e:
            self.process_queue.put(f"Error during analysis: {e}\n")
            logging.error(f"Error during full analysis of {drive}: {e}")
        finally:
            # Clean up test file
            if test_file and os.path.exists(test_file):
                try:
                    os.remove(test_file)
                    logging.info("Benchmark test file removed")
                except Exception as e:
                    logging.warning(f"Failed to remove test file: {e}")
            self.is_running = False
    
    def run_repair_in_thread(self, quick=True):
        """Run the USB repair process in a separate thread."""
        if self.is_running:
            self.process_queue.put("Another operation is already running.\n")
            return
        
        drive = self.validate_drive()
        if not drive:
            return
        
        mode_text = "Quick Repair" if quick else "Deep Repair"
        duration_text = "1-5 minutes" if quick else "several minutes to hours"
        
        # Confirm action
        confirm_msg = f"Start {mode_text} on drive {drive}?\n\nEstimated time: {duration_text}"
        if not quick:
            confirm_msg += "\n\nNote: Deep Repair scans every sector and can take very long!"
        
        response = messagebox.askyesno(f"Confirm {mode_text}", confirm_msg)
        if not response:
            return
        
        self.is_running = True
        self.progress["value"] = 0
        thread = threading.Thread(target=self.repair_usb, args=(drive, quick), daemon=True)
        thread.start()
    
    def repair_usb(self, drive, quick=True):
        """Repair the selected USB drive using chkdsk (Windows only)."""
        if sys.platform != "win32":
            self.process_queue.put("Repair function is only available on Windows.\n")
            logging.warning("Repair attempted on non-Windows platform")
            self.is_running = False
            return
        
        try:
            # Check for admin privileges
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.process_queue.put("Error: Administrator privileges required for repair.\n")
                logging.error("Repair failed - No administrator privileges")
                return
            
            drive_letter = drive.rstrip("\\").rstrip("/")[0]
            if not drive_letter.isalpha():
                self.process_queue.put(f"Invalid drive letter: {drive_letter}\n")
                logging.error(f"Invalid drive letter: {drive_letter}")
                return
            
            # Determine repair mode
            mode_text = "Quick Repair" if quick else "Deep Repair"
            parameters = [f"{drive_letter}:", "/f"]
            
            if not quick:
                parameters.append("/r")  # Add /r for bad sector scan
            
            # Run chkdsk
            chkdsk_path = os.path.join(os.getenv("SystemRoot", "C:\\Windows"), "System32", "chkdsk.exe")
            self.process_queue.put(f"{'='*50}\n")
            self.process_queue.put(f"Starting {mode_text} on {drive_letter}:\n")
            self.process_queue.put(f"{'='*50}\n")
            
            logging.info(f"{mode_text} started on {drive_letter}:")
            logging.info(f"Command: {chkdsk_path} {' '.join(parameters)}")
            
            if not quick:
                self.process_queue.put("WARNING: Deep Repair may take several hours!\n")
                self.process_queue.put("The drive will be scanned sector by sector.\n\n")
                logging.warning("Deep Repair initiated - This may take several hours")
            
            process = subprocess.Popen(
                [chkdsk_path] + parameters,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Read output
            line_count = 0
            for line in iter(process.stdout.readline, ""):
                if line.strip():
                    self.process_queue.put(line)
                    line_count += 1
                    
                    # Update progress (more conservative for deep repair)
                    if quick:
                        if self.progress["value"] < 90:
                            self.progress["value"] += 5
                    else:
                        # For deep repair, progress more slowly
                        if line_count % 10 == 0 and self.progress["value"] < 95:
                            self.progress["value"] += 1
            
            process.wait()
            
            if process.returncode == 0:
                self.process_queue.put(f"\n{'='*50}\n")
                self.process_queue.put(f"{mode_text} completed successfully!\n")
                self.process_queue.put(f"{'='*50}\n")
                logging.info(f"{mode_text} completed successfully on {drive_letter}:")
            else:
                stderr = process.stderr.read()
                self.process_queue.put(f"\n{'='*50}\n")
                self.process_queue.put(f"{mode_text} completed with warnings.\n")
                if stderr:
                    self.process_queue.put(f"{stderr}\n")
                    logging.warning(f"{mode_text} completed with warnings: {stderr}")
                self.process_queue.put(f"{'='*50}\n")
                logging.warning(f"{mode_text} completed with return code: {process.returncode}")
            
            self.progress["value"] = 100
        except Exception as e:
            self.process_queue.put(f"Error during repair: {e}\n")
            logging.error(f"Error during {mode_text} on {drive}: {e}")
        finally:
            self.is_running = False
    
    def run_backup_in_thread(self):
        """Run the USB backup process in a separate thread."""
        if self.is_running:
            self.process_queue.put("Another operation is already running.\n")
            return
        
        drive = self.validate_drive()
        if not drive:
            return
        
        # Ask user to choose backup location and filename
        default_name = f"USB_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        backup_file = filedialog.asksaveasfilename(
            title="Save Backup As",
            defaultextension=".zip",
            filetypes=[("ZIP Archive", "*.zip"), ("All Files", "*.*")],
            initialfile=default_name
        )
        
        if not backup_file:
            return
        
        # Confirm action
        try:
            usage = shutil.disk_usage(drive)
            size_gb = usage.used / (1024**3)
            response = messagebox.askyesno(
                "Confirm Backup",
                f"Create a ZIP backup of {drive}?\n\n"
                f"Used space: {size_gb:.2f} GB\n"
                f"This may take several minutes.\n\n"
                f"Save to: {os.path.basename(backup_file)}"
            )
            if not response:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check drive size: {e}")
            return
        
        self.is_running = True
        self.progress["value"] = 0
        thread = threading.Thread(target=self.backup_usb, args=(drive, backup_file), daemon=True)
        thread.start()
    
    def backup_usb(self, drive, backup_file):
        """Create a ZIP backup of the entire USB drive."""
        try:
            self.process_queue.put(f"Creating ZIP backup: {os.path.basename(backup_file)}\n")
            
            # Count total files for progress tracking
            total_files = 0
            total_size = 0
            files_to_backup = []
            
            self.process_queue.put("Scanning drive...\n")
            
            for root, dirs, files in os.walk(drive):
                # Skip system directories
                dirs[:] = [d for d in dirs if not d.startswith('$') and d != 'System Volume Information']
                
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        files_to_backup.append((file_path, file_size))
                        total_files += 1
                        total_size += file_size
                    except Exception as e:
                        logging.warning(f"Cannot access file {file_path}: {e}")
                        continue
            
            if total_files == 0:
                self.process_queue.put("No files found to backup.\n")
                return
            
            self.process_queue.put(f"Found {total_files} files ({total_size / (1024**3):.2f} GB)\n")
            self.process_queue.put("Creating ZIP archive...\n")
            
            # Create ZIP file
            processed_size = 0
            processed_files = 0
            
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                for file_path, file_size in files_to_backup:
                    try:
                        # Get relative path for archive
                        arcname = os.path.relpath(file_path, drive)
                        zipf.write(file_path, arcname)
                        
                        processed_files += 1
                        processed_size += file_size
                        
                        # Update progress based on size processed
                        progress = int((processed_size / total_size) * 100)
                        self.progress["value"] = min(progress, 99)
                        
                        if processed_files % 50 == 0:  # Update every 50 files
                            self.process_queue.put(
                                f"Progress: {processed_files}/{total_files} files "
                                f"({processed_size / (1024**3):.2f} GB)\n"
                            )
                    except Exception as e:
                        logging.warning(f"Failed to add {file_path} to ZIP: {e}")
                        continue
            
            # Get final ZIP size
            zip_size = os.path.getsize(backup_file)
            compression_ratio = (1 - zip_size / total_size) * 100 if total_size > 0 else 0
            
            self.process_queue.put(f"\n{'='*50}\n")
            self.process_queue.put(f"Backup completed successfully!\n")
            self.process_queue.put(f"Files backed up: {processed_files}\n")
            self.process_queue.put(f"Original size: {total_size / (1024**3):.2f} GB\n")
            self.process_queue.put(f"ZIP size: {zip_size / (1024**3):.2f} GB\n")
            self.process_queue.put(f"Compression: {compression_ratio:.1f}%\n")
            self.process_queue.put(f"Saved to: {backup_file}\n")
            self.process_queue.put(f"{'='*50}\n")
            
            self.progress["value"] = 100
            logging.info(f"Backed up {drive} to {backup_file} - {processed_files} files, {zip_size / (1024**3):.2f} GB")
            
            messagebox.showinfo(
                "Backup Complete",
                f"Successfully backed up {processed_files} files.\n\n"
                f"ZIP size: {zip_size / (1024**3):.2f} GB\n"
                f"Compression: {compression_ratio:.1f}%"
            )
        except Exception as e:
            self.process_queue.put(f"Error during backup: {e}\n")
            logging.error(f"Error during backup: {e}")
            messagebox.showerror("Backup Failed", f"An error occurred during backup:\n{e}")
        finally:
            self.is_running = False
    
    def update_result_display(self, text):
        """Update the result display with new text and log it."""
        self.result_display.config(state="normal")
        self.result_display.insert(tk.END, text)
        self.result_display.see(tk.END)
        self.result_display.config(state="disabled")
        
        # Also log to file (remove empty lines and format)
        if text.strip():
            # Remove ANSI codes and excessive newlines
            clean_text = text.strip()
            if clean_text and clean_text != "="*50:
                logging.info(clean_text)


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
