import leaderboard.leaderboard as lb
from leaderboard.categories import categories, category_names
from leaderboard import tiers
from leaderboard import ranking
from leaderboard import db
from leaderboard import update as lb_update
from leaderboard import commands_helper as helper
import leaderboard.username as names
from formatting import time as time_format
from formatting import moves as moves_format

def get_pb(width, height, user):
    username = names.find_username(user)

    # get all the relevant data in one leaderboard call
    data = lb.get_leaderboard(width, height, user=username)

    msg = f"{width}x{height} PBs for {username}\n"
    msg += "```\n"

    # Sizes used in tier ranking
    if (width, height) in helper.get_used_sizes(categories):
        for i, category in enumerate(categories):
            if category["width"] == width and category["height"] == height:
                # find the users pb for this category
                best_time = helper.category_pb(category,data)

                # find the tier of this result
                tier = tiers.result_tier(i, best_time)
                tier_name = helper.get_tier_name(tier)

                # find the next tier above the users tier so we can show the requirement
                next_tier = helper.get_next_tier(tier)

                requirement_msg = helper.get_requirement_message(next_tier,i)

                msg += f"{category_names[i]}: {time_format.format(best_time)} ({tier_name})"
                if requirement_msg is not None:
                    msg += f" ({requirement_msg})"
                msg += "\n"
    # Other sizes
    else:
        best_time = helper.general_pb(data)
        msg += f"{width}x{height} time: {time_format.format(best_time)}\n"

    msg += "```"

    return msg

def get_move_pb(width, height, user):
    username = names.find_username(user)

    # get all the relevant data in one leaderboard call
    data = lb.get_leaderboard(width, height, user=username, pbtype="move")

    msg = f"{width}x{height} PBs for {username}\n"
    msg += "```\n"

    results = {}
    for result in data:
        avglen = result["avglen"]

        if results[avglen] is None:
            results[avglen] = result["moves"]
        else:
            results[avglen] = min(results[avglen], result["moves"])

    # sort results by avglen
    results = dict(sorted(results.items(), key=lambda x: x[0]))

    for (k, v) in results.items():
        if v is None:
            continue

        if k == 1:
            name = "single"
        else:
            name = f"ao{k}"

        msg += f"{width}x{height} {name}: {moves_format.format(v)}\n"

    msg += "```"

    return msg

def get_req(width, height, tier_name):
    tier = tiers.get_tier(tier_name)
    real_tier_name = tier["name"]

    msg = f"Requirements for {real_tier_name} {width}x{height}\n"
    msg += "```\n"
    for i, category in enumerate(categories):
        if category["width"] == width and category["height"] == height:
            req = tier["times"][i]
            msg += f"{category_names[i]}: {time_format.format(req)}\n"
    msg += "```"

    return msg

def rank(user):
    username = names.find_username(user)
    table = db.latest_results()
    position = ranking.place(table, username)
    power = ranking.power(table[username])
    power_tier_name = tiers.power_tier(power)["name"]
    return f"{username} is in position {position} with {power} power ({power_tier_name})"

def update():
    lb_update.update()
