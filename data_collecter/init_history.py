from sortedcontainers import SortedList

def unpulled_summoner_ids():
    process_file = open("history/unpulled_summoner_ids.txt", "r")
    unpulled_summoner_ids = SortedList()
    try:
        lines = process_file.readlines()
        for line in lines:
            unpulled_summoner_ids.add(int(line))
    finally:
        process_file.close()
    return unpulled_summoner_ids

def pulled_summoner_ids():
    process_file = open("history/pulled_summoner_ids.txt", "r")
    pulled_summoner_ids = SortedList()
    try:
        lines = process_file.readlines()
        for line in lines:
            pulled_summoner_ids.add(int(line))
    finally:
        process_file.close()
    return pulled_summoner_ids

def unpulled_match_ids():
    process_file = open("history/unpulled_match_ids.txt", "r")
    unpulled_match_ids = SortedList()
    try:
        lines = process_file.readlines()
        for line in lines:
            unpulled_match_ids.add(int(line))
    finally:
        process_file.close()
    return unpulled_match_ids

def pulled_match_ids():
    process_file = open("history/pulled_match_ids.txt", "r")
    pulled_match_ids = SortedList()
    try:
        lines = process_file.readlines()
        for line in lines:
            pulled_match_ids.add(int(line))
    finally:
        process_file.close()
    return pulled_match_ids