import threading
import data_collecter.data_collecter as data_collecter
import cassiopeia as cass

class collecterThread (threading.Thread):
    def __init__(self, threadID, initial_summoner_name, region):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.initial_summoner_name = initial_summoner_name
        self.region = region

    def run(self):
        data_collecter.collect_matches(self.initial_summoner_name, self.region)



if __name__ == "__main__":
    #cass.set_riot_api_key("")  # This overrides the value set in your configuration/settings.
    cass.apply_settings("setting.json")
    #cass.set_default_region("JP")
    # data_collecter.collect_matches("Hide on Bush", "KR")
    threadJP = collecterThread(1, "夜空の三日月", "JP")
    threadKR = collecterThread(2, "Hide on Bush", "KR")

    threadJP.start()
    threadKR.start()