from mconduit import build_handler, Context, Vec3d, text
from mconduit.utils.color import rgb_to_argb

from PIL import Image
from io import BytesIO
import numpy as np
import requests
import time


CANVAS_HEIGTH = 100
CANVAS_WIDTH = 100


def main():

    handler = build_handler()

    @handler.on_player_command
    def app(ctx: Context):
        
        if ctx.command.replace("!!", "").strip() != "app":
            return

        coords = ctx.player.pos + ctx.player.forward_vec * 3
        coords = coords.round()
        
        print(f"/setblock {coords} minecraft:diamond_block")
        ctx.server.execute(f"/setblock {coords} minecraft:diamond_block")


    @handler.on_player_command
    def pic(ctx: Context):
        
        command = ctx.command.replace("!!", "").strip()

        if not command.__contains__("pic"):
            return
        
        image_url = command.replace("pic", "").strip()

        if len(image_url) == 0:
            return
        
        ctx.reply(text.yellow("Fetching the image..."))
        
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        ctx.reply(text.green("Starting displaying..."))

        if image.mode != "RGB":
            image = image.convert("RGB")

        image = image.resize((CANVAS_HEIGTH, CANVAS_WIDTH))
        image_arr = np.array(image)
        image_arr = np.rot90(image_arr, k=-1)

        corner_pos = ctx.player.pos + Vec3d(1, 1, 1)
        ctx.server.execute("/kill @e[type=text_display]")

        print("Starting...")

        t0 = time.perf_counter()
        
        with ctx.server.all_at_once():
            for y in range(CANVAS_HEIGTH):
                for x in range(CANVAS_WIDTH):

                    pos = corner_pos + Vec3d(x * .02, y * .02, 0)
                    color = rgb_to_argb(*map(int, image_arr[x, y]))

                    ctx.server.execute(
                        f"/summon text_display {pos.x} {pos.y} {pos.z} {{background:{color}}}"
                    )
        
        print("Done! Took", time.perf_counter() - t0, "seconds")


if __name__ == "__main__":
    main()