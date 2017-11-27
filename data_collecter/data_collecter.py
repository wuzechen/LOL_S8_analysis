import random
from sortedcontainers import SortedList
import datetime
import cassiopeia as cass
from cassiopeia.core import Summoner, MatchHistory, Match, Patch
from cassiopeia.data import Queue
import csv

def filter_match_history(summoner, patch):
    end_time = patch.end
    if end_time is None:
        end_time = datetime.datetime.now()
    match_history = MatchHistory(summoner=summoner, region=summoner.region, queues={Queue.ranked_solo_fives}, begin_time=patch.start, end_time=end_time)
    return match_history

def collect_matches():
    initial_summoner_name = "夜空の三日月"
    region = "JP"

    summoner = Summoner(name=initial_summoner_name, region=region)
    patch_722 = Patch.from_str("7.22", region=region)

    unpulled_summoner_ids = SortedList([summoner.id])
    pulled_summoner_ids = SortedList()

    unpulled_match_ids = SortedList()
    pulled_match_ids = SortedList()

    headers = ["match_id", "creation", "duration", "patch", "region", "game_type", "win",
               "red_win", "red_baron_kills", "red_dragon_kills", "red_rift_herald_kills", "red_rift_herald_kills",
               "red_inhibitor_kills", "red_tower_kills", "red_first_baron", "red_first_dragon", "red_first_blood",
               "red_first_inhibitor", "red_first_tower", "red_dominion_score",
               "blue_win", "blue_baron_kills", "blue_dragon_kills", "blue_rift_herald_kills", "blue_rift_herald_kills",
               "blue_inhibitor_kills", "blue_tower_kills", "blue_first_baron", "blue_first_dragon", "blue_first_blood",
               "blue_first_inhibitor", "blue_first_tower", "blue_dominion_score",
               "red_ban0", "red_ban1", "red_ban2", "red_ban3", "red_ban4",
               "blue_ban0", "blue_ban1", "blue_ban2", "blue_ban3", "blue_ban4"]

    while unpulled_summoner_ids:
        # Get a random summoner from our list of unpulled summoners and pull their match history
        new_summoner_id = random.choice(unpulled_summoner_ids)
        new_summoner = Summoner(id=new_summoner_id, region=region)
        matches = filter_match_history(new_summoner, patch_722)
        unpulled_match_ids.update([match.id for match in matches])
        unpulled_summoner_ids.remove(new_summoner_id)
        pulled_summoner_ids.add(new_summoner_id)

        while unpulled_match_ids:
            # Get a random match from our list of matches
            new_match_id = random.choice(unpulled_match_ids)
            new_match = Match(id=new_match_id, region=region)
            blue = new_match.blue_team
            red = new_match.red_team
            data = {"match_id": new_match_id,
                    "creation": new_match.creation,
                    "duration": new_match.duration.seconds,
                    "patch": new_match.patch,
                    "region": new_match.region,
                    "game_type": new_match.queue,
                    "win": red.win and "red" or "blue",
                    "red_win": red.win,
                    "red_baron_kills": red.baron_kills,
                    "red_dragon_kills": red.dragon_kills,
                    "red_rift_herald_kills": red.rift_herald_kills,
                    "red_inhibitor_kills": red.inhibitor_kills,
                    "red_tower_kills": red.tower_kills,
                    "red_first_baron": red.first_baron,
                    "red_first_dragon": red.first_dragon,
                    "red_first_blood": red.first_blood,
                    "red_first_inhibitor": red.first_inhibitor,
                    "red_first_tower":red.first_tower,
                    "red_dominion_score": red.dominion_score,
                    "blue_win": blue.win,
                    "blue_baron_kills": blue.baron_kills,
                    "blue_dragon_kills": blue.dragon_kills,
                    "blue_rift_herald_kills": blue.rift_herald_kills,
                    "blue_inhibitor_kills": blue.inhibitor_kills,
                    "blue_tower_kills": blue.tower_kills,
                    "blue_first_baron": blue.first_baron,
                    "blue_first_dragon": blue.first_dragon,
                    "blue_first_blood": blue.first_blood,
                    "blue_first_inhibitor": blue.first_inhibitor,
                    "blue_first_tower": blue.first_tower,
                    "blue_dominion_score": blue.dominion_score}
            for index in range(len(red.bans)):
                data["red_ban" + str(index)] = red.bans[index] is not None and red.bans[index].id or "null"
            for index in range(len(blue.bans)):
                data["blue_ban" + str(index)] = blue.bans[index] is not None and blue.bans[index].id or "null"
            #for index, participant in enumerate(new_match.participants):

            # find next player
            for participant in new_match.participants:
                if participant.summoner.id not in pulled_summoner_ids and participant.summoner.id not in unpulled_summoner_ids:
                    unpulled_summoner_ids.add(participant.summoner.id)
            unpulled_match_ids.remove(new_match_id)
            pulled_match_ids.add(new_match_id)

            # Write the data to the csv file
            datas = [data]
            with open("./../data/match_data.csv", "a", newline="") as f:
                writer = csv.DictWriter(f, headers)
                for row in datas:
                    writer.writerow(row)

if __name__ == "__main__":
    #cass.set_riot_api_key("")  # This overrides the value set in your configuration/settings.
    cass.apply_settings("setting.json")
    #cass.set_default_region("JP")
    collect_matches()