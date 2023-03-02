from typing import Tuple
import math
import json



def get_tvl(verbose: bool = False) -> Tuple[int]:
    """
    Fetch tvl from the DefiLlama API
    """
    import requests
    import time

    url = "https://api.llama.fi/tvl/spice-finance"
    headers = {"accept": "/"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if verbose:
            print("200 OK")
        tvl = response.text.split("\n")[0]
    else:
        if verbose:
            print(response.status_code)
        time.sleep(10)

    url2 = "https://coins.llama.fi/prices/current/coingecko:ethereum?searchWidth=4h"
    headers2 = {"accept": "application/json"}
    response = requests.get(url2, headers=headers2)
    if response.status_code == 200:
        if verbose:
            print("200 OK")
        data = json.loads(response.text)
        eth = data["coins"]["coingecko:ethereum"]["price"]
    else:
        if verbose:
            print(response.status_code)
        time.sleep(10)

    tvl = round(float(tvl) / float(eth),1)
    return tvl


def main(verbose=False):
    import yaml
    import discord
    import asyncio

    # 1. Load config
    filename = "TVL_Bot/tvl_config.yaml"
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.Loader)

    # 2. Connect w the bot
    client = discord.Client(intents=discord.Intents.default())

    async def send_update(tvl):
        nickname = f"PRLG TVL: Ξ{tvl}"
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
            tvl = get_tvl(verbose)
            # 4. Feed it to the bot
            await send_update(tvl)

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