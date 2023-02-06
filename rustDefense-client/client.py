import socketio
import subprocess
import winreg
import vdf
import psutil
import json
import cli_ui
import srcs.helpers as helpers

env_data = json.load(open('srcs/conf.json', 'r'))

debug = False

menu_loop = True
while menu_loop:
    choices = ["Add/Remove Phone Number", "Start Program"]

    selection = cli_ui.ask_choice("Choose an action", choices=choices)

    if selection == "Add/Remove Phone Number":
        helpers.phone_operations()
    elif selection == "Start Program":
        menu_loop = False

sio = socketio.Client()
sio.connect(env_data["url"])

cli_ui.info_2(f'Connection established with SID {sio.sid}\n')
cli_ui.info_1(f'Waiting for raid signal [Do not exit the app]')

if debug:
    @sio.on('test_event')
    def on_message():
        print("Test Event Received")


@sio.on('raid')
def raid_alert(server):
    cli_ui.info_1("Raid signal received. Launching Rust and connecting to the server!")

    if "RustClient.exe" not in (p.name() for p in psutil.process_iter()):
        hkey_local = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(hkey_local, r"SOFTWARE\WOW6432Node\Valve\Steam")
        steam_path = winreg.QueryValueEx(key, 'InstallPath')[0]

        library_folders = vdf.load(open(rf'{steam_path}\steamapps\libraryfolders.vdf'))

        location = get_location(library_folders)

        acf = vdf.load(open(rf'{steam_path}\steamapps\appmanifest_252490.acf'))
        name = acf["AppState"]["name"]

        rust_location = fr'{location}\steamapps\common\{name}\Rust.exe'
        cwd = fr"{location}\steamapps\common\{name}"

        args = f'{rust_location} +connect {server} -gc.buffer 4096 -headlerp_inertia 0' \
               f' -window-mode exclusive -high'

        subprocess.call(args, cwd=cwd)
    else:
        print('Rust already running')


def get_location(library_folders):
    for folder in library_folders['libraryfolders']:
        for app in library_folders['libraryfolders'][folder]['apps']:
            if app == "252490":
                library_location = library_folders['libraryfolders'][folder]['path']
                return library_location
