from mconduit.utils import color


def test_rgb_to_argb():
    
    assert color.rgb_to_argb(0, 0, 0, 0) == 0
    assert color.rgb_to_argb(10, 204, 55) == -16069577
    

def test_rgb_to_hsv():

    assert color.rgb_to_hsv(10, 204, 55) == (134, 95.1, 80.0)
    assert color.rgb_to_hsv(0, 0, 0) == (0, 0.0, 0.0)
    assert color.rgb_to_hsv(255, 255, 255) == (0, 0.0, 100.0)


def test_hex_to_rgb():

    assert color.hex_to_rgb("#0acc37") == (10, 204, 55)
    assert color.hex_to_rgb("0acc37") == (10, 204, 55)


def test_rgb_to_hex():

    assert color.rgb_to_hex(10, 204, 55) == "#0acc37"
    assert color.rgb_to_hex(0, 0, 0) == "#000000"