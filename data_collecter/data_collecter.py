import random
from sortedcontainers import SortedList
import datetime
import cassiopeia as cass
from cassiopeia.core import Summoner, MatchHistory, Match, Patch
from cassiopeia.data import Queue
import csv
import copy
import json
import init.csv_header as csv_header
import init.init_history as init
import init.log_history as log

def filter_match_history(summoner, patch):
    end_time = datetime.datetime.now()
    match_history = MatchHistory(summoner=summoner, region=summoner.region,
                                 queues={Queue.ranked_solo_fives}, begin_time=patch.start, end_time=end_time)
    return match_history

def get_role(role_string):
    if role_string == "Lane.top_laneSOLO":
        role = "top"
    elif role_string == "Lane.jungleNone":
        role = "jug"
    elif role_string == "Lane.mid_laneSOLO":
        role = "mid"
    elif role_string == "Lane.bot_laneRole.adc":
        role = "adc"
    elif role_string == "Lane.bot_laneRole.support":
        role = "sup"
    else:
        role = "null"
    return role

def collect_matches(initial_summoner_name, region, patch):
    summoner = Summoner(name=initial_summoner_name, region=region)
    patch_722 = Patch.from_str(patch, region=region)

    unpulled_summoner_ids = init.unpulled_summoner_ids(region)
    if len(unpulled_summoner_ids) == 0:
        unpulled_summoner_ids.add(summoner.id)
    pulled_summoner_ids = init.pulled_summoner_ids(region)

    unpulled_match_ids = init.unpulled_match_ids(region)
    pulled_match_ids = init.unpulled_match_ids(region)

    count = 0
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
            blue = getattr(new_match, "blue_team", None)
            red = getattr(new_match, "red_team", None)
            if blue is None or red is None:
                continue
            match_data = {
                    "match_id": new_match_id,
                    "creation": getattr(new_match, "creation", None).strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": getattr(new_match.duration, "seconds", 0),
                    "patch": getattr(new_match, "patch", patch),
                    "region": getattr(new_match, "region", region),
                    "game_type": getattr(new_match, "queue", "Queue.depreciated_ranked_solo_fives"),
                    "win": getattr(red, "win", False) and "red" or "blue",
                    "red_win": str(getattr(red, "win", False)).lower(),
                    "red_baron_kills": getattr(red, "baron_kills", 0),
                    "red_dragon_kills": getattr(red, "dragon_kills", 0),
                    "red_rift_herald_kills": getattr(red, "rift_herald_kills", 0),
                    "red_inhibitor_kills": getattr(red, "inhibitor_kills", 0),
                    "red_tower_kills": getattr(red, "tower_kills", 0),
                    "red_first_baron": str(getattr(red, "first_baron", False)).lower(),
                    "red_first_dragon": str(getattr(red, "first_dragon", False)).lower(),
                    "red_first_blood": str(getattr(red, "first_blood", False)).lower(),
                    "red_first_inhibitor": str(getattr(red, "first_inhibitor", False)).lower(),
                    "red_first_tower": str(getattr(red, "first_tower", False)).lower(),
                    "red_dominion_score": getattr(red, "dominion_score", 0),
                    "blue_win": str(getattr(blue, "win", False)).lower(),
                    "blue_baron_kills": getattr(blue, "baron_kills", 0),
                    "blue_dragon_kills": getattr(blue, "dragon_kills", 0),
                    "blue_rift_herald_kills": getattr(blue, "rift_herald_kills", 0),
                    "blue_inhibitor_kills": getattr(blue, "inhibitor_kills", 0),
                    "blue_tower_kills": getattr(blue, "tower_kills", 0),
                    "blue_first_baron": str(getattr(blue, "first_baron", False)).lower(),
                    "blue_first_dragon": str(getattr(blue, "first_dragon", False)).lower(),
                    "blue_first_blood": str(getattr(blue, "first_blood", False)).lower(),
                    "blue_first_inhibitor": str(getattr(blue, "first_inhibitor", False)).lower(),
                    "blue_first_tower": str(getattr(blue, "first_tower", False)).lower(),
                    "blue_dominion_score": getattr(blue, "dominion_score", 0),
                    }
            match_players = []
            match_player_data = {}
            timelines = {}
            timeline_data = {}
            for index in range(len(red.bans)):
                match_data["red_ban" + str(index)] = red.bans[index] is not None and red.bans[index].id or -1
            for index in range(len(blue.bans)):
                match_data["blue_ban" + str(index)] = blue.bans[index] is not None and blue.bans[index].id or -1

            # match_player_data
            for participant in red.participants:
                role = get_role(str(getattr(participant, "lane", "null")) + str(getattr(participant, "role", "null")))
                if role == "null":
                    continue
                match_player_data = {"match_id": new_match_id ,"role": role, "side": "red"}
                match_player_data["pick"] = \
                    getattr(participant.champion, "id", -1)
                match_player_data["player_id"] = \
                    getattr(participant.summoner, "id", -1)
                match_player_data["level"] = \
                    getattr(participant, "rank_last_season", 0)
                match_player_data["summoner_spell_d"] =\
                    getattr(participant.summoner_spell_d, "id", -1)
                match_player_data["summoner_spell_f"] = \
                    getattr(participant.summoner_spell_f, "id", -1)
                match_player_data["kill"] = \
                    getattr(participant.stats, "kills", 0)
                match_player_data["deaths"] = \
                    getattr(participant.stats, "deaths", 0)
                match_player_data["assists"] = \
                    getattr(participant.stats, "assists", 0)
                match_player_data["gold_earned"] = \
                    getattr(participant.stats, "gold_earned", 0)
                match_player_data["gold_spent"] = \
                    getattr(participant.stats, "gold_spent", 0)
                match_player_data["kda"] = \
                    getattr(participant.stats, "kda", 0)
                match_player_data["level"] = \
                    getattr(participant.stats, "level", 0)
                match_player_data["total_minions_killed"] = \
                    getattr(participant.stats, "total_minions_killed", 0)
                match_player_data["turret_kills"] = \
                    getattr(participant.stats, "turret_kills", 0)
                match_player_data["inhibitor_kills"] = \
                    getattr(participant.stats, "inhibitor_kills", 0)
                match_player_data["killing_sprees"] = \
                    getattr(participant.stats, "killing_sprees", 0)
                match_player_data["double_kills"] = \
                    getattr(participant.stats, "double_kills", 0)
                match_player_data["triple_kills"] = \
                    getattr(participant.stats, "triple_kills", 0)
                match_player_data["quadra_kills"] = \
                    getattr(participant.stats, "quadra_kills", 0)
                match_player_data["panta_kills"] = \
                    getattr(participant.stats, "penta_kills", 0)
                match_player_data["first_blood_assist"] = \
                    str(getattr(participant.stats, "first_blood_assist", False)).lower()
                match_player_data["first_blood_kill"] = \
                    str(getattr(participant.stats, "first_blood_kill", False)).lower()
                match_player_data["first_inhibitor_assist"] = \
                    str(getattr(participant.stats, "first_inhibitor_assist", False)).lower()
                match_player_data["first_inhibitor_kill"] = \
                    str(getattr(participant.stats, "first_inhibitor_kill", False)).lower()
                match_player_data["first_tower_assist"] = \
                    str(getattr(participant.stats, "first_tower_assist", False)).lower()
                match_player_data["first_tower_kill"] = \
                    str(getattr(participant.stats, "first_tower_kill", False)).lower()
                match_player_data["vision_score"] = \
                    getattr(participant.stats, "vision_score", 0)
                match_player_data["vision_wards_bought_in_game"] = \
                    getattr(participant.stats, "vision_wards_bought_in_game", 0)
                match_player_data["sight_wards_bought_in_game"] = \
                    getattr(participant.stats, "sight_wards_bought_in_game", 0)
                match_player_data["wards_killed"] = \
                    getattr(participant.stats, "wards_killed", 0)
                match_player_data["wards_placed"] = \
                    getattr(participant.stats, "wards_placed", 0)
                match_player_data["total_time_crowd_control_dealt"] = \
                    getattr(participant.stats, "total_time_crowd_control_dealt", 0)
                match_player_data["total_damage_dealt"] = \
                    getattr(participant.stats, "total_damage_dealt", 0)
                match_player_data["total_damage_dealt_to_champions"] = \
                    getattr(participant.stats, "total_damage_dealt_to_champions", 0)
                match_player_data["total_damage_taken"] = \
                    getattr(participant.stats, "total_damage_taken", 0)
                match_player_data["total_heal"] = \
                    getattr(participant.stats, "total_heal", 0)
                match_player_data["total_units_healed"] = \
                    getattr(participant.stats, "total_units_healed", 0)
                match_player_data["longest_time_spent_living"] = \
                    getattr(participant.stats, "longest_time_spent_living", 0)
                match_player_data["neutral_minions_killed"] =\
                    getattr(participant.stats, "neutral_minions_killed", 0)
                match_player_data["neutral_minions_killed_enemy_jungle"] = \
                    getattr(participant.stats, "neutral_minions_killed_enemy_jungle", 0)
                match_player_data["neutral_minions_killed_team_jungle"] = \
                    getattr(participant.stats, "neutral_minions_killed_team_jungle", 0)
                match_player_data["damage_dealt_to_objectives"] = \
                    getattr(participant.stats, "damage_dealt_to_objectives", 0)
                match_player_data["damage_dealt_to_turrets"] = \
                    getattr(participant.stats, "damage_dealt_to_turrets", 0)
                match_player_data["damage_self_mitigated"] = \
                    getattr(participant.stats, "damage_self_mitigated", 0)
                items = getattr(participant.stats, "item", None)
                if items is not None:
                    for index, item in enumerate(items):
                        match_player_data["item" + str(index)] = getattr(item, "id", -1)
                creeps_per_min_deltas = getattr(participant.timeline, "creeps_per_min_deltas", None)
                if creeps_per_min_deltas is not None:
                    match_player_data["creeps_per_min_deltas"] = json.dumps(creeps_per_min_deltas)
                cs_diff_per_min_deltas = getattr(participant.timeline, "cs_diff_per_min_deltas", None)
                if cs_diff_per_min_deltas is not None:
                    match_player_data["cs_diff_per_min_deltas"] = json.dumps(cs_diff_per_min_deltas)
                damage_taken_diff_per_min_deltas = getattr(participant.timeline, "damage_taken_diff_per_min_deltas", None)
                if damage_taken_diff_per_min_deltas is not None:
                    match_player_data["damage_taken_diff_per_min_deltas"] = json.dumps(damage_taken_diff_per_min_deltas)
                damage_taken_per_min_deltas = getattr(participant.timeline, "damage_taken_per_min_deltas",None)
                if damage_taken_per_min_deltas is not None:
                    match_player_data["damage_taken_per_min_deltas"] = json.dumps(damage_taken_per_min_deltas)
                gold_per_min_deltas = getattr(participant.timeline, "gold_per_min_deltas", None)
                if gold_per_min_deltas is not None:
                    match_player_data["gold_per_min_deltas"] = json.dumps(gold_per_min_deltas)
                xp_per_min_deltas = getattr(participant.timeline, "xp_per_min_deltas", None)
                if xp_per_min_deltas is not None:
                    match_player_data["xp_per_min_deltas"] = json.dumps(xp_per_min_deltas)
                xp_diff_per_min_deltas = getattr(participant.timeline, "xp_diff_per_min_deltas", None)
                if xp_diff_per_min_deltas is not None:
                    match_player_data["xp_diff_per_min_deltas"] = json.dumps(xp_diff_per_min_deltas)
                # deep copy
                match_players.append(copy.deepcopy(match_player_data))

                # timeline data
                frames = getattr(participant.timeline, "frames", None)
                if frames is not None:
                    for index, frame in enumerate(frames):
                        if frame is None:
                            continue
                        if index in timelines:
                            timeline_data = timelines.get(index)
                        if timeline_data is None:
                            timeline_data = {}
                        timeline_data["match_id"] = new_match_id
                        timeline_data["frame"] = index
                        timeline_data["red_" + role + "_creep_score"] = getattr(frame, "creep_score", 0)
                        timeline_data["red_" + role + "_current_gold"] = getattr(frame, "current_gold", 0)
                        timeline_data["red_" + role + "_gold_earned"] = getattr(frame, "gold_earned", 0)
                        timeline_data["red_" + role + "_level"] = getattr(frame, "level", 0)
                        position = getattr(frame, "position", None)
                        if position is not None:
                            timeline_data["red_" + role + "_positionX"] = position.x
                            timeline_data["red_" + role + "_positionY"] = position.y
                        timelines[index] = copy.deepcopy(timeline_data)
                        timeline_data = {}

            for participant in blue.participants:
                role = get_role(str(getattr(participant, "lane", "null")) + str(getattr(participant, "role", "null")))
                if role == "null":
                    continue
                match_player_data = {"match_id": new_match_id, "role": role, "side": "blue"}
                match_player_data["pick"] = \
                    getattr(participant.champion, "id", -1)
                match_player_data["player_id"] = \
                    getattr(participant.summoner, "id", -1)
                match_player_data["rank"] = \
                    getattr(participant, "rank_last_season", 0)
                match_player_data["summoner_spell_d"] = \
                    getattr(participant.summoner_spell_d, "id", -1)
                match_player_data["summoner_spell_f"] = \
                    getattr(participant.summoner_spell_f, "id", -1)
                match_player_data["kill"] = \
                    getattr(participant.stats, "kills", 0)
                match_player_data["deaths"] = \
                    getattr(participant.stats, "deaths", 0)
                match_player_data["assists"] = \
                    getattr(participant.stats, "assists", 0)
                match_player_data["gold_earned"] = \
                    getattr(participant.stats, "gold_earned", 0)
                match_player_data["gold_spent"] = \
                    getattr(participant.stats, "gold_spent", 0)
                match_player_data["kda"] = \
                    getattr(participant.stats, "kda", 0)
                match_player_data["level"] = \
                    getattr(participant.stats, "level", 0)
                match_player_data["total_minions_killed"] = \
                    getattr(participant.stats, "total_minions_killed", 0)
                match_player_data["turret_kills"] = \
                    getattr(participant.stats, "turret_kills", 0)
                match_player_data["inhibitor_kills"] = \
                    getattr(participant.stats, "inhibitor_kills", 0)
                match_player_data["killing_sprees"] = \
                    getattr(participant.stats, "killing_sprees", 0)
                match_player_data["double_kills"] = \
                    getattr(participant.stats, "double_kills", 0)
                match_player_data["triple_kills"] = \
                    getattr(participant.stats, "triple_kills", 0)
                match_player_data["quadra_kills"] = \
                    getattr(participant.stats, "quadra_kills", 0)
                match_player_data["panta_kills"] = \
                    getattr(participant.stats, "penta_kills", 0)
                match_player_data["first_blood_assist"] = \
                    str(getattr(participant.stats, "first_blood_assist", False)).lower()
                match_player_data["first_blood_kill"] = \
                    str(getattr(participant.stats, "first_blood_kill", False)).lower()
                match_player_data["first_inhibitor_assist"] = \
                    str(getattr(participant.stats, "first_inhibitor_assist", False)).lower()
                match_player_data["first_inhibitor_kill"] = \
                    str(getattr(participant.stats, "first_inhibitor_kill", False)).lower()
                match_player_data["first_tower_assist"] = \
                    str(getattr(participant.stats, "first_tower_assist", False)).lower()
                match_player_data["first_tower_kill"] = \
                    str(getattr(participant.stats, "first_tower_kill", False)).lower()
                match_player_data["vision_score"] = \
                    getattr(participant.stats, "vision_score", 0)
                match_player_data["vision_wards_bought_in_game"] = \
                    getattr(participant.stats, "vision_wards_bought_in_game", 0)
                match_player_data["sight_wards_bought_in_game"] = \
                    getattr(participant.stats, "sight_wards_bought_in_game", 0)
                match_player_data["wards_killed"] = \
                    getattr(participant.stats, "wards_killed", 0)
                match_player_data["wards_placed"] = \
                    getattr(participant.stats, "wards_placed", 0)
                match_player_data["total_time_crowd_control_dealt"] = \
                    getattr(participant.stats, "total_time_crowd_control_dealt", 0)
                match_player_data["total_damage_dealt"] = \
                    getattr(participant.stats, "total_damage_dealt", 0)
                match_player_data["total_damage_dealt_to_champions"] = \
                    getattr(participant.stats, "total_damage_dealt_to_champions", 0)
                match_player_data["total_damage_taken"] = \
                    getattr(participant.stats, "total_damage_taken", 0)
                match_player_data["total_heal"] = \
                    getattr(participant.stats, "total_heal", 0)
                match_player_data["total_units_healed"] = \
                    getattr(participant.stats, "total_units_healed", 0)
                match_player_data["longest_time_spent_living"] = \
                    getattr(participant.stats, "longest_time_spent_living", 0)
                match_player_data["neutral_minions_killed"] = \
                    getattr(participant.stats, "neutral_minions_killed", 0)
                match_player_data["neutral_minions_killed_enemy_jungle"] = \
                    getattr(participant.stats, "neutral_minions_killed_enemy_jungle", 0)
                match_player_data["neutral_minions_killed_team_jungle"] = \
                    getattr(participant.stats, "neutral_minions_killed_team_jungle", 0)
                match_player_data["damage_dealt_to_objectives"] = \
                    getattr(participant.stats, "damage_dealt_to_objectives", 0)
                match_player_data["damage_dealt_to_turrets"] = \
                    getattr(participant.stats, "damage_dealt_to_turrets", 0)
                match_player_data["damage_self_mitigated"] = \
                    getattr(participant.stats, "damage_self_mitigated", 0)
                items = getattr(participant.stats, "item", None)
                if items is not None:
                    for index, item in enumerate(items):
                        match_player_data["item" + str(index)] = getattr(item, "id", -1)
                creeps_per_min_deltas = getattr(participant.timeline, "creeps_per_min_deltas", None)
                if creeps_per_min_deltas is not None:
                    match_player_data["creeps_per_min_deltas"] = json.dumps(creeps_per_min_deltas)
                cs_diff_per_min_deltas = getattr(participant.timeline, "cs_diff_per_min_deltas", None)
                if cs_diff_per_min_deltas is not None:
                    match_player_data["cs_diff_per_min_deltas"] = json.dumps(cs_diff_per_min_deltas)
                damage_taken_diff_per_min_deltas =\
                    getattr(participant.timeline, "damage_taken_diff_per_min_deltas", None)
                if damage_taken_diff_per_min_deltas is not None:
                    match_player_data["damage_taken_diff_per_min_deltas"] = json.dumps(damage_taken_diff_per_min_deltas)
                damage_taken_per_min_deltas = getattr(participant.timeline, "damage_taken_per_min_deltas", None)
                if damage_taken_per_min_deltas is not None:
                    match_player_data["damage_taken_per_min_deltas"] = json.dumps(damage_taken_per_min_deltas)
                gold_per_min_deltas = getattr(participant.timeline, "gold_per_min_deltas", None)
                if gold_per_min_deltas is not None:
                    match_player_data["gold_per_min_deltas"] = json.dumps(gold_per_min_deltas)
                xp_per_min_deltas = getattr(participant.timeline, "xp_per_min_deltas", None)
                if xp_per_min_deltas is not None:
                    match_player_data["xp_per_min_deltas"] = json.dumps(xp_per_min_deltas)
                xp_diff_per_min_deltas = getattr(participant.timeline, "xp_diff_per_min_deltas", None)
                if xp_diff_per_min_deltas is not None:
                    match_player_data["xp_diff_per_min_deltas"] = json.dumps(xp_diff_per_min_deltas)
                match_players.append(copy.deepcopy(match_player_data))

                # timeline data
                frames = getattr(participant.timeline, "frames", None)
                if frames is not None:
                    for index, frame in enumerate(frames):
                        if frame is None:
                            continue
                        if index in timelines:
                            timeline_data = timelines.get(index)
                        if timeline_data is None:
                            timeline_data = {}
                        timeline_data["match_id"] = new_match_id
                        timeline_data["frame"] = index
                        timeline_data["blue_" + role + "_creep_score"] = getattr(frame, "creep_score", 0)
                        timeline_data["blue_" + role + "_current_gold"] = getattr(frame, "current_gold", 0)
                        timeline_data["blue_" + role + "_gold_earned"] = getattr(frame, "gold_earned", 0)
                        timeline_data["blue_" + role + "_level"] = getattr(frame, "level", 0)
                        position = getattr(frame, "position", None)
                        if position is not None:
                            timeline_data["blue_" + role + "_positionX"] = position.x
                            timeline_data["blue_" + role + "_positionY"] = position.y
                        # deep copy
                        timelines[index] = copy.deepcopy(timeline_data)
                        timeline_data = {}
                        
            # find next player
            for participant in new_match.participants:
                if participant.summoner.id not in pulled_summoner_ids and\
                        participant.summoner.id not in unpulled_summoner_ids and len(unpulled_summoner_ids) < 1000:
                    unpulled_summoner_ids.add(participant.summoner.id)
            unpulled_match_ids.remove(new_match_id)
            pulled_match_ids.add(new_match_id)

            count += 1

            if count > 20:
                log.unpulled_summoner_ids(unpulled_summoner_ids, region)
                log.pulled_summoner_ids(pulled_summoner_ids, region)
                log.unpulled_match_ids(unpulled_match_ids, region)
                log.pulled_match_ids(pulled_match_ids, region)
                count = 0
            # Write match data to csv file
            # create new csv file daily
            now = datetime.datetime.now()
            with open("./../data/match_data_" + now.strftime("%Y-%m-%d") + ".csv", "a", newline="") as f:
                writer = csv.DictWriter(f, csv_header.match_data_headers,
                                        delimiter=';', quoting=csv.QUOTE_NONE, quotechar='')
                writer.writerow(match_data)
            with open("./../data/match_player_data_" + now.strftime("%Y-%m-%d") + ".csv", "a", newline="") as f:
                writer = csv.DictWriter(f, csv_header.match_player_data_headers,
                                        delimiter=';', quoting=csv.QUOTE_NONE, quotechar='')
                for match_player_data in match_players:
                    writer.writerow(match_player_data)
            # Write time line data to csv file
            with open("./../data/timeline_data_" + now.strftime("%Y-%m-%d") + ".csv", "a", newline="") as f:
                writer = csv.DictWriter(f, csv_header.timeline_data_headers,
                                        delimiter=';', quoting=csv.QUOTE_NONE, quotechar='')
                for index in timelines:
                    writer.writerow(timelines[index])


if __name__ == "__main__":
    #cass.set_riot_api_key("")  # This overrides the value set in your configuration/settings.
    cass.apply_settings("setting.json")
    #cass.set_default_region("JP")
    collect_matches("Hide on Bush", "KR", "7.22")