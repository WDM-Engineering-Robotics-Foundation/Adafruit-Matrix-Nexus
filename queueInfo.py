#!/usr/bin/env python
# Show Nexus Queueing Info
# imports
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import requests
import datetime
import sys
import threading
# nexus variables
event_key = "demo5314"
api_key = "INSERT_API_KEY"
url = "https://frc.nexus/api/v1/event/" + event_key
headers = {"Nexus-Api-Key": api_key}
response = requests.get(url, headers=headers) 
data = response.json()

def get_app_updates():
        response = requests.get(url, headers=headers) 
        data = response.json()
        time.sleep(30)

update_thread = threading.Thread(target=get_app_updates,daemon=True)
update_thread.start()

my_team_number = "2000"
my_matches = filter(lambda m: my_team_number in m.get('redTeams', []) + m.get('blueTeams', []), data['matches'])
my_next_match = next(filter(lambda m: not m['status'] == 'On field', my_matches), None)

if not response.ok:
    error_message

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
                estimated_queue_time = my_next_match['times'].get('estimatedQueueTime',None)
                #if estimated_queue_time:
                #    queue_time = "We will be queued at ~{}".format(datetime.datetime.fromtimestamp(estimated_queue_time / 1000))
                #    line3 = graphics.DrawText(offscreen_canvas, font, pos, 20, textColor, queue_time)
            else:
                no_queue = f"No future matches"
                line1 = graphics.DrawText(offscreen_canvas,font,pos,7,textColor, no_queue)
                line2 = graphics.DrawText(offscreen_canvas,font,pos,15,textColor,"scheduled yet.")
            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
