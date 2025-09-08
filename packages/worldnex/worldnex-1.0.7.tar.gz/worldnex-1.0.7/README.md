# Nex  

Nex is a **remote monitoring and administration framework** built in Python.  
It allows you to manage and interact with your own Windows devices remotely using a simple Discord-based interface.  

**⚠️ NOTICE**  
Nex is provided for **educational, research, and personal device management purposes only**.  
It is **not intended for unauthorized access** to computers.  

---

## Installation  
First create a discord bot and add it to your new made empty discord channel

pip install worldnex

import nex  

nex.start("BOT_TOKEN", UserID = DISCORD_USER_ID, ServerID = DISCORD_SERVER_ID)  

Once the bot is online, type `access` in different Discord channels to switch between the infected computers(main channel has access to ever single infected computer).

type `!h` in to see all available commands. 

and use the file exe file in the dist folder.

---

## Features  

- Remote desktop monitoring (screenshots, screen recording).  
- Camera access for personal device checks.  
- Command execution on your own machines.  
- Network control (toggle Wi-Fi).  
- System power management (shutdown, restart).  
- Process management (list, terminate).  
- Input & activity logging for testing environments.  
- Export of browser session data for research/demonstration.  

---

## Usage  

- Each device has a **unique session ID**, making it easy to reconnect.  
- To send a command to all connected devices, use `all` as the session ID.  
- Some features may require administrative privileges.  
- Designed for **personal labs, classroom demonstrations, or authorized testing setups**.  

---

## Disclaimer  

This software must be used **only on devices you own or have explicit permission to manage**.  
Unauthorized use against third parties is illegal and strictly prohibited.  

The author accepts **no responsibility** for misuse. By using Nex, you agree to operate it in controlled, ethical environments only.  

---

## Development  

- Windows functionality is currently the most complete.  
- Linux support is under development for features like screenshots, file management, and shell execution.  
