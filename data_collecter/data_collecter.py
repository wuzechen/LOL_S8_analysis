import random
from sortedcontainers import SortedList
import datetime
import cassiopeia as cass
from cassiopeia.core import Summoner, MatchHistory, Match, Patch
from cassiopeia.data import Queue
import csv
import re
import csv_header

def filter_match_history(summoner, patch):
    end_time = patch.end
    if end_time is None:
        end_time = datetime.datetime.now()
    match_history = MatchHistory(summoner=summoner, region=summoner.region, queues={Queue.ranked_solo_fives}, begin_time=patch.start, end_time=end_time)
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

def time_convert(time_string):
    matchObj = re.match(r'(.*)-end', time_string)
    if matchObj:
        end = int(matchObj.group(1)) + 10
        return matchObj.group(1) + "-" + str(end)
    else:
        return time_string

def collect_matches():
    initial_summoner_name = "夜空の三日月"
    region = "JP"
    patch = "7.22"

    summoner = Summoner(name=initial_summoner_name, region=region)
    patch_722 = Patch.from_str(patch, region=region)

    unpulled_summoner_ids = SortedList([summoner.id])
    pulled_summoner_ids = SortedList()

    unpulled_match_ids = SortedList()
    pulled_match_ids = SortedList()

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
            data = {
                    "match_id": new_match_id,
                    "creation": getattr(new_match, "creation", None),
                    "duration": getattr(new_match.duration, "seconds", 0),
                    "patch": getattr(new_match, "patch", patch),
                    "region": getattr(new_match, "region", region),
                    "game_type": getattr(new_match, "queue", "Queue.depreciated_ranked_solo_fives"),
                    "win": getattr(red, "win", False) and "red" or "blue",
                    "red_win": getattr(red, "win", False),
                    "red_baron_kills": getattr(red, "baron_kills", 0),
                    "red_dragon_kills": getattr(red, "dragon_kills", 0),
                    "red_rift_herald_kills": getattr(red, "rift_herald_kills", 0),
                    "red_inhibitor_kills": getattr(red, "inhibitor_kills", 0),
                    "red_tower_kills": getattr(red, "tower_kills", 0),
                    "red_first_baron": getattr(red, "first_baron", False),
                    "red_first_dragon": getattr(red, "first_dragon", False),
                    "red_first_blood": getattr(red, "first_blood", False),
                    "red_first_inhibitor": getattr(red, "first_inhibitor", False),
                    "red_first_tower": getattr(red, "first_tower", False),
                    "red_dominion_score": getattr(red, "dominion_score", 0),
                    "blue_win": getattr(blue, "win", False),
                    "blue_baron_kills": getattr(blue, "baron_kills", 0),
                    "blue_dragon_kills": getattr(blue, "dragon_kills", 0),
                    "blue_rift_herald_kills": getattr(blue, "rift_herald_kills", 0),
                    "blue_inhibitor_kills": getattr(blue, "inhibitor_kills", 0),
                    "blue_tower_kills": getattr(blue, "tower_kills", 0),
                    "blue_first_baron": getattr(blue, "first_baron", False),
                    "blue_first_dragon": getattr(blue, "first_dragon", False),
                    "blue_first_blood": getattr(blue, "first_blood", False),
                    "blue_first_inhibitor": getattr(blue, "first_inhibitor", False),
                    "blue_first_tower": getattr(blue, "first_tower", False),
                    "blue_dominion_score": getattr(blue, "dominion_score", 0),
                    }
            timeline_data = {"match_id": new_match_id}
            event_data = {}
            for index in range(len(red.bans)):
                data["red_ban" + str(index)] = red.bans[index] is not None and red.bans[index].id or -1
            for index in range(len(blue.bans)):
                data["blue_ban" + str(index)] = blue.bans[index] is not None and blue.bans[index].id or -1
            for participant in red.participants:
                role = get_role(str(getattr(participant, "lane", "null")) + str(getattr(participant, "role", "null")))
                if role == "null":
                    continue
                data["red_pick_" + role] = \
                    getattr(participant.champion, "id", -1)
                data["red_player_" + role] = \
                    getattr(participant.summoner, "id", -1)
                data["red_player_level_" + role] = \
                    getattr(participant, "rank_last_season", 0)
                data["red_summoner_spell_d_" + role] =\
                    getattr(participant.summoner_spell_d, "id", -1)
                data["red_summoner_spell_f_" + role] = \
                    getattr(participant.summoner_spell_f, "id", -1)
                data["red_player_kill_" + role] = \
                    getattr(participant.stats, "kills", 0)
                data["red_player_deaths_" + role] = \
                    getattr(participant.stats, "deaths", 0)
                data["red_player_assists_" + role] = \
                    getattr(participant.stats, "assists", 0)
                data["red_player_gold_earned_" + role] = \
                    getattr(participant.stats, "gold_earned", 0)
                data["red_player_gold_spent_" + role] = \
                    getattr(participant.stats, "gold_spent", 0)
                data["red_player_kda_" + role] = \
                    getattr(participant.stats, "kda", 0)
                data["red_player_level_" + role] = \
                    getattr(participant.stats, "level", 0)
                data["red_player_total_minions_killed_" + role] = \
                    getattr(participant.stats, "total_minions_killed", 0)
                data["red_player_turret_kills_" + role] = \
                    getattr(participant.stats, "turret_kills", 0)
                data["red_player_inhibitor_kills_" + role] = \
                    getattr(participant.stats, "inhibitor_kills", 0)
                data["red_player_killing_sprees_" + role] = \
                    getattr(participant.stats, "killing_sprees", 0)
                data["red_player_double_kills_" + role] = \
                    getattr(participant.stats, "double_kills", 0)
                data["red_player_triple_kills_" + role] = \
                    getattr(participant.stats, "triple_kills", 0)
                data["red_player_quadra_kills_" + role] = \
                    getattr(participant.stats, "quadra_kills", 0)
                data["red_player_panta_kills_" + role] = \
                    getattr(participant.stats, "penta_kills", 0)
                data["red_player_first_blood_assist_" + role] = \
                    getattr(participant.stats, "first_blood_assist", False)
                data["red_player_first_blood_kill_" + role] = \
                    getattr(participant.stats, "first_blood_kill", False)
                data["red_player_first_inhibitor_assist_" + role] = \
                    getattr(participant.stats, "first_inhibitor_assist", False)
                data["red_player_first_inhibitor_kill_" + role] = \
                    getattr(participant.stats, "first_inhibitor_kill", False)
                data["red_player_tower_assist_" + role] = \
                    getattr(participant.stats, "first_tower_assist", False)
                data["red_player_tower_kill_" + role] = \
                    getattr(participant.stats, "first_tower_kill", False)
                data["red_player_vision_score_" + role] = \
                    getattr(participant.stats, "vision_score", 0)
                data["red_player_vision_wards_bought_in_game_" + role] = \
                    getattr(participant.stats, "vision_wards_bought_in_game", 0)
                data["red_player_sight_wards_bought_in_game_" + role] = \
                    getattr(participant.stats, "sight_wards_bought_in_game", 0)
                data["red_player_wards_killed_" + role] = \
                    getattr(participant.stats, "wards_killed", 0)
                data["red_player_wards_placed_" + role] = \
                    getattr(participant.stats, "wards_placed", 0)
                data["red_player_total_time_crowd_control_dealt_" + role] = \
                    getattr(participant.stats, "total_time_crowd_control_dealt", 0)
                data["red_player_total_damage_dealt_" + role] = \
                    getattr(participant.stats, "total_damage_dealt", 0)
                data["red_player_total_damage_dealt_to_champions_" + role] = \
                    getattr(participant.stats, "total_damage_dealt_to_champions", 0)
                data["red_player_total_damage_taken_" + role] = \
                    getattr(participant.stats, "total_damage_taken", 0)
                data["red_player_total_heal_" + role] = \
                    getattr(participant.stats, "total_heal", 0)
                data["red_player_total_units_healed_" + role] = \
                    getattr(participant.stats, "total_units_healed", 0)
                data["red_player_longest_time_spent_living_" + role] = \
                    getattr(participant.stats, "longest_time_spent_living", 0)
                data["red_player_neutral_minions_killed_" + role] =\
                    getattr(participant.stats, "neutral_minions_killed", 0)
                data["red_player_neutral_minions_killed_enemy_jungle_" + role] = \
                    getattr(participant.stats, "neutral_minions_killed_enemy_jungle", 0)
                data["red_player_neutral_minions_killed_team_jungle_" + role] = \
                    getattr(participant.stats, "neutral_minions_killed_team_jungle", 0)
                data["red_player_damage_dealt_to_objectives_" + role] = \
                    getattr(participant.stats, "damage_dealt_to_objectives", 0)
                data["red_player_damage_dealt_to_turrets_" + role] = \
                    getattr(participant.stats, "damage_dealt_to_turrets", 0)
                data["red_player_damage_self_mitigated_" + role] = \
                    getattr(participant.stats, "damage_self_mitigated", 0)
                items = getattr(participant.stats, "item", None)
                if items is not None:
                    for index, item in enumerate(items):
                        data["red_player_item" + str(index) + "_" + role] = getattr(item, "id", -1)
                creeps_per_min_deltas = getattr(participant.timeline, "creeps_per_min_deltas", None)
                if creeps_per_min_deltas is not None:
                    for time, value in creeps_per_min_deltas.items():
                        data["red_player_creeps_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                cs_diff_per_min_deltas = getattr(participant.timeline, "cs_diff_per_min_deltas", None)
                if cs_diff_per_min_deltas is not None:
                    for time, value in cs_diff_per_min_deltas.items():
                        data["red_player_cs_diff_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                damage_taken_diff_per_min_deltas = getattr(participant.timeline, "damage_taken_diff_per_min_deltas", None)
                if damage_taken_diff_per_min_deltas is not None:
                    for time, value in damage_taken_diff_per_min_deltas.items():
                        data["red_player_damage_taken_diff_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                damage_taken_per_min_deltas = getattr(participant.timeline, "damage_taken_per_min_deltas",None)
                if damage_taken_per_min_deltas is not None:
                    for time, value in damage_taken_per_min_deltas.items():
                        data["red_player_damage_taken_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                gold_per_min_deltas = getattr(participant.timeline, "gold_per_min_deltas", None)
                if gold_per_min_deltas is not None:
                    for time, value in gold_per_min_deltas.items():
                        data["red_player_gold_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                xp_per_min_deltas = getattr(participant.timeline, "xp_per_min_deltas", None)
                if xp_per_min_deltas is not None:
                    for time, value in xp_per_min_deltas.items():
                        data["red_player_xp_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                xp_diff_per_min_deltas = getattr(participant.timeline, "xp_diff_per_min_deltas", None)
                if xp_diff_per_min_deltas is not None:
                    for time, value in xp_per_min_deltas.items():
                        data["red_player_xp_diff_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                frames = getattr(participant.timeline, "frames", None)
                if frames is not None:
                    for index, frame in enumerate(frames):
                        timeline_data["red_" + role + "_creep_score_" + str(index)] = getattr(frame, "creep_score", 0)
                        timeline_data["red_" + role + "_current_gold_" + str(index)] = getattr(frame, "current_gold", 0)
                        timeline_data["red_" + role + "_gold_earned_" + str(index)] = getattr(frame, "gold_earned", 0)
                        timeline_data["red_" + role + "_level_" + str(index)] = getattr(frame, "level", 0)
                        position = getattr(frame, "position", None)
                        if position is not None:
                            timeline_data["red_" + role + "_positionX_" + str(index)] = position.x
                            timeline_data["red_" + role + "_positionY_" + str(index)] = position.y
            for participant in blue.participants:
                role = get_role(str(getattr(participant, "lane", "null")) + str(getattr(participant, "role", "null")))
                if role == "null":
                    continue
                data["blue_pick_" + role] = \
                    getattr(participant.champion, "id", -1)
                data["blue_player_" + role] = \
                    getattr(participant.summoner, "id", -1)
                data["blue_player_level_" + role] = \
                    getattr(participant, "rank_last_season", 0)
                data["blue_summoner_spell_d_" + role] =\
                    getattr(participant.summoner_spell_d, "id", -1)
                data["blue_summoner_spell_f_" + role] = \
                    getattr(participant.summoner_spell_f, "id", -1)
                data["blue_player_kill_" + role] = \
                    getattr(participant.stats, "kills", 0)
                data["blue_player_deaths_" + role] = \
                    getattr(participant.stats, "deaths", 0)
                data["blue_player_assists_" + role] = \
                    getattr(participant.stats, "assists", 0)
                data["blue_player_gold_earned_" + role] = \
                    getattr(participant.stats, "gold_earned", 0)
                data["blue_player_gold_spent_" + role] = \
                    getattr(participant.stats, "gold_spent", 0)
                data["blue_player_kda_" + role] = \
                    getattr(participant.stats, "kda", 0)
                data["blue_player_level_" + role] = \
                    getattr(participant.stats, "level", 0)
                data["blue_player_total_minions_killed_" + role] = \
                    getattr(participant.stats, "total_minions_killed", 0)
                data["blue_player_turret_kills_" + role] = \
                    getattr(participant.stats, "turret_kills", 0)
                data["blue_player_inhibitor_kills_" + role] = \
                    getattr(participant.stats, "inhibitor_kills", 0)
                data["blue_player_killing_sprees_" + role] = \
                    getattr(participant.stats, "killing_sprees", 0)
                data["blue_player_double_kills_" + role] = \
                    getattr(participant.stats, "double_kills", 0)
                data["blue_player_triple_kills_" + role] = \
                    getattr(participant.stats, "triple_kills", 0)
                data["blue_player_quadra_kills_" + role] = \
                    getattr(participant.stats, "quadra_kills", 0)
                data["blue_player_panta_kills_" + role] = \
                    getattr(participant.stats, "penta_kills", 0)
                data["blue_player_first_blood_assist_" + role] = \
                    getattr(participant.stats, "first_blood_assist", False)
                data["blue_player_first_blood_kill_" + role] = \
                    getattr(participant.stats, "first_blood_kill", False)
                data["blue_player_first_inhibitor_assist_" + role] = \
                    getattr(participant.stats, "first_inhibitor_assist", False)
                data["blue_player_first_inhibitor_kill_" + role] = \
                    getattr(participant.stats, "first_inhibitor_kill", False)
                data["blue_player_tower_assist_" + role] = \
                    getattr(participant.stats, "first_tower_assist", False)
                data["blue_player_tower_kill_" + role] = \
                    getattr(participant.stats, "first_tower_kill", False)
                data["blue_player_vision_score_" + role] = \
                    getattr(participant.stats, "vision_score", 0)
                data["blue_player_vision_wards_bought_in_game_" + role] = \
                    getattr(participant.stats, "vision_wards_bought_in_game", 0)
                data["blue_player_sight_wards_bought_in_game_" + role] = \
                    getattr(participant.stats, "sight_wards_bought_in_game", 0)
                data["blue_player_wards_killed_" + role] = \
                    getattr(participant.stats, "wards_killed", 0)
                data["blue_player_wards_placed_" + role] = \
                    getattr(participant.stats, "wards_placed", 0)
                data["blue_player_total_time_crowd_control_dealt_" + role] = \
                    getattr(participant.stats, "total_time_crowd_control_dealt", 0)
                data["blue_player_total_damage_dealt_" + role] = \
                    getattr(participant.stats, "total_damage_dealt", 0)
                data["blue_player_total_damage_dealt_to_champions_" + role] = \
                    getattr(participant.stats, "total_damage_dealt_to_champions", 0)
                data["blue_player_total_damage_taken_" + role] = \
                    getattr(participant.stats, "total_damage_taken", 0)
                data["blue_player_total_heal_" + role] = \
                    getattr(participant.stats, "total_heal", 0)
                data["blue_player_total_units_healed_" + role] = \
                    getattr(participant.stats, "total_units_healed", 0)
                data["blue_player_longest_time_spent_living_" + role] = \
                    getattr(participant.stats, "longest_time_spent_living", 0)
                data["blue_player_neutral_minions_killed_" + role] =\
                    getattr(participant.stats, "neutral_minions_killed", 0)
                data["blue_player_neutral_minions_killed_enemy_jungle_" + role] = \
                    getattr(participant.stats, "neutral_minions_killed_enemy_jungle", 0)
                data["blue_player_neutral_minions_killed_team_jungle_" + role] = \
                    getattr(participant.stats, "neutral_minions_killed_team_jungle", 0)
                data["blue_player_damage_dealt_to_objectives_" + role] = \
                    getattr(participant.stats, "damage_dealt_to_objectives", 0)
                data["blue_player_damage_dealt_to_turrets_" + role] = \
                    getattr(participant.stats, "damage_dealt_to_turrets", 0)
                data["blue_player_damage_self_mitigated_" + role] = \
                    getattr(participant.stats, "damage_self_mitigated", 0)
                items = getattr(participant.stats, "item", None)
                if items is not None:
                    for index, item in enumerate(items):
                        data["blue_player_item" + str(index) + "_" + role] = getattr(item, "id", -1)
                creeps_per_min_deltas = getattr(participant.timeline, "creeps_per_min_deltas", None)
                if creeps_per_min_deltas is not None:
                    for time, value in creeps_per_min_deltas.items():
                        data["blue_player_creeps_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                cs_diff_per_min_deltas = getattr(participant.timeline, "cs_diff_per_min_deltas", None)
                if cs_diff_per_min_deltas is not None:
                    for time, value in cs_diff_per_min_deltas.items():
                        data["blue_player_cs_diff_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                damage_taken_diff_per_min_deltas = getattr(participant.timeline, "damage_taken_diff_per_min_deltas",None)
                if damage_taken_diff_per_min_deltas is not None:
                    for time, value in damage_taken_diff_per_min_deltas.items():
                        data["blue_player_damage_taken_diff_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                damage_taken_per_min_deltas = getattr(participant.timeline, "damage_taken_per_min_deltas", None)
                if damage_taken_per_min_deltas is not None:
                    for time, value in damage_taken_per_min_deltas.items():
                        data["blue_player_damage_taken_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                gold_per_min_deltas = getattr(participant.timeline, "gold_per_min_deltas", None)
                if gold_per_min_deltas is not None:
                    for time, value in gold_per_min_deltas.items():
                        data["blue_player_gold_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                xp_per_min_deltas = getattr(participant.timeline, "xp_per_min_deltas", None)
                if xp_per_min_deltas is not None:
                    for time, value in xp_per_min_deltas.items():
                        data["blue_player_xp_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                xp_diff_per_min_deltas = getattr(participant.timeline, "xp_diff_per_min_deltas", None)
                if xp_diff_per_min_deltas is not None:
                    for time, value in xp_per_min_deltas.items():
                        data["blue_player_xp_diff_per_min_deltas_" + time_convert(time)+ "_" + role] = value
                frames = getattr(participant.timeline, "frames", None)
                if frames is not None:
                    for index, frame in enumerate(frames):
                        timeline_data["blue_" + role + "_creep_score_" + str(index)] = getattr(frame, "creep_score", 0)
                        timeline_data["blue_" + role + "_current_gold_" + str(index)] = getattr(frame, "current_gold", 0)
                        timeline_data["blue_" + role + "_gold_earned_" + str(index)] = getattr(frame, "gold_earned", 0)
                        timeline_data["blue_" + role + "_level_" + str(index)] = getattr(frame, "level", 0)
                        position = getattr(frame, "position", None)
                        if position is not None:
                            timeline_data["blue_" + role + "_positionX_" + str(index)] = position.x
                            timeline_data["blue_" + role + "_positionY_" + str(index)] = position.y
            # find next player
            for participant in new_match.participants:
                if participant.summoner.id not in pulled_summoner_ids and participant.summoner.id not in unpulled_summoner_ids:
                    unpulled_summoner_ids.add(participant.summoner.id)
            unpulled_match_ids.remove(new_match_id)
            pulled_match_ids.add(new_match_id)

            # Write match data to csv file
            with open("./../data/match_data.csv", "a", newline="") as f:
                writer = csv.DictWriter(f, csv_header.data_headers)
                writer.writerow(data)
            # Write time line data to csv file
            with open("./../data/timeline_data.csv", "a", newline="") as f:
                writer = csv.DictWriter(f, csv_header.timeline_data_headers)
                writer.writerow(timeline_data)



if __name__ == "__main__":
    #cass.set_riot_api_key("")  # This overrides the value set in your configuration/settings.
    cass.apply_settings("setting.json")
    #cass.set_default_region("JP")
    collect_matches()