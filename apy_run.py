from typing import Tuple
import math
import json



def get_apy(verbose: bool = False) -> Tuple[int]:
    """
    Fetch apy from the DefiLlama API
    """
    import requests
    import time

    url = 'https://yields.llama.fi/chart/9acfbce9-ea0f-4718-ba7a-123b57554399'
    headers = {'accept': '/'}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if verbose:
            print("200 OK")
        data = json.loads(response.text)
        apy = data["data"][-1]["apy"]
    else:
        if verbose:
            print(response.status_code)
        time.sleep(10)

    return round(apy,2)


def main(verbose=False):
    import yaml
    import discord
    import asyncio

    # 1. Load config
    filename = "APY_Bot/apy_config.yaml"
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.Loader)

    # 2. Connect w the bot
    client = discord.Client(intents=discord.Intents.default())

    async def send_update(apy):
        nickname = f"APY: {apy}%"
        status = "24h"
        await client.get_guild(config["guildId"]).me.edit(nick=nickname)
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=status)
        )
        await asyncio.sleep(config["updateFreq"])  # in seconds

    @client.event
    async def on_ready():
        """
        When discord client is ready
        """
        while True:
            apy = get_apy(verbose)
            # 4. Feed it to the bot
            await send_update(apy)

    client.run(config["discordBotKey"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",  # equiv. default is False
        help="toggle verbose",
    )
    args = parser.parse_args()
    main(verbose=args.verbose)