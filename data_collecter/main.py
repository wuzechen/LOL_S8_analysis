import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
from data_collecter import collecter
import cassiopeia as cass

class collecterThread (threading.Thread):
    def __init__(self, threadID, initial_summoner_name, region, patch):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.initial_summoner_name = initial_summoner_name
        self.region = region
        self.patch = patch

    def run(self):
        print("crate thread {0}".format(self.region))
        while True:
            collecter.collect_matches(self.initial_summoner_name, self.region, self.patch)



if __name__ == "__main__":
    #cass.set_riot_api_key("")  # This overrides the value set in your configuration/settings.
    cass.apply_settings("setting.json")
    #cass.set_default_region("JP")
    # data_collecter.collect_matches("Hide on Bush", "KR")
    threadJP = collecterThread(1, "夜空の三日月", "JP", "7.22")
    threadKR = collecterThread(2, "Hide on Bush", "KR", "7.22")
    threadNA = collecterThread(3, "Søren Bjerg", "NA", "7.22")
    threadEU = collecterThread(4, "FNC Rekkles", "EUW", "7.22")

    threadJP.start()
    threadKR.start()
    threadNA.start()
    threadEU.start()