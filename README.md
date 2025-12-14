<p align="center">
  <h1 align="center">USB Checker (UCT)</h1>
</p>

<p align="center">
  USB Checker (UCT) is a user-friendly desktop application designed to help users manage and troubleshoot USB drives efficiently. Built with Python and the Tkinter library, this tool provides a range of features to analyze, repair, benchmark, and back up USB drives. It is particularly useful for diagnosing issues, optimizing performance, and ensuring data safety.
</p>

---

## **Key Features**

### **Drive Analysis**
- Displays detailed information about the selected USB drive, including:
  - Total storage capacity.
  - Used and free space.
- Helps users understand the current state of their USB drive.

### **Drive Repair**
- Runs the `chkdsk` utility to repair file system errors on the selected USB drive.
- Requires administrator privileges to ensure proper execution.
- Provides real-time progress updates during the repair process.

### **Benchmark Test**
- Measures the read and write speeds of the USB drive.
- Performs a 100 MB file write and read test to calculate speed in MB/s.
- Informs the user about the progress and results of the benchmark.

### **Data Backup**
- Allows users to back up data from the USB drive to a selected folder on their computer.
- Preserves the directory structure during the backup process.
- Provides progress updates during the backup operation.

### **Drive Selection**
- Automatically detects and lists all available USB drives.
- Allows users to refresh the list of drives with a single click.

### **Real-Time Output**
- Displays real-time progress and results in a scrollable output window.
- Keeps users informed about the status of ongoing operations.

### **Progress Bar**
- Visualizes the progress of operations like repair, benchmark, and backup.
- Provides a clear indication of how much of the task is completed.

### **Log Management**
- Logs all operations to a file for troubleshooting.
- Includes an "Open Log File" button for easy access to logs.
- Automatically manages log file size (max 10 MB).

---

## **How It Works**

1. **Select a USB Drive**:
   - Choose the desired USB drive from the dropdown menu.

2. **Perform Actions**:
   - Use the buttons to analyze, repair, benchmark, or back up the selected drive.
   - Each operation runs in a separate thread to keep the interface responsive.

3. **View Results**:
   - Results and progress are displayed in the output window in real-time.
   - Detailed logs are saved to a file (`usb_checker.log`) for future reference.

---

## **Screenshots**

<p align="center">
  <h3>Main Interface</h3>
  <img src="https://storage.ko-fi.com/cdn/useruploads/display/2f90d7b9-4849-429a-8898-828f91d86b3e_uct.png" alt="USB Checker (UCT) Main Interface" width="600"/>
</p>

<p align="center">
  <h3>Drive Analysis</h3>
  <img src="https://storage.ko-fi.com/cdn/useruploads/display/87c158d4-058b-4fa1-b82c-9cd2bf91234b_python3.12_1k7dngpq9i.png" alt="USB Checker Drive Analysis" width="600"/>
</p>

<p align="center">
  <h3>Benchmark Results</h3>
  <img src="https://storage.ko-fi.com/cdn/useruploads/display/425d75bc-b1c4-4759-8a16-e38cd586b33a_python3.12_q1cooqcodo.png" alt="USB Checker Benchmark Results" width="600"/>
</p>

---

## **System Requirements**

- **Operating System**: Windows (due to the use of `chkdsk` and `diskpart`).
- **Python Version**: Python 3.x.
- **Required Libraries**: `tkinter`, `psutil`, `shutil`, `subprocess`, `threading`, `webbrowser`, `ctypes`, `logging`.

---

## **Installation**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pxelbrei/UCT.git
   cd UCT
