import datetime
import heapq
import json
import time
import typing
import os
import re
from playwright.sync_api import sync_playwright

OverwolfRawLogType = tuple[str, str, str, str | None, str | None, str]


def log_reader(path: str) -> typing.Iterator[OverwolfRawLogType | None]:
    """Yields new events shared by the Overwolf Game Events Service. Only reads events containing JSON."""
    with open(path, encoding="utf-8") as file:
        while True:
            line = file.readline()

            if not line:
                yield None
                continue

            match = re.search(r"(\d+-\d+-\d+ \d+:\d+:\d+,\d+) \((\w+)\) (<.+?> \(.+?\)) - (?:\[(.+?)\] )?(?:(.+?) )?(\{\".+\}|\[[\"\{].+\])", line)
            if not match:
                continue

            yield tuple(match.groups())  # type: ignore


def bulk_log_reader(directories: list[str], max_age: int | None = None) -> typing.Iterator[OverwolfRawLogType]:
    """
    Continuously reads new logs from files in the given directories
    and yields parsed log entries in chronological order.
    """
    seen_files: set[str] = set()
    iterators: list[tuple[typing.Iterator[OverwolfRawLogType | None], str]] = []
    heap: list[tuple[tuple[str, int], OverwolfRawLogType]] = []

    while True:
        for directory in directories:
            for entry in os.scandir(directory):
                if entry.path not in seen_files and (max_age is None or time.time() - entry.stat().st_mtime <= max_age):
                    seen_files.add(entry.path)
                    iterators.append((log_reader(entry.path), entry.path))

        for it, _ in iterators:
            while True:
                entry = next(it)
                if entry is None:
                    break
                heapq.heappush(heap, ((entry[0], len(heap)), entry))

        if heap:
            _, entry = heapq.heappop(heap)
            yield entry
        else:
            time.sleep(0.01)


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


OVERWOLF_APPS_LOG_DIR = os.path.expanduser("~\\AppData\\Local\\Overwolf\\Log\\Apps")
MAX_LOG_AGE = 600
TEAM_COLORS = (("34", "36", "35"), ("33", "31", "32"), ("90", "90", "90"))

data: dict[str, typing.Any] = {}
teams: list[list[str]] = []
round_history: dict[str, dict[int, dict[str, str]]] = {}
current_round = 1
player_info: dict[str, typing.Any] = {}
player_colors: dict[str, str] = {}

directories = [os.path.join(OVERWOLF_APPS_LOG_DIR, "Rainbow 6 Siege Tracker"), os.path.join(OVERWOLF_APPS_LOG_DIR, "Overwolf General GameEvents Provider")]
for timestamp, _loglevel, _source, log_type, log_text, raw_data in bulk_log_reader(directories, MAX_LOG_AGE):
    print(timestamp, end="\r")
    if timestamp < (datetime.datetime.now() - datetime.timedelta(seconds=MAX_LOG_AGE)).isoformat(sep=" "):
        continue

    if log_type == "Tracker Network Service" and log_text and log_text.startswith("Bulk endpoint response"):
        player_info = {i["playerId"]: i for i in json.loads(raw_data)["data"]["playersInfo"]}

    if log_type == "PLUGIN INFO":
        event = json.loads(raw_data)
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
            player_colors = {player["profile_id"]: TEAM_COLORS[player["team_id"]][0] for player in data["player_list_log"]}
            taken_colors: list[int] = [0, 0]
            for team in teams:
                team_number = None
                for player_id in team:
                    for player in data["player_list_log"]:
                        if player["profile_id"] == player_id:
                            team_number = player["team_id"]

                if team_number is None:
                    continue

                taken_colors[team_number] += 1
                for player_id in team:
                    player_colors[player_id] = TEAM_COLORS[team_number][taken_colors[team_number]]

        if event_key.startswith("roster_"):
            if not value:
                round_history = {}
                teams = []
                player_info = {}
                player_colors = {}
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
        print(timestamp)
        print("\033[1;36m== Players ==\033[0m")
        for player in sorted(player_info.values(), key=lambda i: player_colors.get(i["playerId"], "90")):
            print(
                f"\033[1;{player_colors.get(player['playerId'], '90')}m{f'{player["playerName"]} {f"({player['playerPrivacyName']})" if player["playerPrivacyName"] else ""}':35}\033[0m"
                f" - \033[1;32m{player['lifetimeStats']['matchesPlayed'] if player.get('lifetimeStats') else 0:>4}\033[0m matches, \033[1;35m{player['lifetimeRankedStats']['bestRank']['name'] if player.get('lifetimeRankedStats') else "None":12}\033[0m"
                f" {player['playerId']}"
            )

        print()
        print("\033[1;36m== Squads ==\033[0m")
        for team in teams:
            print(
                "- "
                + ", ".join(
                    (
                        f"\033[1;{player_colors[player_id]}m{player_info[player_id]['playerPrivacyName'] or player_info[player_id]['playerName']}\033[0m"
                        if player_id in player_info
                        else "???"
                    )
                    for player_id in team
                )
            )

        print()
        print("\033[1;36m== Round history ==\033[0m")
        for roster_id, player_history in sorted(round_history.items(), key=lambda i: (data[i[0]]["team"], data[i[0]]["score"]), reverse=True):
            print(
                f"\033[1;33m{data[roster_id]['player']:16}\033[0m | "
                + " | ".join(
                    f"\033[1;36m{round['operator'].title() if round['operator'] != 'NONE' else '':8}\033[0m"
                    f" \033[1;32m{round['kills']:>2}\033[0m \033[1;31m{round['deaths']:>2}\033[0m \033[1;34m{round['assists']:>2}\033[0m"
                    if (round := player_history.get(round_num))
                    else " " * 17
                    for round_num in range(1, 10)
                )
            )
