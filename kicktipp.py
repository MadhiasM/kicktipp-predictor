import argparse
import getpass
import os

# TODO: Only make bets that lie in the future
#from datetime import date

from predictor import Predictor
from robobrowser import RoboBrowser

# TODO: Catch if matchday is already over (by date/deadline? or by checking if form is stll there?)
# If matchday + match time + time before before current time, then skip match
# TODO: Distinguish between league and tournaments since they often have a difference in expected goals

URL = "https://www.kicktipp.de"
PROFILE = "/info/profil"
URL_LOGIN = f"{URL}/{PROFILE}/login"

COMMUNITY_URL = f"{URL}/{PROFILE}/meinetipprunden"
BET_SUBMISSION = "tippabgabe"
BET_SUBMISSION_FORM = f"{BET_SUBMISSION}Form"
BET_SUBMIT_BUTTON = "submitbutton"
GAME_BET_FORM = "spieltippForms"
HOME_BET = "heimTipp"
AWAY_BET = "gastTipp"

CONTENT = "kicktipp-content"

NOT_BETTABLE = "nichttippbar"

RULES = "spielregeln"
DEADLINE_RULE = "Tippabgaberegel"
RESULT_RULE = {
    "regulation": '"90 Minuten"',
    "extra time": '"nach Verlängerung"',
    "penalties": '"nach Elfmeterschießen"',
}
RESULT_HEADER = "Es wird das Ergebnis"

POINTS_RULE = {
    "Punkteregel: 2 - 4 Punkte": "no_bias",
    "Punkteregel: 2 - 6 Punkte": "away_bias",
}

LOGIN_FORM = {
    "username": "kennung",
    "password": "passwort",
    "id": "loginFormular"
}

LOGIN_RETURN = {
    "success": "messagebox success",
    "error": "messagebox errors"
}

def log_in(browser: RoboBrowser) -> str:
    username = input("E-mail address:  ")
    print(username)
    while len(username) == 0 or "@" not in username or "." not in username:
        print("Invalid E-mail. Try again")
        username = input("E-mail address:  ")

    password = getpass.getpass()
    while len(password) == 0:
        print("Password cannot be empty. Try again")
        password = getpass.getpass()

    browser.open(URL_LOGIN)
    login_form = browser.get_form(LOGIN_FORM["id"])
    if login_form:
        login_form[LOGIN_FORM["username"]] = username
        login_form[LOGIN_FORM["password"]] = password

        browser.submit_form(login_form)
    else:
        raise Exception("Could not get login form")

    login_success = browser.find(class_=LOGIN_RETURN["success"])
    if not login_success:
        login_error = browser.find(class_=LOGIN_RETURN["error"])
        print("Login failed:")
        print(login_error.get_text())
        log_in(browser)
    else:
        print("Login successfull:")
        print(login_success.get_text())
        return browser.session.cookies["login"]


def get_communities(browser: RoboBrowser) -> list[str]:
    c = [
        [cl["href"] for cl in cd.find_all("a", href=True)]
        for cd in browser.find(id=CONTENT)
        .find(class_="pagecontent")
        .find(class_="menu")
        .find_all(class_="level0")
    ]
    cm = []
    for i in c:
        cm.append(i[0].strip("/"))
    return cm


def get_matchdays(browser: RoboBrowser) -> list[str]:
    return [
        m["href"].split("=")[-1]
        for m in browser.find(id=CONTENT)
        .find(class_="dropdowncontent")
        .find_all("a", href=True)
    ]


# TODO: allow input of community in command line instead of all
# TODO: Decide if matchdays should be ints or strings (1 or '1'), so far str seems fine


def get_matches(browser: RoboBrowser) -> list[list[any]]:
    # match_content = browser.find(id='tippabgabeSpiele').select('td[class="nw"]')
    return [tr.find_all("td") for tr in browser.find("tbody").find_all("tr")]


def place_bets(browser: RoboBrowser, bets: dict[str, tuple[int, ...]]) -> bool:
    bet_form = browser.get_form(BET_SUBMISSION_FORM)

    for match_id in bets:
        home_goals_form = f"{GAME_BET_FORM}[{match_id}].{HOME_BET}"
        away_goals_form = f"{GAME_BET_FORM}[{match_id}].{AWAY_BET}"

        if bet_form:
            bet_form[home_goals_form] = str(bets[match_id][0])
            bet_form[away_goals_form] = str(bets[match_id][1])
        else:
            raise Exception("Could not get bet submission form")

    browser.submit_form(bet_form, submit=BET_SUBMIT_BUTTON)
    bet_submit_respone = str(browser.response)
    if bet_submit_respone == "<Response [200]>":
        return True
    else:
        return False


def get_rules(browser: RoboBrowser) -> any:
    return browser.find(id=CONTENT)


def get_deadline(browser: RoboBrowser) -> int: # Minutes
    rules = get_rules(browser)
    deadline = int(
        rules.find("h2", string=lambda t: DEADLINE_RULE in t.string).text.split(" ")[1]
    )
    return deadline


def get_mode(browser: RoboBrowser) -> list[any]:
    rules = get_rules(browser)
    # mode = rules.find('p', string = lambda t: RESULT_HEADER in t.string)
    mode = [rules.find_all("p")[i] for i in [1, 2]]
    return mode


def get_end_mode(browser: RoboBrowser) -> str:
    mode = get_mode(browser)
    end_mode = mode[1].find("b").text
    return end_mode


# Not yet used
def get_result_mode(browser: RoboBrowser) -> str:
    mode = get_mode(browser)
    end_mode = mode[0].find("b").text
    return end_mode


def get_point_mode(browser: RoboBrowser) -> str:
    rules = get_rules(browser)
    # Find the <h2> that starts with "Punkteregel"
    point_h2 = None
    for h2 in rules.find_all("h2"):
        if h2.get_text().strip().startswith("Punkteregel"):
            point_h2 = h2
            break
    if not point_h2:
        raise Exception("Could not find Punkteregel header")
    points = point_h2.get_text().strip()
    points_rule = POINTS_RULE.get(points)
    if not points_rule:
        raise Exception(f"Unknown points rule: {points}")
    return points_rule


def parse_points_table(browser: RoboBrowser) -> dict[str, list[int]]:
    rules = get_rules(browser)
    points = {}
    for row in rules.find("tbody").find_all("tr"):
        cells = row.find_all("td")
        label = cells[0].get_text(strip=True).lower()
        if "heimsieg" in label or "sieg" == label:
            key = "home"
        elif "auswärtssieg" in label:
            key = "away"
        elif "unentschieden" in label:
            key = "draw"
        else:
            continue
        pts = []
        for cell in cells[1:]:
            val = cell.get_text(strip=True)
            pts.append(int(val) if val.isdigit() else 0)
        points[key] = pts
    # If only "home" is present, use it for both home and away (no_bias case)
    if "home" in points and "away" not in points:
        points["away"] = points["home"]
    return points

def main(arguments: argparse.Namespace) -> None:
    browser = RoboBrowser(parser="html5lib")

    # TODO: Isolate in own module?
    if arguments.get_login_token:
        token = log_in(browser)
        print(token)
        # TODO: Get login token and permanently store as environment variable
        # os.environ['KICKTIPP'] = token
    elif arguments.use_login_token:
        token = arguments.use_login_token
    elif arguments.use_environment_variable_token:
        try:
            token = os.environ["KICKTIPP"]
            print(token)

        except KeyError as err:
            raise Exception(
                "Login token not found in environment variables. Use --get-login-token first and store as KICKTIPP in system environment variables."
            ) from err

    else:
        token = log_in(browser)
        # raise Exception('No input arguments given.') # TODO: Explain, which/how to use

    if token:
        browser.session.cookies["login"] = token
    else:
        raise Exception("No token found")

    # TODO: Get all communities
    browser.open(COMMUNITY_URL)
    communities = get_communities(browser)
    if not communities:
        raise Exception("No community found")

    # TODO: Get bet season (tippsaison ID) - not needed?
    # BET_SEASON_ID = '2262212'  # <input type="hidden" name="tippsaisonId" value="2262212">

    # DONE: Get number of matchdays (n(spieltagIndex))
    for community in communities:
        RULES_URL = f"{URL}/{community}/{RULES}"
        browser.open(RULES_URL)

        # deadline = get_deadline(browser)
        # end_mode = get_end_mode(browser)
        # result_mode = get_result_mode(browser)
        point_mode = get_point_mode(browser)
        points = parse_points_table(browser)
        # TODO: use deadline to check if game is bettable
        # TODO: use end_mode to adjust bets for 90 mins, extra time or penalties
        # TODO: use result mode to adjust bet to be result or tendency

        browser.open(f"{URL}/{community}/{BET_SUBMISSION}")
        matchdays = get_matchdays(browser)
        for matchday in matchdays:
            browser.open(f"{URL}/{community}/{BET_SUBMISSION}?spieltagIndex={matchday}")
            match_round = browser.find(
                "div", class_="prevnextTitle"
            ).get_text()  # match_round =

            matchday_bets = {}

            print(match_round)

            matches = get_matches(browser)

            for match in matches:
                match_time = match[0].get_text()  # TODO: Catch if no date is given yet?
                home = match[1].get_text()
                away = match[2].get_text()

                if match[3].get("class")[0] == NOT_BETTABLE:
                    print(f"{match_time}\n{home} vs. {away}\nOdds (H/D/A): N/A\nPredicted bet: Not bettable, maybe game lies in the past\n")
                    #print(match[3].get('class')[0])
                    continue
                match_id = match[3].find_all("input")[0].get("id").split("_")[1]
                # match_name = match[3].find_all('input')[0].get('name')  # TODO: Remove if not needed
                try:
                    # Home, draw, away odds
                    match_odds = [
                        float(o)
                        for o in match[4]
                        .get_text()
                        .strip("Quote: ")
                        .replace("/", "")
                        .split("  ")
                    ]
                except (
                    IndexError
                ) as err:  # Matchdays where no odds are available at all
                    print(f'No odds found for {match_round} in match {home} vs. {away} on {match_time}. Skipped.')
                    match_odds = "N/A"
                    match_bet = ("-", "-")
                except (
                    ValueError
                ) as err:  # Matchdays where odds are available only partially
                    match_odds = "N/A"
                    match_bet = ("-", "-")
                    # If no odds available, just bet 2:1 for now:
                    # match_bet = ('2','1')
                    # matchday_bets[match_id] = match_bet
                else:
                    match_predictor = Predictor(mode=point_mode, points=points)
                    match_bet = match_predictor.forecast(match_odds)
                    matchday_bets[match_id] = match_bet

                print(f"{match_time}\n{home} vs. {away}\nOdds (H/D/A): {match_odds}\nForecast bet: {match_bet[0]}:{match_bet[1]}\n")
            if matchday_bets:
                bets_placed = place_bets(browser, matchday_bets)
                if not bets_placed:
                    print(f"Could not place bets for {match_round}\n")
            else:
                print(f"No odds found for matchday {match_round}")
            print(f"{len(matchday_bets)} out of {len(matches)} bets for {match_round} placed.\n")  # TODO: Show how many bets are placed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optional app description")
    parser.add_argument("--get-login-token", action="store_true")
    parser.add_argument("--use-login-token")
    parser.add_argument("--use-environment-variable-token", action="store_true")

    args = parser.parse_args()

    main(args)
