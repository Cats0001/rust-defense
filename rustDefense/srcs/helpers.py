import json
import plivo
from discord_webhook import DiscordWebhook, DiscordEmbed

env_data = json.load(open('srcs/env.json', 'r'))

if env_data["enablePhone"]:
    plivo_auth_id = env_data["data"]["plivo"]["auth_id"]
    plivo_auth_token = env_data["data"]["plivo"]["auth_token"]
    group_phlo_id = env_data["data"]["plivo"]["group_phlo"]

    phlo_client = plivo.phlo.RestClient(auth_id=plivo_auth_id, auth_token=plivo_auth_token)
    general_phlo = phlo_client.phlo.get(group_phlo_id)

    voice_phlo_id = env_data["data"]["plivo"]["voice_phlo"]

    voice_phlo = phlo_client.phlo.get(voice_phlo_id)
    from_number = env_data["data"]["plivo"]["number"]


def send_alerts(numbers, body, phone=True, text=True):
    if not env_data["enablePhone"]:
        return

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


class WebhookSender:
    def __init__(self, hook_url):
        if (hook_url is None) or (hook_url.strip() == ''):
            self.enabled = False
        else:
            self.enabled = True
        self.hook_url = hook_url

    def send_event(self, event, priority):
        if self.enabled:
            if event == 'Raid Alarm':
                text = "@everyone"
            else:
                text = ""
            webhook = DiscordWebhook(url=self.hook_url, username="Raid Alarm", content=text)
            embed = DiscordEmbed(title='New Event', description=f'Event Triggered: {event}', color='03b2f8')
            embed.set_footer(text='v1.0')
            embed.set_timestamp()
            embed.add_embed_field(name='Sensor ID', value=priority)

            webhook.add_embed(embed)
            response = webhook.execute()
