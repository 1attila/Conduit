"""
Runs Conduit
"""

from Conduit import build_handler, Context, Text, Color
import time

handler = build_handler()

server1 = handler.servers[0]


@server1.on_player_join
def say_hello(ctx: Context):

    time.sleep(10)
    ctx.say(f"Hello {ctx.player}!", "Conduit")
    print("Joined!")


@server1.on_player_left
def say_bye(ctx: Context):
    print(f"bye!")


@server1.event
def on_player_message(ctx: Context):
    ctx.reply(
        Text.Text("True").green().underlined().hover(Text.HoverAction.ShowText, "!!") + Text.Text(
        "False", Color.Red, Text.Style.Underlined)
    )


@server1.event
def on_player_death(ctx: Context):
    print(f"{ctx.player}")
    ctx.say("Oh no!")


@server1.event
def on_player_command(ctx: Context):
    ctx.reply(Text.red(f"Hello, {ctx.player}!"))