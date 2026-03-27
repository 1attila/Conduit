from mconduit import build_handler, Context, __version__


def main():

    handler = build_handler()

    @handler.on_player_command
    def here(ctx: Context):

        if ctx.command.removeprefix("!!").strip() == "here":
            ctx.say(f"{ctx.player} is at {ctx.player.pos} in {ctx.player.dimension}", "")

    
    @handler.on_player_command
    def help(ctx: Context):

        if ctx.command.removeprefix("!!").strip() == "help":
            ctx.reply(f"Conduit v-{__version__.__version__}")