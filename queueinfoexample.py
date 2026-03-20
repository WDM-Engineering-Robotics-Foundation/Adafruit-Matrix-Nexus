#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
import threading
import time
from threading import Lock

import requests

event_key = "YOUR_EVENT"
api_key = "YOUR_API_KEY"
url = "https://frc.nexus/api/v1/event/" + event_key
session = requests.Session()
headers = {"Nexus-Api-Key": api_key}

my_team_number = "2000"


# stores info about current match
class MatchData:
    __matches = None
    __next_match = None
    __lock = Lock()

    def __init__(self, data):
        self.update(data)

    def update(self, data):
        self.__lock.acquire()  # start lock
        matches = filter(lambda m: my_team_number in m.get('redTeams', []) + m.get('blueTeams', []), data['matches'])
        next_match = next(filter(lambda m: not m['status'] == 'On field', matches), None)

        self.__matches = matches
        self.__next_match = next_match
        self.__lock.release()  # end lock

    def next_match(self):
        try:
            self.__lock.acquire()
            return self.__next_match
        finally:
            self.__lock.release()

    def matches(self):
        try:
            self.__lock.acquire()
            return self.__matches
        finally:
            self.__lock.release()


current_data: MatchData = None

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to show on the RGB LED panel", default="Hello world!")

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../fonts/6x10.bdf")
        textColor = graphics.Color(255,255,255)
        blue = graphics.Color(0,0,255)
        red = graphics.Color(255,0,0)
        pos = 128
        my_text = self.args.text
        while True:
            # fetch next match data
            global current_data
            my_next_match = current_data.next_match()

            line1 = graphics.DrawText(offscreen_canvas, font, pos, 7, textColor, "Next match")
            line2 = graphics.DrawText(offscreen_canvas, font, pos, 15, textColor, "Match")
            line3 = graphics.DrawText(offscreen_canvas, font, pos, 23, textColor, "Status")
            line4 = graphics.DrawText(offscreen_canvas, font, pos, 31, textColor, "Bumpers")

            offscreen_canvas.Clear()
            if my_next_match:
                next_match = f"{my_team_number}'s next match is"
                match_number = f"{my_next_match['label']}!"
                status = f"{my_next_match['status']}"
                alliance_color = 'red' if my_team_number in my_next_match.get('redTeams', []) else 'blue'
                bumpers = f"Put {alliance_color} bumpers on"
                if alliance_color == 'red':
                    line1 = graphics.DrawText(offscreen_canvas, font, pos, 7, red, next_match)
                    line2 = graphics.DrawText(offscreen_canvas, font, pos, 15, textColor, match_number)
                    line3 = graphics.DrawText(offscreen_canvas, font, pos, 23, textColor, status)
                    line4 = graphics.DrawText(offscreen_canvas, font, pos, 31, red, bumpers)
                else:
                    line1 = graphics.DrawText(offscreen_canvas, font, pos, 7, blue, next_match)
                    line2 = graphics.DrawText(offscreen_canvas, font, pos, 15, textColor, match_number)
                    line3 = graphics.DrawText(offscreen_canvas, font, pos, 23, textColor, status)
                    line4 = graphics.DrawText(offscreen_canvas, font, pos, 31, blue, bumpers)

            else:
                no_queue = f"No future matches"
                line1 = graphics.DrawText(offscreen_canvas,font,pos,7,textColor, no_queue)
                line2 = graphics.DrawText(offscreen_canvas,font,pos,15,textColor,"scheduled yet.")
            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


def update_loop():
    while True:
        global current_data
        current_data = MatchData(requests.get(url, headers=headers).json())
        time.sleep(30)


if __name__ == '__main__':
    update_thread = threading.Thread(target=update_loop, daemon=True)
    update_thread.start()

    run_text = RunText()
    if not run_text.process():
        run_text.print_help()
