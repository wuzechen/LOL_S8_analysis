
def get_region_str_in_elasticsearch(region):
    if region == "JP" or region == "jp":
        return "Region.japan"
    elif region == "KR" or region == "kr":
        return "Region.korea"
    elif region == "NA" or region == "na":
        return "Region.north_america"
    elif region == "EUW" or region == "euw":
        return "Region.europe_west"