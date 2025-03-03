"""
Runs Conduit
"""

from conduit import build_handler, Context, Text, Color


handler = build_handler()


@handler.on_player_join
def say_hello(ctx: Context):

    ctx.reply(f"Hello {ctx.player}!")
    print("Joined!")


@handler.on_player_left
def say_bye(ctx: Context):
    print(f"bye!")


@handler.event
def on_player_message(ctx: Context):
    ctx.reply(
        Text.Text("True").green().underlined().hover(Text.HoverAction.ShowText, "!!") + Text.Text(
        "False", Color.Red, Text.Style.Underlined)
    )


@handler.event
def on_player_death(ctx: Context):
    print(f"{ctx.player}")
    ctx.say("Oh no!")


@handler.event
def on_player_command(ctx: Context):
    ctx.reply(Text.red(f"Hello, {ctx.player}!"))