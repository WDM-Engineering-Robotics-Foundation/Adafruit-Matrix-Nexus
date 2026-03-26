#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
import threading
import time
import datetime
import math
from threading import Lock
from flask import Flask, request

my_team_number = "6419"

app = Flask(__name__)

class MatchData:
    def __init__(self, data=None):
        self.__next_match = None
        self.__lock = Lock()
        if data:
            self.update(data)

    def update(self, data):
        with self.__lock:
            matches = list(filter(lambda m: my_team_number in m.get('redTeams', []) + m.get('blueTeams', []), data.get('matches', [])))
            
            self.__next_match = next((m for m in matches if m['status'] != 'On field' and m['status'] != 'Completed'), None)
            if self.__next_match:
                self.__time_estimate = self.__next_match['times'].get('estimatedQueueTime', None)
            print(f"Data Updated! Next Match: {self.__next_match['label'] if self.__next_match else 'None'}")

    def next_match(self):
         return self.__next_match
    def time_estimate(self):
        return self.__time_estimate

    def get_lock(self):
        return self.__lock

current_data = None 

@app.route('/', methods=['POST'])
def nexus_webhook():
    global current_data
    json_data = request.json
    if current_data is None:
        current_data = MatchData(json_data)
    else:
        current_data.update(json_data)
    return "OK", 200

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../fonts/6x10.bdf")
        
        white = graphics.Color(255, 255, 255)
        blue = graphics.Color(0, 0, 255)
        red = graphics.Color(255, 0, 0)
        
        pos = 128
        
        while True:
            with current_data.get_lock():
                offscreen_canvas.Clear()
                my_next_match = current_data.next_match()

                if my_next_match:
                    alliance_color = 'red' if my_team_number in my_next_match.get('redTeams', []) else 'blue'
                    color = red if alliance_color == 'red' else blue

                    minute_estimate = math.floor(((current_data.time_estimate() / 1000) - time.time())/60)
                    
                    graphics.DrawText(offscreen_canvas, font, pos, 7, color, f"Next: {my_next_match['label']}")
                    graphics.DrawText(offscreen_canvas, font, pos, 15, white, f"Status: {my_next_match['status']}")
                    graphics.DrawText(offscreen_canvas, font, pos, 23, color, f"Bumper: {alliance_color.upper()}")
                    if minute_estimate > 0:
                        graphics.DrawText(offscreen_canvas, font, pos, 31, white, f"Queueing in ~{minute_estimate} mins")
                else:
                    graphics.DrawText(offscreen_canvas, font, pos, 7, white, "Waiting for Match...")

                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                time.sleep(0.1)

def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    webhook_thread = threading.Thread(target=start_flask, daemon=True)
    webhook_thread.start()

    while current_data is None:
        print("Waiting for first Webhook from Nexus/ngrok...")
        time.sleep(1)
    run_text = RunText()
    if not run_text.process():
        run_text.print_help()
