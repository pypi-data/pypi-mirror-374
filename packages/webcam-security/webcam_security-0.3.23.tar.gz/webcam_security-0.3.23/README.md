# Webcam Security

[![PyPI version](https://img.shields.io/pypi/v/webcam-security.svg?style=flat-square)](https://pypi.org/project/webcam-security/)
[![Python Versions](https://img.shields.io/pypi/pyversions/webcam-security.svg?style=flat-square)](https://pypi.org/project/webcam-security/)
[![Downloads](https://img.shields.io/pypi/dm/webcam-security?style=flat-square)](https://pypi.org/project/webcam-security/)

A Python package for webcam security monitoring with Telegram notifications. This package provides updatedon detection capabilities with configurable monitoring hours and automatic video recording.

## Features

- 🎥 Real-time motion detection using webcam
- 📱 Telegram notifications with snapshots and device identification
- ⏰ Configurable monitoring hours (default: 10 PM - 6 AM)
- 🔧 Telegram bot commands for remote configuration
- 🚨 Force monitoring on/off via Telegram
- 🎬 Automatic video recording on motion detection
- 🎵 Audio recording with video (combined MP4 format)
- 🧹 Automatic cleanup of old recordings
- 🖥️ Live preview with monitoring status
- 🚀 Easy-to-use CLI interface
- 🔄 Self-update mechanism
- ⚡ UV-powered for faster builds and dependency management

## Telegram Bot Commands

Once the monitoring is running, you can control it remotely via Telegram commands:

### Status & Control
- `/start` - Welcome message and command list
- `/status` - Show current configuration and monitoring status
- `/help` - Show detailed help and command reference
- `/force_on` - Force monitoring ON (ignores time schedule)
- `/force_off` - Force monitoring OFF (returns to normal schedule)
- `/peek` - Take manual photo and send to Telegram

### Configuration
- `/set_hours <start> <end>` - Set monitoring hours (24h format)
  - Example: `/set_hours 22 6` (10 PM to 6 AM)
  - Example: `/set_hours 0 24` (24/7 monitoring)

### System
- `/update` - Check for software updates
- `/update_async` - Start async update with retry logic (5 attempts)
- `/restart_bot` - Restart bot polling thread if it stops responding
- `/restart` - Restart entire application (loads new code after updates)

## Usage

### Quick Start

1. **Initialize configuration:**
   ```bash
   webcam-security init --bot-token "YOUR_BOT_TOKEN" --chat-id "YOUR_CHAT_ID" --device-id "MyCamera" --media-path "~/my-recordings"
   ```

2. **Start monitoring:**
   ```bash
   webcam-security start
   ```

3. **Control remotely via Telegram:**
   - Send `/start` to your bot for command list
   - Use `/force_on` to enable monitoring immediately
   - Use `/set_hours 22 6` to set monitoring hours
   - Use `/restart` to restart the application after updates

### Device Identification

All media sent to Telegram includes a device identifier:
- If you specify `--device-id` during init, that name will be used
- Otherwise, the system hostname will be used automatically
- This helps identify which camera sent the alert when you have multiple systems

### Media Storage

Recordings and snapshots are stored in a configurable location:
- **Default**: `~/webcam-security` (in your home directory)
- **Custom**: Use `--media-path` during init or `/set_media_path` via Telegram
- **Examples**: 
  - `~/Documents/security` - Store in Documents folder
  - `/var/security/recordings` - Store in system directory
  - `~/Desktop/camera1` - Store on desktop with device name

### Application Restart

After updating the software, new features may not be available until the application is restarted:
- **CLI**: Use `webcam-security restart` to restart the application
- **Telegram**: Use `/restart` command to restart the application
- **Manual**: Stop the application (Ctrl+C) and run `webcam-security start` again

### Available Commands

- `webcam-security init` - Initialize configuration
- `webcam-security start` - Start monitoring
- `webcam-security status` - Show current configuration
- `webcam-security clean` - Manually clean old recordings
- `webcam-security update` - Check for and install updates
- `webcam-security self-update` - Auto-update and restart
- `webcam-security self-update-async` - Start async update with retry logic
- `webcam-security restart` - Restart application to load updated code

