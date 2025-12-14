# USB Checker (UCT)

A Windows desktop application for USB drive management and troubleshooting, built with Python and Tkinter.

## Features
- **Drive Analysis**: Shows drive information including capacity, used/free space, file system, and label
- **Drive Repair**: Runs chkdsk to fix file system errors (requires admin rights)
- **Data Backup**: Backs up USB drive contents to a selected folder
- **Drive Detection**: Automatically detects and lists USB drives
- **Real-time Output**: Shows operation progress in a scrollable window
- **Logging**: Saves all operations to usb_checker.log with auto-rotation

## Requirements
- Windows
- Python 3.x
- psutil library

## Installation
```bash
git clone https://github.com/bl4k7en/UCT.git
cd UCT
pip install psutil
python usb_checker.py
