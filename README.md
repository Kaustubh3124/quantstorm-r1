# QuantStorm R1 Bot

This repository contains the custom submission bot for QuantStorm 2026 Round 1.

## Submission file

`strategies/quantstorm_bot.py`

The bot follows the QuantStorm `Bot` interface with all five required methods:

- `reset`
- `bid`
- `quote`
- `respond`
- `use_transform`

The strategy uses the rulebook's five powers, the 24-TE budget, first-price auction shading, revealed-coin information, Foresight information, tight legal opening spreads, and state-dependent Transform decisions.

## Local validation

Place this file alongside the official QuantStorm project files and validate it with:

```bash
python backtester.py --validate strategies/quantstorm_bot.py
```

A normal duel can be run with:

```bash
python backtester.py --bot1 strategies/quantstorm_bot.py --bot2 strategies/rational.py
```

And isolated behaviour can be checked with:

```bash
python backtester.py --bot1 strategies/quantstorm_bot.py --bot2 strategies/rational.py --isolate
```

The official rulebook remains the authority for the tournament rules and submission requirements.