import json
import time
import typing
import os
import re
from playwright.sync_api import sync_playwright


def get_overwolf_latest_logs_path(app: str = "Overwolf General GameEvents Provider", prefix: str | None = None) -> str:
    """Get the path to the latest overwolf logs supposing a specific path."""
    log_directory = os.path.expanduser(f"~\\AppData\\Local\\Overwolf\\Log\\Apps\\{app}")
    files = [os.path.join(log_directory, file) for file in os.listdir(log_directory) if prefix is None or file.startswith(prefix)]
    return max(files, key=lambda i: os.stat(i).st_mtime)


def event_reader(path: str | None = None) -> typing.Iterator[typing.Any]:
    """Yields new events shared by the Overwolf Game Events Service."""
    while True:
        current_path = path or get_overwolf_latest_logs_path()
        with open(current_path, encoding="utf-8") as file:
            while True:
                line = file.readline()
                # if no new info check if overwolf maybe created a new log file
                if not line:
                    path = get_overwolf_latest_logs_path()
                    if path != current_path:
                        break
                    else:
                        time.sleep(0.01)
                        continue

                match = re.search(r"(\d+-\d+-\d+ \d+:\d+:\d+,\d+) \((\w+)\) (<.+?> \(.+?\)) - \[(.+?)\] ([\w ]+)?(\{.+\})", line)
                if not match:
                    continue

                _time, _loglevel, _file, log_type, _log_text, raw_data = match.groups()
                data = json.loads(raw_data)

                # technically there's data in "InfoDBContainer" but it's a preprocessed copy
                if log_type == "PLUGIN INFO":
                    yield data


def get_tracker_played_with(player_ids: typing.Collection[str]) -> dict[str, typing.Any]:
    """Fetch the api.tracker.gg endpoint to get info of players this player has played with."""

    data: dict[str, typing.Any] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        for player in player_ids:
            page.goto(f"https://api.tracker.gg/api/v1/r6siege/stats/played-with/ubi/{player}")
            data[player] = json.loads(page.evaluate("() => document.body.innerText"))

        browser.close()

    return data


def calculate_teams(player_ids: typing.Collection[str], cutoff: int = 10) -> list[list[str]]:
    teams: list[set[str]] = []
    for player_id, player_data in get_tracker_played_with(player_ids).items():
        for played_with in player_data["data"]:
            other_player_id = played_with["profileId"]
            if other_player_id not in player_ids or played_with["count"] < cutoff:
                continue

            for team in teams:
                if player_id in team or other_player_id in team:
                    team |= {player_id, other_player_id}
                    break
            else:
                teams.append({player_id, other_player_id})

    return [list(i) for i in teams]


def get_player_information(expected_player_ids: list[str], path: str | None = None) -> dict[str, typing.Any]:
    """Searches the tracker log for player information."""
    path = path or get_overwolf_latest_logs_path("Rainbow 6 Siege Tracker", "background.html")
    with open(path, encoding="utf-8") as file:
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
            if "Bulk endpoint response: " in line:
                raw_data = json.loads(line.split("Bulk endpoint response: ")[1])
                data = {i["playerId"]: i for i in raw_data["data"]["playersInfo"]}
                if set(data.keys()) >= set(expected_player_ids):
                    return data


data: dict[str, typing.Any] = {}
teams: list[list[str]] = []
round_history: dict[str, dict[int, dict[str, str]]] = {}
current_round = 1
player_info: dict[str, typing.Any] = {}

for event in event_reader():
    event_key = event["key"]
    try:
        value = json.loads(event["value"])
    except json.decoder.JSONDecodeError:
        try:
            value = json.loads("[" + event["value"] + "]")
        except json.decoder.JSONDecodeError:
            value = event["value"]

    data[event_key] = value

    if event_key == "player_list_log":
        teams = calculate_teams([i["profile_id"] for i in value])
        player_info = get_player_information([i["profile_id"] for i in value])

    if event_key.startswith("roster_"):
        if not value:
            round_history = {}
            teams = []
            player_info = {}
            continue

        round_history.setdefault(event_key, {})[current_round] = value

    if event_key == "round_start_log":
        current_round += 1
    if event_key == "match_end_log":
        current_round = 1

    # render to screen
    if not event_key.startswith("roster_") and event_key not in ("player_list_log", "round_start_log"):
        continue

    os.system("cls")
    print("\033[1;36m== Players ==\033[0m")
    for player in player_info.values():
        print(
            f"\033[1;33m{f'{player["playerName"]} {f"({player['playerPrivacyName']})" if player["playerPrivacyName"] else ""}':35}\033[0m"
            f" - \033[1;32m{player['lifetimeStats']['matchesPlayed']:>4}\033[0m matches, \033[1;35m{player['lifetimeRankedStats']['bestRank']['name']:12}\033[0m"
            f" {player["playerId"]}"
        )

    print()
    print("\033[1;36m== Squads ==\033[0m")
    for team in teams:
        print("\033[1;34m- \033[0m" + ", ".join(f"\033[1;33m{player_info[i]['playerPrivacyName'] or player_info[i]['playerName']}\033[0m" for i in team))

    print()
    print("\033[1;36m== Round history ==\033[0m")
    for roster_id, player_history in sorted(round_history.items(), key=lambda i: i[0]):
        print(
            f"\033[1;33m{data[roster_id]['player']:16}\033[0m | "
            + " | ".join(
                f"\033[1;36m{round['operator'].title() if round['operator'] != 'NONE' else '':8}\033[0m"
                f" \033[1;32m{round['kills']:>2}\033[0m \033[1;31m{round['deaths']:>2}\033[0m \033[1;34m{round['assists']:>2}\033[0m"
                for round_num in range(10)
                if (round := player_history.get(round_num))
            )
        )
