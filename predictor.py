class Predictor():

    DRAW_THRESHOLD = 2.25 # Not to be used in knock out phase if result after extra time + penalties is used in the rules
    BIG_WIN_THRESHOLD = 7.5 # 5.25 for group stage, 8 for knockout?

    WIN = (1,0) # (2,1) for group stage, (1,0) for knockout stage # TODO: detect if knockout
    BIG_WIN = (2,0)
    DRAW = (0,0)  # 0:0 is used because the most realistic scenario for a draw is that both teams do not attack since a draw is sufficient for both (see Schande von Gijon)

    def forecast(self, odds: list): # TODO: replace home, away, odds by a class Match
        diff = odds[0] - odds[2]
        
        if odds[1] < self.DRAW_THRESHOLD:
            return self.DRAW
        elif abs(diff) < self.BIG_WIN_THRESHOLD:
            result = self.WIN
        else:
            result = self.BIG_WIN
            
        return result if diff < 0 else tuple(reversed(result))
