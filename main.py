from time import sleep
from re import compile, sub
from os import getenv

from feedparser import parse
from discord_webhook import DiscordWebhook, DiscordEmbed
from tinydb import TinyDB, Query

clean_html = compile("<.*?>")


def cleanhtml(raw_html):
    """
    Remove HTML tags
    """
    cleantext = sub(clean_html, "", raw_html)
    return cleantext


if __name__ == "__main__":

    db = TinyDB("zines.json")
    zines = Query()

    for entry in parse("https://zine.wilderworld.com/rss/").entries:

        if db.search(zines.id == entry["id"]):
            print("already sent zine")
            continue

        webhook = DiscordWebhook(url=getenv("WEBHOOK_URL"))

        # create embed object for webhook
        embed = DiscordEmbed(
            title=entry.get("title", "New Post"),
            url=entry.get("link", "wilderworld.com"),
            description=cleanhtml(entry.get("summary", "New Post")),
            color="03b2f8",
        )

        # set author
        embed.set_author(
            name=entry.get("author", "wilderworld.com"),
            url="https://zine.wilderworld.com",
            icon_url="https://icodrops.com/wp-content/uploads/2021/04/WilderWorld_logo.jpeg",
        )

        # set image
        try:
            embed.set_image(url=entry.get("media_content").pop().get("url"))
        except IndexError:
            print("no image")
            pass

        # set timestamp (default is now)
        embed.set_timestamp()

        # add embed object to webhook
        webhook.add_embed(embed)

        response = webhook.execute()

        if response.status_code == 200:
            db.insert({"id": entry["id"]})
            print("sent " + entry["id"])

        sleep(5)
