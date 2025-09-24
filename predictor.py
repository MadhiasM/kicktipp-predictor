class Predictor:
    DRAW_THRESHOLD = 2.25  # Not to be used in knock out phase if result after extra time + penalties is used in the rules
    BIG_WIN_THRESHOLD = 7.5  # 5.25 for group stage, 8 for knockout?

    WIN = (
        2,
        1,
    )  # (2,1) for group stage, (1,0) for knockout stage # TODO: detect if knockout
    BIG_WIN = (2, 0)
    DRAW = (
        0,
        0,
    )  # 0:0 is used because the most realistic scenario for a draw is that both teams do not attack since a draw is sufficient for both (see Schande von Gijon)

    # TODO: Calculate it based on the mode (no_bias = 1; away_bias = (6/4 + 5/3 + 4/2) / 3)
    # TODO: https://www.kicktipp.de/sparta2526/spielregeln Get the points directly from kicktipp
    # Punkteregel: 2 - 6 Punkte
    #               Tendenz	Tordifferenz	Ergebnis
    # Heimsieg	    2	    3	            4
    # Unentschieden	4	    -	            6
    # Auswärtssieg	4	    5	            6
    POINTS = {
        "no_bias": {"home": [4, 3, 2], "away": [4, 3, 2]},
        "away_bias": {"home": [4, 3, 2], "away": [6, 5, 4]},
    }

    def __init__(self, mode="no_bias"):
        self.mode = mode
        self.points = self.POINTS[mode]
        self.bias = sum(
            a / b for a, b in zip(self.points["away"], self.points["home"])
        ) / len(self.points["home"])

    def forecast(self, odds: list):
        if self.mode == "no_bias":
            return self.forecast_no_bias(odds)
        elif self.mode == "away_bias":
            return self.forecast_away_bias(odds)

    def forecast_no_bias(
        self, odds: list
    ):  # TODO: replace home, away, odds by a class Match
        diff = odds[0] - odds[2]

        if odds[1] < self.DRAW_THRESHOLD:
            return self.DRAW
        elif abs(diff) < self.BIG_WIN_THRESHOLD:
            result = self.WIN
        else:
            result = self.BIG_WIN

        return result if diff < 0 else tuple(reversed(result))

    def forecast_away_bias(
        self, odds: list
    ):  # TODO: replace home, away, odds by a class Match
        # TODO: Refactor home draw and away odds outside of the function, maybe into __init__
        home_odds = odds[0]
        draw_odds = odds[1]
        away_odds = odds[2]

        diff = odds[0] - odds[2]

        # If away odds are below the bias threshold, bet on away team even if the odd is higher
        if away_odds < home_odds * self.bias:
            if draw_odds < self.DRAW_THRESHOLD:
                return tuple(reversed(self.DRAW))
            elif abs(diff) < self.BIG_WIN_THRESHOLD:
                return tuple(reversed(self.WIN))
            else:
                return tuple(reversed(self.BIG_WIN))
        else:
            # Fallback to no_bias logic
            return self.forecast_no_bias(odds)
