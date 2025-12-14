# USB Checker (UCT)

A Windows desktop application for USB drive management, built with Python and Tkinter. Provides tools for analyzing, repairing, formatting, backing up, and wiping USB drives with a clean graphical interface.

## Features
- **Drive Analysis**: View detailed storage information and drive properties
- **Drive Repair**: Fix file system errors using Windows chkdsk
- **Format Drives**: Quick/Full format with multiple file system options
- **Data Backup**: Backup USB contents with directory structure preservation
- **Data Wiping**: Securely erase drive contents
- **Auto Detection**: Automatically identifies USB drives
- **Logging**: Comprehensive operation logging with easy access

## Requirements
- Windows OS
- Python 3.x
- psutil library

## Installation
```bash
git clone https://github.com/bl4k7en/UCT.git
cd UCT
pip install psutil
python usb_checker.py
