
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