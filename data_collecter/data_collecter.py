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
               "blue_ban0", "blue_ban1", "blue_ban2", "blue_ban3", "blue_ban4",]

    roles = ["top", "jungle", "mid", "adc", "support"]

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
                data["red_ban" + str(index)] = red.bans[index] is not None and red.bans[index].id or "-1"
            for index in range(len(blue.bans)):
                data["blue_ban" + str(index)] = blue.bans[index] is not None and blue.bans[index].id or "-1"
            for participant in red.participants:
                role = str(participant.lane) + str(participant.role)
                data["red_pick_" + role] = \
                    participant.champion.id is not None and participant.champion.id or -1
                data["red_player_" + role] = \
                    participant.summoner.id is not None and participant.summoner.id or -1
                data["red_player_level_" + role] = \
                    participant.rank_last_season is not None and participant.rank_last_season or 0
                data["red_summoner_spell_d_" + role] =\
                    participant.summoner_spell_d.id is not None and participant.summoner_spell_d.id or -1
                data["red_summoner_spell_f_" + role] = \
                    participant.summoner_spell_f.id is not None and participant.summoner_spell_f.id or -1
                data["red_player_kill_" + role] = \
                    participant.stats.kills is not None and participant.stats.kills or 0
                data["red_player_deaths_" + role] = \
                    participant.stats.deaths is not None and participant.stats.deaths or 0
                data["red_player_assists_" + role] = \
                    participant.stats.assists is not None and participant.stats.assists or 0
                data["red_player_gold_earned_" + role] = \
                    participant.stats.gold_earned is not None and participant.stats.gold_earned or 0
                data["red_player_gold_spent_" + role] = \
                    participant.stats.gold_spent is not None and participant.stats.gold_spent or 0
                data["red_player_kda_" + role] = \
                    participant.stats.kda is not None and participant.stats.kda or 0
                data["red_player_level_" + role] = \
                    participant.stats.level is not None and participant.stats.level or 0
                data["red_player_total_minions_killed" + role] = \
                    participant.stats.total_minions_killed is not None and participant.stats.total_minions_killed or 0
                data["red_player_turret_kills" + role] = \
                    participant.stats.turret_kills is not None and participant.stats.turret_kills or 0
                data["red_player_inhibitor_kills_" + role] = \
                    participant.stats.inhibitor_kills is not None and participant.stats.inhibitor_kills or 0
                data["red_player_killing_sprees_" + role] = \
                    participant.stats.killing_sprees is not None and participant.stats.killing_sprees or 0
                data["red_player_double_kills_" + role] = \
                    participant.stats.double_kills is not None and participant.stats.double_kills or 0
                data["red_player_triple_kills" + role] = \
                    participant.stats.triple_kills is not None and participant.stats.triple_kills or 0
                data["red_player_quadra_kills" + role] = \
                    participant.stats.quadra_kills is not None and participant.stats.quadra_kills or 0
                data["red_player_panta_kills" + role] = \
                    participant.stats.penta_kills is not None and participant.stats.penta_kills or 0
                data["red_player_first_blood_assist_" + role] = \
                    participant.stats.first_blood_assist is not None and participant.stats.first_blood_assist or False
                data["red_player_first_blood_kill_" + role] = \
                    participant.stats.first_blood_kill is not None and participant.stats.first_blood_kill or False
                data["red_player_first_inhibitor_assist_" + role] = \
                    participant.stats.first_inhibitor_assist is not None and participant.stats.first_inhibitor_assist or False
                data["red_player_first_inhibitor_kill_" + role] = \
                    participant.stats.first_inhibitor_kill is not None and participant.stats.first_inhibitor_kill or False
                data["red_player_tower_assist_" + role] = \
                    participant.stats.first_tower_assist is not None and participant.stats.first_tower_assist or False
                data["red_player_tower_kill_" + role] = \
                    participant.stats.first_tower_kill is not None and participant.stats.first_tower_kill or False
                data["red_player_vision_score_" + role] = \
                    participant.stats.vision_score is not None and participant.stats.vision_score or 0
                data["red_player_vision_wards_bought_in_game_" + role] = \
                    participant.stats.vision_wards_bought_in_game is not None and participant.stats.vision_wards_bought_in_game or 0
                data["red_player_sight_wards_bought_in_game_" + role] = \
                    participant.stats.sight_wards_bought_in_game is not None and participant.stats.sight_wards_bought_in_game or 0
                data["red_player_wards_killed_" + role] = \
                    participant.stats.wards_killed is not None and participant.stats.wards_killed or 0
                data["red_player_wards_placed_" + role] = \
                    participant.stats.wards_placed is not None and participant.stats.wards_placed or 0
                data["red_player_total_time_crowd_control_dealt_" + role] = \
                    participant.stats.total_time_crowd_control_dealt is not None and participant.stats.total_time_crowd_control_dealt or 0
                data["red_player_total_damage_dealt_" + role] = \
                    participant.stats.total_damage_dealt is not None and participant.stats.total_damage_dealt or 0
                data["red_player_total_damage_dealt_to_champions_" + role] = \
                    participant.stats.total_damage_dealt_to_champions is not None and participant.stats.total_damage_dealt_to_champions or 0
                data["red_player_total_damage_taken_" + role] = \
                    participant.stats.total_damage_taken is not None and participant.stats.total_damage_taken or 0
                data["red_player_total_heal_" + role] = \
                    participant.stats.total_heal is not None and participant.stats.total_heal or 0
                data["red_player_total_units_healed_" + role] = \
                    participant.stats.total_units_healed is not None and participant.stats.total_units_healed or 0
                data["red_player_longest_time_spent_living_" + role] = \
                    participant.stats.longest_time_spent_living is not None and participant.stats.longest_time_spent_living or 0
                data["red_player_neutral_minions_killed_" + role] =\
                    participant.stats.neutral_minions_killed is not None and participant.stats.neutral_minions_killed or 0
                data["red_player_neutral_minions_killed_enemy_jungle_" + role] = \
                    participant.stats.neutral_minions_killed_enemy_jungle is not None and participant.stats.neutral_minions_killed_enemy_jungle or 0
                data["red_player_neutral_minions_killed_team_jungle_" + role] = \
                    participant.stats.neutral_minions_killed_team_jungle is not None and participant.stats.neutral_minions_killed_team_jungle or 0
                data["red_player_damage_dealt_to_objectives_" + role] = \
                    participant.stats.damage_dealt_to_objectives is not None and participant.stats.damage_dealt_to_objectives or 0
                data["red_player_damage_dealt_to_turrets_" + role] = \
                    participant.stats.damage_dealt_to_turrets is not None and participant.stats.damage_dealt_to_turrets or 0
                data["red_player_damage_self_mitigated_" + role] = \
                    participant.stats.damage_self_mitigated is not None and participant.stats.damage_self_mitigated or 0

            for participant in blue.participants:
                role = str(participant.lane) + str(participant.role)
                data["blue_pick_" + role] = \
                    participant.champion.id is not None and participant.champion.id or -1
                data["blue_player_" + role] = \
                    participant.summoner.id is not None and participant.summoner.id or -1
                data["blue_player_level_" + role] = \
                    participant.rank_last_season is not None and participant.rank_last_season or 0
                data["blue_summoner_spell_d_" + role] =\
                    participant.summoner_spell_d.id is not None and participant.summoner_spell_d.id or -1
                data["blue_summoner_spell_f_" + role] = \
                    participant.summoner_spell_f.id is not None and participant.summoner_spell_f.id or -1
                data["blue_player_kill_" + role] = \
                    participant.stats.kills is not None and participant.stats.kills or 0
                data["blue_player_deaths_" + role] = \
                    participant.stats.deaths is not None and participant.stats.deaths or 0
                data["blue_player_assists_" + role] = \
                    participant.stats.assists is not None and participant.stats.assists or 0
                data["blue_player_gold_earned_" + role] = \
                    participant.stats.gold_earned is not None and participant.stats.gold_earned or 0
                data["blue_player_gold_spent_" + role] = \
                    participant.stats.gold_spent is not None and participant.stats.gold_spent or 0
                data["blue_player_kda_" + role] = \
                    participant.stats.kda is not None and participant.stats.kda or 0
                data["blue_player_level_" + role] = \
                    participant.stats.level is not None and participant.stats.level or 0
                data["blue_player_total_minions_killed" + role] = \
                    participant.stats.total_minions_killed is not None and participant.stats.total_minions_killed or 0
                data["blue_player_turret_kills" + role] = \
                    participant.stats.turret_kills is not None and participant.stats.turret_kills or 0
                data["blue_player_inhibitor_kills_" + role] = \
                    participant.stats.inhibitor_kills is not None and participant.stats.inhibitor_kills or 0
                data["blue_player_killing_sprees_" + role] = \
                    participant.stats.killing_sprees is not None and participant.stats.killing_sprees or 0
                data["blue_player_double_kills_" + role] = \
                    participant.stats.double_kills is not None and participant.stats.double_kills or 0
                data["blue_player_triple_kills" + role] = \
                    participant.stats.triple_kills is not None and participant.stats.triple_kills or 0
                data["blue_player_quadra_kills" + role] = \
                    participant.stats.quadra_kills is not None and participant.stats.quadra_kills or 0
                data["blue_player_panta_kills" + role] = \
                    participant.stats.penta_kills is not None and participant.stats.penta_kills or 0
                data["blue_player_first_blood_assist_" + role] = \
                    participant.stats.first_blood_assist is not None and participant.stats.first_blood_assist or False
                data["blue_player_first_blood_kill_" + role] = \
                    participant.stats.first_blood_kill is not None and participant.stats.first_blood_kill or False
                data["blue_player_first_inhibitor_assist_" + role] = \
                    participant.stats.first_inhibitor_assist is not None and participant.stats.first_inhibitor_assist or False
                data["blue_player_first_inhibitor_kill_" + role] = \
                    participant.stats.first_inhibitor_kill is not None and participant.stats.first_inhibitor_kill or False
                data["blue_player_tower_assist_" + role] = \
                    participant.stats.first_tower_assist is not None and participant.stats.first_tower_assist or False
                data["blue_player_tower_kill_" + role] = \
                    participant.stats.first_tower_kill is not None and participant.stats.first_tower_kill or False
                data["blue_player_vision_score_" + role] = \
                    participant.stats.vision_score is not None and participant.stats.vision_score or 0
                data["blue_player_vision_wards_bought_in_game_" + role] = \
                    participant.stats.vision_wards_bought_in_game is not None and participant.stats.vision_wards_bought_in_game or 0
                data["blue_player_sight_wards_bought_in_game_" + role] = \
                    participant.stats.sight_wards_bought_in_game is not None and participant.stats.sight_wards_bought_in_game or 0
                data["blue_player_wards_killed_" + role] = \
                    participant.stats.wards_killed is not None and participant.stats.wards_killed or 0
                data["blue_player_wards_placed_" + role] = \
                    participant.stats.wards_placed is not None and participant.stats.wards_placed or 0
                data["blue_player_total_time_crowd_control_dealt_" + role] = \
                    participant.stats.total_time_crowd_control_dealt is not None and participant.stats.total_time_crowd_control_dealt or 0
                data["blue_player_total_damage_dealt_" + role] = \
                    participant.stats.total_damage_dealt is not None and participant.stats.total_damage_dealt or 0
                data["blue_player_total_damage_dealt_to_champions_" + role] = \
                    participant.stats.total_damage_dealt_to_champions is not None and participant.stats.total_damage_dealt_to_champions or 0
                data["blue_player_total_damage_taken_" + role] = \
                    participant.stats.total_damage_taken is not None and participant.stats.total_damage_taken or 0
                data["blue_player_total_heal_" + role] = \
                    participant.stats.total_heal is not None and participant.stats.total_heal or 0
                data["blue_player_total_units_healed_" + role] = \
                    participant.stats.total_units_healed is not None and participant.stats.total_units_healed or 0
                data["blue_player_longest_time_spent_living_" + role] = \
                    participant.stats.longest_time_spent_living is not None and participant.stats.longest_time_spent_living or 0
                data["blue_player_neutral_minions_killed_" + role] =\
                    participant.stats.neutral_minions_killed is not None and participant.stats.neutral_minions_killed or 0
                data["blue_player_neutral_minions_killed_enemy_jungle_" + role] = \
                    participant.stats.neutral_minions_killed_enemy_jungle is not None and participant.stats.neutral_minions_killed_enemy_jungle or 0
                data["blue_player_neutral_minions_killed_team_jungle_" + role] = \
                    participant.stats.neutral_minions_killed_team_jungle is not None and participant.stats.neutral_minions_killed_team_jungle or 0
                data["blue_player_damage_dealt_to_objectives_" + role] = \
                    participant.stats.damage_dealt_to_objectives is not None and participant.stats.damage_dealt_to_objectives or 0
                data["blue_player_damage_dealt_to_turrets_" + role] = \
                    participant.stats.damage_dealt_to_turrets is not None and participant.stats.damage_dealt_to_turrets or 0
                data["blue_player_damage_self_mitigated_" + role] = \
                    participant.stats.damage_self_mitigated is not None and participant.stats.damage_self_mitigated or 0

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