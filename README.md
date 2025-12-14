# USB Checker (UCT)

<p align="center">
  <img src="https://storage.ko-fi.com/cdn/useruploads/display/2f90d7b9-4849-429a-8898-828f91d86b3e_uct.png" alt="USB Checker (UCT) Main Interface" width="600"/>
</p>

## 📋 Overview

USB Checker (UCT) is a comprehensive Windows desktop application for USB drive management, troubleshooting, and data operations. Built with Python and Tkinter, it provides an all-in-one solution for USB drive maintenance with a clean, user-friendly interface.

## ✨ Features

### 🔍 **Drive Information & Analysis**
- **Detailed Drive Information**: Shows drive letter, file system type, and volume label
- **Storage Analysis**: Displays total, used, and free space in gigabytes
- **Smart Detection**: Automatically identifies and lists only USB/removable drives
- **Real-time Refresh**: Update drive list with one click

### 🛠️ **Drive Maintenance & Repair**
- **File System Repair**: Executes Windows `chkdsk` utility to fix errors
- **Automatic Admin Elevation**: Requests administrator privileges when needed
- **Progress Monitoring**: Real-time updates during repair operations
- **Safe Operation**: Validates drives before performing repairs

### 📁 **File Management Operations**
- **Quick Format**: Fast format option for USB drives (FAT32/NTFS)
- **Full Format**: Complete format with sector checking
- **File System Selection**: Choose between NTFS, FAT32, or exFAT formats
- **Secure Format**: Optional quick format bypass for thorough cleaning

### 💾 **Advanced Data Operations**
- **Data Backup**: Complete backup of USB drive contents with directory structure preservation
- **Data Wiping**: Secure erase functionality for sensitive data
- **Progress Tracking**: Visual progress bar for all operations
- **Error Handling**: Comprehensive error checking and user feedback

### 📝 **System & Logging**
- **Comprehensive Logging**: All operations logged to `usb_checker.log`
- **Log Management**: Automatic log rotation (10MB max size)
- **Easy Access**: One-click log file opening
- **Real-time Output**: Scrollable output window showing operation progress

## 🖥️ User Interface

### Interface Components:
- **Drive Selection Dropdown**: Shows detected USB drives with format: `DriveLetter - Label (FileSystem)`
- **Action Buttons**: 
  - Analyze: Get drive information
  - Repair: Fix file system errors
  - Format: Format the drive
  - Backup: Backup drive contents
  - Wipe: Securely erase data
- **Control Buttons**:
  - Refresh: Update drive list
  - Open Log File: View operation logs
- **Output Display**: Real-time operation feedback
- **Progress Bar**: Visual operation progress
- **GitHub Link**: Direct link to source repository

## 🚀 Installation & Setup

### Requirements:
- **Operating System**: Windows 10/11
- **Python**: Version 3.6 or higher
- **Privileges**: Administrator rights for full functionality

### Installation Steps:

1. **Clone the repository**:
```bash
git clone https://github.com/bl4k7en/UCT.git
cd UCT
