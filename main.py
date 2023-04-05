import re
import dotenv
import os
from twitchio.ext import commands

dotenv.load_dotenv(override=True)

check_str = re.compile("attend.*")


def webhook(message: str):
    # send a message to discord webhook.
    # webhook url is in the environment.

    import requests

    url = os.environ.get("WEBHOOK_URL")
    data = {"content": message}
    r = requests.post(
        url, json=data, headers={"Content-Type": "application/json"}, timeout=15
    )
    # print(r, r.status_code, r.text)
    print(message)


def get_stream(channel_name: str) -> bool | int:
    # if stream is offline, return false
    import requests

    url = f"https://api.twitch.tv/helix/streams?user_login={channel_name}"
    headers = {
        "Client-ID": os.environ["CLIENT_ID"],
        "Authorization": "Bearer " + os.environ["ACCESS_TOKEN"],
    }
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        if r.json()["data"]:
            # return stream's uptime in seconds
            t = r.json()["data"][0][
                "started_at"
            ]  # The UTC date and time (in RFC3339 format) of when the broadcast began.
            import datetime
            import time

            t = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")
            t = time.mktime(t.timetuple())
            return int(time.time() - t)
        else:
            return False
    else:
        print(r.status_code)
        return False


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.environ["ACCESS_TOKEN"], prefix="?", initial_channels=["solfibot"]
        )
        self.had_i_checked = False
        self.i_said = False

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

    # when a message is sent
    async def event_message(self, message):
        if message.author.name == "bbangddeock":
            if check_str.match(message.content):
                print("stream online and checked")
                webhook(f"{message.author.name} 님이 출석하셨어요!")
                self.had_i_checked = True
                return
        is_online = get_stream("ppo_yame")
        # if stream is offline
        if is_online is False:
            print("stream offline")
            self.had_i_checked = False
            return

        if self.i_said:
            return

        print(self.i_said)
        # if online
        if is_online > 3600:
            if not self.had_i_checked:
                self.i_said = True
                print("stream online and not checked")
                webhook(f"{message.author.name} 님이 출석하지 않으셨어요!")
            else:
                print("stream online and already checked")


bot = Bot()
bot.run()