# Name: Kaustubh Sharma
# College: BITS Pilani
# Roll Number: 2024xxxx

import random


POWER_VALUES = {
    "FORESIGHT": {1: 0.76, 2: 1.16, 3: 1.48, 4: 1.97, 5: 2.02},
    "TRICK_ROOM": {1: 1.14, 2: 0.00, 3: 0.00, 4: 0.60, 5: 0.52},
    "SUBSTITUTE": {1: 1.46, 2: 1.15, 3: 0.95, 4: 0.57, 5: 0.29},
    "STEALTH_ROCK": {1: 1.51, 2: 0.75, 3: 0.75, 4: 0.75, 5: 0.00},
    "TRANSFORM": {1: 1.58, 2: 1.24, 3: 1.31, 4: 0.00, 5: 0.00},
}

SHADE = 0.60
FLAT_THRESHOLD = 1


class Bot:
    name = "KaustubhR1"

    def reset(self, seat, config, seed):
        self.seat = seat
        self.config = config
        self.rng = random.Random(seed)
        self.opp_quotes = {}
        self.last_my_quote = None

    def _power_value(self, obs, power):
        return POWER_VALUES.get(power, {}).get(obs.round, 0.50)

    def _value(self, obs, quote=None):
        # Own revealed information is the base estimate.
        value = float(obs.k_mine)

        # Foresight directly reveals a sample from the opponent's revealed
        # coins, so use that signal when it is available.
        if obs.foresight:
            value += float(sum(obs.foresight))

        # If we are the taker, the maker's opening midpoint is a useful noisy
        # signal of their estimate of the hidden score.
        if quote is not None:
            midpoint = (quote[0] + quote[1]) / 2.0
            value = 0.65 * value + 0.35 * midpoint

        return value

    def bid(self, obs, offered):
        if not offered or obs.te_mine <= 0:
            return {}

        power = offered[0]
        value = self._power_value(obs, power)

        if power == "TRANSFORM":
            # Transform is most useful when our revealed hand is close to
            # neutral; swapping gives us access to a more informative hand.
            if abs(obs.k_mine) > FLAT_THRESHOLD:
                return {}

        fair_te = value / self.config.TE_SALVAGE
        bid = int(fair_te * SHADE)
        bid = max(0, min(bid, obs.te_mine))

        if bid == 0:
            return {}
        return {power: bid}

    def quote(self, obs):
        # Use the tightest legal spread. The midpoint is our estimate of S.
        value = round(self._value(obs))
        width = obs.final_cap
        low = value - width // 2
        high = low + width
        self.last_my_quote = (low, high)
        return (low, high)

    def respond(self, obs, quote, turn):
        bid, ask = quote
        value = self._value(obs, quote)

        buy_edge = value - ask
        sell_edge = bid - value

        # SUBSTITUTE makes taking a downside risk cheaper.
        if "SUBSTITUTE" in obs.powers_mine:
            sell_threshold = -1.0
        else:
            sell_threshold = 0.0

        if buy_edge > 0 and buy_edge >= sell_edge:
            return "ACCEPT_BUY"
        if sell_edge > sell_threshold and sell_edge > buy_edge:
            return "ACCEPT_SELL"

        width = ask - bid
        new_width = max(obs.final_cap, width - self.config.MIN_REDUCTION)

        if new_width >= width:
            return ("COUNTER", bid, ask)

        center = round(value)
        low = center - new_width // 2
        high = low + new_width

        if low < bid:
            low = bid
            high = low + new_width
        if high > ask:
            high = ask
            low = high - new_width

        return ("COUNTER", low, high)

    def use_transform(self, obs):
        # A balanced hand carries the most uncertainty, so swapping is useful.
        return abs(obs.k_mine) <= FLAT_THRESHOLD
