class Predictor:
    DRAW_THRESHOLD: float = 2.25  # Not to be used in knock out phase if result after extra time + penalties is used in the rules
    BIG_WIN_THRESHOLD: float  = 7.5  # 5.25 for group stage, 8 for knockout?
    HUGE_WIN_THRESHOLD: float  = 18  # 18-20 seems about right for a 3:0
    WIN: tuple[int, int] = (2, 1)  # (2,1) for group stage, (1,0) for knockout stage # TODO: detect if knockout
    HUGE_WIN: tuple[int, int] = (3, 0)
    BIG_WIN: tuple[int, int] = (2, 0)
    DRAW: tuple[int, int] = (0, 0)  # 0:0 is used because the most realistic scenario for a draw is that both teams do not attack since a draw is sufficient for both (see Schande von Gijon)

    # TODO: Calculate it based on the mode (no_bias = 1; away_bias = (6/4 + 5/3 + 4/2) / 3)
    # TODO: https://www.kicktipp.de/sparta2526/spielregeln Get the points directly from kicktipp
    # Punkteregel: 2 - 6 Punkte
    #               Tendenz	Tordifferenz	Ergebnis
    # Heimsieg	    2	    3	            4
    # Unentschieden	4	    -	            6
    # Auswärtssieg	4	    5	            6

    # This is only used as a fallback if it cannot be parsed from the website
    POINTS: dict[str, dict[str, list[int]]] = {
        "no_bias": {
            "home": [4, 3, 2],
            "away": [4, 3, 2],
            "draw": [6, 4, 4] # Not used currently, but there for completeness. Note that technically, there are only 2 variants for a draw, but the difference is added here for completeness
        },
        "away_bias": {
            "home": [4, 3, 2],
            "away": [6, 5, 4],
            "draw": [6, 4, 4] # Not used currently, but there for completeness. Note that technically, there are only 2 variants for a draw, but the difference is added here for completeness
        }
    }

    def __init__(self, mode: str = "no_bias", points: dict[str, list[int]] = None):
        self.mode = mode
        if points is None:
            self.points = self.POINTS[mode]
        else:
            self.points = points
        self.bias = sum(a / b for a, b in zip(self.points["away"], self.points["home"])) / len(self.points["home"])

    def forecast(self, odds: list[float]) -> tuple[int, int]:
        home_odds, draw_odds, away_odds = odds
        odds_diff = home_odds - away_odds

        if draw_odds < self.DRAW_THRESHOLD:
            return self.DRAW
        elif away_odds < home_odds * self.bias:
            # Favor away win
            if abs(odds_diff) < self.BIG_WIN_THRESHOLD:
                return tuple(reversed(self.WIN))
            elif abs(odds_diff) < self.HUGE_WIN_THRESHOLD:
                return tuple(reversed(self.BIG_WIN))
            else:
                return tuple(reversed(self.HUGE_WIN))
        elif abs(odds_diff) < self.BIG_WIN_THRESHOLD:
            return self.WIN
        elif abs(odds_diff) < self.HUGE_WIN_THRESHOLD:
            return self.BIG_WIN
        else:
            return self.HUGE_WIN
