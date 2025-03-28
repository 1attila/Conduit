from conduit import build_handler, Context, text, Color


def main():

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
            text.Text("True").green().underlined().hover(text.HoverAction.ShowText, "!!") + text.Text(
            "False", Color.Red, text.Style.Underlined)
        )


    @handler.event
    def on_player_death(ctx: Context):
        print(f"{ctx.player}")
        ctx.say("Oh no!")


    @handler.event
    def on_player_command(ctx: Context):
        ctx.reply(text.red(f"Hello, {ctx.player}!"))