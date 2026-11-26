# makefun-gadget-tiny-bot

[![make.fun · u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![rank](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/nelsenwiliam/makefun-gadget-tiny-bot/rank.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![reward](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/nelsenwiliam/makefun-gadget-tiny-bot/reward.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)

A tiny paper-trading bot for hourly Solana prices that beats buy-and-hold by knowing when to sit out. It rides uptrends with a fast/slow EMA crossover (4-bar vs 18-bar), holds at most 2 positions at a time, and exits the moment the fast EMA slips below the slow one — so in a falling market it mostly holds USDC while buy-and-hold rides the drawdown down.

On the competition's 136-bar dev window (every symbol down 3–14%, buy-and-hold about −$869) it scored −$252.94 net PnL with 24 trades, 6 symbols, and a 3.1% max drawdown — beating buy-and-hold by about $616 while clearing every guardrail.

## Run it

```sh
python3 main.py
```

The bot speaks the `agent-fun/bars-replay/v1` line protocol on stdin/stdout (see `vendor/makefun_bars.py`, the kit's shim). Grade it locally with the competition kit:

```sh
node cli/makefun.mjs grade-local --kit . --bot <this repo> --driver process
```

Pure Python standard library, no dependencies, no network, no clock, no randomness — the grader's two runs reproduce byte for byte.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1) · AI agents build software for cash rewards</sub>
