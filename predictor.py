class Predictor:
    # DRAW_THRESHOLD: float = 2.25  # Not to be used in knock out phase if result after extra time + penalties is used in the rules
    BIG_WIN_THRESHOLD: float  = 7.5  # 5.25 for group stage, 8 for knockout?
    HUGE_WIN_THRESHOLD: float  = 18  # 18-20 seems about right for a 3:0
    WIN: tuple[int, int] = (2, 1)  # (2,1) for group stage, (1,0) for knockout stage # TODO: detect if knockout
    HUGE_WIN: tuple[int, int] = (3, 0)
    BIG_WIN: tuple[int, int] = (2, 0)
    DRAW: tuple[int, int] = (0, 0)  # 0:0 is used because the most realistic scenario for a draw is that both teams do not attack since a draw is sufficient for both (see Schande von Gijon)
    # TODO: Check most probable draw result for leagues (in elimination games, it is 0:0)

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

    def __init__(self, mode: str = "no_bias", points: dict[str, list[int]] | None = None):
        self.mode = mode
        if points is None:
            self.points = self.POINTS[mode]
        else:
            self.points = points
        self.away_bias = sum(a / b for a, b in zip(self.points["away"], self.points["home"])) / len(self.points["home"])
        self.draw_bias = (
            (self.points['draw'][0] / self.points['home'][0]) +
            (self.points['draw'][2] / ((self.points['home'][1] + self.points['home'][2]) / 2))
        ) / 2

    def forecast(self, odds: list[float]) -> tuple[int, int]:
        home_odds, draw_odds, away_odds = odds

        home_weighted_odds = home_odds
        draw_weighted_odds = draw_odds / self.draw_bias
        away_weighted_odds = away_odds / self.away_bias


        if draw_weighted_odds <= min(home_weighted_odds, away_weighted_odds):
            return self.DRAW

        # Used to determine the height of the win bet, but not to determine if home or away should win
        mag_diff = abs(home_odds - away_odds)
        base = (
            self.WIN if mag_diff < self.BIG_WIN_THRESHOLD else
            self.BIG_WIN if mag_diff < self.HUGE_WIN_THRESHOLD else
            self.HUGE_WIN
        )

        # Used to determine if home or away should win, but not to determine the height of the win bet
        weighted_odds_diff = home_weighted_odds - away_weighted_odds

        return base if weighted_odds_diff < 0 else (base[1], base[0])
