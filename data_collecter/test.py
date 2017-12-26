import threading
import cassiopeia as cass
import time
import random


class testThread(threading.Thread):
    def __init__(self, threadID, initial_summoner_name, region):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.initial_summoner_name = initial_summoner_name
        self.region = region

    def run(self):
        test = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for i in range(10,100):
            test.append(i)
            print(self.region + str(test))
            file = open("test.txt", "a")
            for id in test:
                file.write(str(id) + '' + self.region + '\n')
            test = []
            print(self.region + "sleep")
            time.sleep(random.randint(1,2))


if __name__ == "__main__":
    # cass.set_riot_api_key("")  # This overrides the value set in your configuration/settings.
    cass.apply_settings("setting.json")
    # cass.set_default_region("JP")
    # data_collecter.collect_matches("Hide on Bush", "KR")


    threadJP = testThread(1, "夜空の三日月", "JP")
    threadKR = testThread(2, "Hide on Bush", "KR")
    threadJP.start()
    threadKR.start()