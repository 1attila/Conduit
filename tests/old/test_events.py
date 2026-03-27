from mconduit import build_handler, Context, Server, Handler


def main():
    
    handler = build_handler()


    @handler.on_player_command
    def on_command(ctx: Context):
        print("Player command")

    @handler.on_player_message
    def on_message(ctx: Context):
        print("Player message")

    @handler.on_player_join
    def on_join(ctx: Context):
        print("Player join")

    @handler.on_player_left
    def on_left(ctx: Context):
        print("Player left")

    @handler.on_player_death
    def on_death(ctx: Context):
        print("Player death")

    @handler.on_conduit_start
    def on_cstart(ctx: Handler):
        print("Conduit start")

    @handler.on_conduit_stop
    def on_cstop(ctx: Handler):
        print("Conduit stop")
    
    @handler.on_server_start
    def on_sstart(ctx: Server):
        print("Server start")

    @handler.on_server_stop
    def on_sstop(ctx: Server):
        print("Server stop")


if __name__ == "__main__":
    main()