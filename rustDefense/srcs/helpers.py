import json
import plivo

env_data = json.load(open('srcs/env.json', 'r'))

plivo_auth_id = env_data["data"]["plivo"]["auth_id"]
plivo_auth_token = env_data["data"]["plivo"]["auth_token"]
group_phlo_id = env_data["data"]["plivo"]["group_phlo"]

phlo_client = plivo.phlo.RestClient(auth_id=plivo_auth_id, auth_token=plivo_auth_token)
general_phlo = phlo_client.phlo.get(group_phlo_id)

voice_phlo_id = env_data["data"]["plivo"]["voice_phlo"]
voice_phlo = phlo_client.phlo.get(voice_phlo_id)

from_number = env_data["data"]["plivo"]["number"]


def send_alerts(numbers, body, phone=True, text=True):
    for number in numbers:
        max_retries = 3
        retries = 0
        loop = True
        if max_retries == retries:
            loop = False
        while loop:
            try:
                if text:
                    payload = {"from": from_number,
                               "to": number,
                               "Msg": f"Defense Alert: {body}"}

                    general_phlo.run(**payload)
                if phone:
                    payload = {"from": from_number,
                               "to": number,
                               "Msg": f"Defense Alert: {body}"}

                    voice_phlo.run(**payload)
                loop = False
            except Exception as e:
                print(e)
                retries += 1
