# Draft Pick Evaluator

A decision-support tool that ranks prospects for an NBA team's draft pick. It takes the team's positional needs, scores each prospect on ESPN rank, production and fit, and lists alternates in order. The tool is a transparent scoring model, not a validated prediction system.

**Track:** Best Apps and Agents
**Status:** Scoring engine and command-line interface working. Web interface and Nemotron explanation step in progress.

## What it does

Given a team's needs and any prospects already taken, the tool returns:

1. A recommended prospect, with the points each factor contributed.
2. Up to three alternates, in order.
3. A close-call flag when the top two scores are within one point.
4. A list of prospects excluded because no BPM is recorded.

## How the score works

Each prospect gets a score out of 100 from three parts:

| Factor | Weight | How it's measured |
|---|---|---|
| Consensus | 0.65 | ESPN rank, scaled so rank 1 scores full marks and the last rank scores zero |
| Production | 0.30 | BPM, scaled between the lowest and highest BPM in the pool |
| Fit | 0.05 | 1 if the prospect's position matches a team need, otherwise 0 |

The weights are a documented judgement, not fitted to results. They sum to 1.

Positions with a slash, such as `PG/SG`, count for either need.

Production is scaled across the pool, so the top BPM always scores full points and the lowest scores zero. Scores therefore depend on who else is in the pool.

## Sensitivity to the need weight

The top pick depends on how much the team's needs count. Test case: need = SG, production weight fixed at 0.30.

| Rank weight | Need weight | Top pick | Score | Runner-up | Gap |
|---|---|---|---|---|---|
| 0.70 | 0.00 | Tyran Stokes | 95.3 | Braylon Mullins | 6.0 |
| 0.65 | 0.05 | Tyran Stokes | 90.3 | Braylon Mullins | 0.2 |
| 0.60 | 0.10 | Braylon Mullins | 90.8 | Jordan Smith Jr. | 5.1 |
| 0.50 | 0.20 | Braylon Mullins | 92.4 | Caleb Holt | 6.4 |

The top pick changes between need weights of 0.05 and 0.10. The current setting of 0.05 sits at that boundary, so the output reports a close call in that case.

Reproduce this table with `python3 sensitivity.py`.

## Data

Prospect data is in `data/2027_nba_draft_big_board.csv`, covering the 2027 draft class.

- **Stats season:** 2025–26, each player's most recent season before the 2026–27 season. This is not their final college season.
- **ESPN rank:** entered manually from ESPN's big board, with the date checked in each row.
- **Leagues:** the file mixes NCAA, G League, EuroLeague, ABA League, ACB and LNB Élite players. Stats from different leagues are not directly comparable. The league is recorded for each row, but the scoring does not adjust for it.
- **Missing BPM:** six prospects have no BPM recorded. They are kept in the file and excluded from the recommendation. The output lists them.
- **Ages:** calculated to the 2027 draft date.
- **Sources:** some rows come from sources other than the rest of the file. Check the `source` column for each row.

## Limitations

- **One team, one need, one pool.** The sensitivity table shows how the output responds to the weights, not whether any pick is correct.
- **No validation yet.** The model has not been tested against outcomes. The 2020–2025 historical set exists, but its outcome labels are still descriptive rather than rule-based, so no accuracy claim is made.
- **Cross-league comparison.** BPM from different leagues is treated as comparable. This affects prospects such as Luigi Suigo, whose BPM comes from the ABA League.
- **Pick number is not used.** It appears in the output but does not change the score.
- **Production is one stat.** Defence, role, shooting profile and injury history are not scored.

## Setup

Requires Python 3. No external packages are needed for the command-line tool.

```
python3 scoring.py --team "Team name" --pick 1 --needs PG C --taken "Player Name"
```

Arguments:

- `--team`: team name, shown in the output
- `--pick`: pick number, shown in the output only
- `--needs`: one or more position codes the team needs
- `--taken`: names of players already picked, in quotes

## Files

- `scoring.py`: scoring and command-line interface
- `data_loader.py`: loads and checks the CSV
- `sensitivity.py`: runs the need-weight sensitivity table
- `data/2027_nba_draft_big_board.csv`: prospect data

## Licence

MIT
