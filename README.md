# USB Checker (UCT)

A Windows desktop application for USB drive management and troubleshooting, built with Python and Tkinter.

<p align="center">
  <img src="https://storage.ko-fi.com/cdn/useruploads/display/87c158d4-058b-4fa1-b82c-9cd2bf91234b_python3.12_1k7dngpq9i.png" alt="Python 3.12 Feature Example 1"/>
</p>
<p align="center">
  <img src="https://storage.ko-fi.com/cdn/useruploads/display/425d75bc-b1c4-4759-8a16-e38cd586b33a_python3.12_q1cooqcodo.png" alt="Python 3.12 Feature Example 2"/>
</p>

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
