import requests
import cli_ui
import socket
import json

env_data = json.load(open('srcs/conf.json', 'r'))


def phone_operations():
    action = cli_ui.ask_choice("Would you like to add or remove your number?", choices=["add", "remove"])

    get_number_loop = True
    while get_number_loop:
        number = cli_ui.ask_string("Please enter your 10 digit US or Canadian phone number")
        if not (number.isdigit()):
            cli_ui.error("Sorry, that number is not valid. Ensure you are only typing in numbers.")
            continue

        if not (len(number) == 10):
            cli_ui.error("Sorry, that number is not valid. Check the number of characters.")
            continue

        get_number_loop = False

    password_loop = True
    while password_loop:
        password = cli_ui.ask_string("Enter your password. This should be posted in #automation-announcements")

        data = {
            "password": password,
            "number": number,
            "action": action,
            "hostname": socket.gethostname()
        }

        r = requests.post(f'{env_data["url"]}/phone', json=data)

        if r.status_code == 200:
            cli_ui.info_1(f"Success.")
            return

        elif r.status_code == 401:
            cli_ui.error('Authentication error, please enter the password again.')

        elif r.status_code == 400:
            if action == "add":
                cli_ui.error('Client error, is your phone number already registered?')
            else:
                cli_ui.error('Client error, is your phone number registered?')

            return

        else:
            cli_ui.error(f'Unknown error with status code {r.status_code}, try again.')
            return
