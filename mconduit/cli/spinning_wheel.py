"""
Same as prompt_toolkit's SpinningWheel but with a different animation
"""

from prompt_toolkit.shortcuts import ProgressBar, ProgressBarCounter
from prompt_toolkit.formatted_text import HTML, AnyFormattedText
from prompt_toolkit.shortcuts.progress_bar.formatters import Formatter
from prompt_toolkit.layout.dimension import D, AnyDimension
import time


class SpinningWheel(Formatter):
    """
    Display a spinning wheel.
    """

    template = HTML("<spinning-wheel>{0}</spinning-wheel>")
    characters = r"⡀⡁⡂⡃⡄⡅⡆⡇⡈⡉⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿"

    def format(
        self,
        progress_bar: ProgressBar,
        progress: ProgressBarCounter[object],
        width: int,
    ) -> AnyFormattedText:
        
        index = int(time.time() * 3) % len(self.characters)
        
        return self.template.format(self.characters[index])
    

    def get_width(self, progress_bar: ProgressBar) -> AnyDimension:
        return D.exact(1)