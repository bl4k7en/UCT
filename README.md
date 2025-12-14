# USB Checker (UCT)

<p align="center">
  <img src="https://storage.ko-fi.com/cdn/useruploads/display/2f90d7b9-4849-429a-8898-828f91d86b3e_uct.png" alt="USB Checker (UCT) Screenshot" width="600"/>
</p>

## 📋 Overview

USB Checker (UCT) is a Windows desktop application built with Python and Tkinter for comprehensive USB drive management. The tool provides an intuitive interface to analyze, repair, benchmark, and backup USB drives with real-time feedback.

## ✨ Features

### 🔍 Drive Analysis
- Displays detailed information about selected USB drives
- Shows total, used, and free storage space in GB
- Displays file system type and drive label
- Automatic USB drive detection with refresh capability

### 🔧 Drive Repair
- Executes Windows `chkdsk` utility to fix file system errors
- Requires and automatically requests administrator privileges
- Real-time progress updates during repair process
- Logs all repair activities for troubleshooting

### 📊 Benchmark Testing
- Performs 100MB read/write speed tests
- Measures and displays both read and write speeds in MB/s
- Automatic cleanup of test files after benchmarking
- Progress visualization during testing

### 💾 Data Backup
- Full directory structure preservation during backup
- Interactive folder selection for backup destination
- Progress tracking during backup operations
- Safe file copying with metadata preservation

### 📝 Log Management
- Comprehensive logging to `usb_checker.log` file
- Automatic log file rotation (max 10MB size)
- One-click access to log file via "Open Log File" button
- Timestamped operations for debugging

## 🖥️ Interface

### Main Window Components:
- **Drive Selection**: Dropdown with auto-detected USB drives showing drive letter, label, and file system
- **Action Buttons**: Analyze, Repair, Benchmark, Backup
- **Refresh Button**: Updates available USB drive list
- **Output Display**: Real-time scrollable text area showing operation results
- **Progress Bar**: Visual progress indicator for long-running operations
- **GitHub Link**: Direct link to project repository

## 🚀 Installation

### Prerequisites:
- Windows operating system
- Python 3.x installed
- Administrator privileges (for repair functionality)

### Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/bl4k7en/UCT.git
   cd UCT
