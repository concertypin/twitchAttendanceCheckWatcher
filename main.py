import os
import datetime
import time
import requests

import dotenv
from twitchio.ext import commands

dotenv.load_dotenv(override=True)

check_str = __import__("re").compile(
    os.environ["NICKNAME"] + r"---> 이 채널의 \n번째 출석체크입니다\..*"
)


def webhook(message: str):
    # send a message to discord webhook.
    # webhook url is in the environment.
    url = os.environ.get("WEBHOOK_URL")
    data = {"content": message}
    response = requests.post(
        url, json=data, headers={"Content-Type": "application/json"}, timeout=15
    )
    print(message)


def get_stream(channel_name: str) -> bool | int:
    # if stream is offline, return false
    url = f"https://api.twitch.tv/helix/streams?user_login={channel_name}"
    headers = {
        "Client-ID": os.environ["CLIENT_ID"],
        "Authorization": "Bearer " + os.environ["ACCESS_TOKEN"],
    }
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code == 200:
        if response.json()["data"]:
            # return stream's uptime in seconds
            uptime = response.json()["data"][0][
                "started_at"
            ]  # The UTC date and time (in RFC3339 format) of when the broadcast began.
            uptime = datetime.datetime.strptime(uptime, "%Y-%m-%dT%H:%M:%SZ")
            uptime = time.mktime(uptime.timetuple())
            return int(time.time() - uptime)
        else:
            return False
    else:
        print(response.status_code)
        return False


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.environ["ACCESS_TOKEN"],
            prefix="?",
            initial_channels=[os.environ["CHANNEL"]],
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
        is_online = get_stream(os.environ["CHANNEL"])
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
