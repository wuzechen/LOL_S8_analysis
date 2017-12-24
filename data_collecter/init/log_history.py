
def unpulled_summoner_ids(unpulled_summoner_id, region):
    file = open("history/unpulled_summoner_ids_" + region + ".txt", "w+")
    for id in unpulled_summoner_id:
        file.write(str(id)+'\n')

def pulled_summoner_ids(pulled_summoner_id, region):
    file = open("history/pulled_summoner_ids_" + region + ".txt", "w+")
    for id in pulled_summoner_id:
        file.write(str(id)+'\n')

def unpulled_match_ids(unpulled_match_id, region):
    file = open("history/unpulled_match_ids_" + region + ".txt", "w+")
    for id in unpulled_match_id:
        file.write(str(id)+'\n')

def pulled_match_ids(pulled_match_id, region):
    file = open("history/pulled_match_ids_" + region + ".txt", "w+")
    for id in pulled_match_id:
        file.write(str(id)+'\n')