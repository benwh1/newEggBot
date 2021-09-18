import os
import requests
from leaderboard import categories
from leaderboard import tiers
from helper import serialize
from replit import db

def get_leaderboard(width=-1, height=-1, solvetype="any", avglen=-1, user=""):
    url = os.environ['slidysim']
    r = requests.post(url, data = {
        "width"       : width,
        "height"      : height,
        "solvetype"   : solvetype,
        "displaytype" : "Standard",
        "avglen"      : avglen,
        "pbtype"      : "time",
        "sortby"      : "time",
        "controls"    : "km",
        "user"        : user,
        "solvedata"   : 0,
        "version"     : "28.3"
    })

    data = [line.split(",") for line in r.text[19:].split("<br>")[:-1]]

    leaderboard = []
    for row in data:
        leaderboard.append({
            "width"       : int(row[0]),
            "height"      : int(row[1]),
            "solvetype"   : row[2],
            "displaytype" : row[3],
            "user"        : row[4],
            "time"        : int(row[5]),
            "moves"       : int(row[6]),
            "tps"         : int(row[7]),
            "avglen"      : int(row[8]),
            "controls"    : row[9],
            "pbtype"      : row[10],
            "timestamp"   : int(row[12])
        })

    return leaderboard

# filters the leaderboard results, removing any results that don't correspond
# to one of our categories. each result has a "category" parameter appended
# which is the index of the category in leaderboard.categories.categories.
def get_category_results():
    # get the full leaderboard
    lb = get_leaderboard()

    # filter the results
    filtered_lb = []
    entries = ["width", "height", "solvetype", "avglen"]
    for result in lb:
        result_category = {x : result[x] for x in entries}
        try:
            # add the category index for convenience
            index = categories.categories.index(result_category)
            result["category"] = index
            filtered_lb.append(result)
        except ValueError as e:
            continue

    # sort by username
    filtered_lb.sort(key=lambda x: x["user"])

    return filtered_lb

# creates a dict of the form {username : [list of category times]}
# where the i'th element of the list of times is the users time in
# the i'th category in leaderboard.categories.categories.
def results_table():
    results = get_category_results()
    users = sorted(set(x["user"] for x in results))

    table = {}

    for user in users:
        # create an empty row with one entry per category
        row = [None]*len(categories.categories)

        for result in results:
            if result["user"] != user:
                continue

            category = result["category"]

            # fill in the entry in the table with the users best time.
            # note that there may be multiple results in the leaderboard
            # if the user has done solves with both control schemes,
            # so we need to choose the fastest one.
            if row[category] is None:
                row[category] = result["time"]
            else:
                row[category] = min(row[category], result["time"])

        # add the users results to the table
        table[user] = row

    return table

def power(results_list):
    total = 0
    for i, result in enumerate(results_list):
        tier = tiers.result_tier(i, result)
        if tier is None:
            continue
        total += tier["power"]
    return total

# sort rows of the table by power
def sort_table(results_table):
    return dict(sorted(results_table.items(), key=lambda x: -power(x[1])))

# takes a dict of results {user : [results]} and creates a list of lists
# of the form [[user, place, power, results], ...]
def format_results_table(results_table):
    sorted_table = sort_table(results_table)
    formatted_table = []
    for i, user in enumerate(sorted_table):
        # add row but replace None with -1 in the results
        new_row = [user, i+1, power(sorted_table[user])]
        new_row += [x if x is not None else -1 for x in sorted_table[user]]
        formatted_table.append(new_row)
    return formatted_table

# get the latest results table that we have stored in the db
def latest_from_db():
    date = db.prefix("leaderboard/data/")[-1]
    table = serialize.deserialize(db[date])
    return table
