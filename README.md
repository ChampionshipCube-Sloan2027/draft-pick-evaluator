# Draft Pick Evaluator

A decision-support tool for NBA draft picks. It ranks the 2027 prospect board against a team's stated needs, explains each recommendation from the scores it was built on, and includes a mock draft simulator for scenario testing.

**Track:** Best Apps and Agents
**Live app:** https://YOUR-APP-URL.streamlit.app
**Video:** https://youtu.be/YOUR-VIDEO-ID

## What it does

**Recommendation tool (main page).** Enter a team, pick number and positions of need. The app returns:
- A recommended prospect, with the points each factor contributed
- Up to three alternates, in order
- A close-call flag when the top two scores are within one point
- A downloadable PDF report
- Reference footage links and the author's scouting summary, for prospects where these are filled in

**Mock draft simulator (second page).** A seeded hypothetical draft order, with the AI teams picking by the same scoring. You can pick for your own team, review each pick, and compare alternative weightings in a Decision Lab. The simulator labels every AI team's needs as simulated, unless they have been researched.

## How the score works

Each prospect gets a score out of 100 from three parts in the main tool:

| Factor | Weight | How it is measured |
|---|---|---|
| ESPN rank | 0.65 | Rank 1 scores full marks, the last rank scores zero |
| BPM | 0.30 | Scaled on fixed bounds of -5 to +8, clipped to that range |
| Position of need | 0.05 | 1 if the prospect's position matches a team need, otherwise 0 |

The weights are a documented judgement, not fitted to results. They sum to 1. The pick number is shown for reference and does not change the score.

The simulator uses the same quality measures, and adds a team-fit component from positions and skills. Its weights are in `model_config.json`.

## Sensitivity

The top pick depends on how much the team's needs count. For the test case (need = SG, production weight fixed at 0.30):

| Rank weight | Need weight | Top pick | Score | Runner-up | Gap |
|---|---|---|---|---|---|
| 0.70 | 0.00 | Tyran Stokes | 96.3 | Jordan Smith Jr. | 4.5 |
| 0.65 | 0.05 | Jordan Smith Jr. | 91.9 | Tyran Stokes | 0.6 |
| 0.60 | 0.10 | Jordan Smith Jr. | 91.9 | Caleb Holt | 0.6 |
| 0.50 | 0.20 | Jordan Smith Jr. | 92.1 | Caleb Holt | 0.5 |

With no need weight, Tyran Stokes leads. Any positive need weight makes Jordan Smith Jr. the top pick, and three of the four settings are close calls. The tool's current setting of 0.05 is one of them, and the app flags it.

The full research and the skill-component test are in `sensitivity_report.md`. The skill component is off by default, because the scouting text is templated and its effect depends partly on placeholder team needs.

## Explanations

The main page builds its explanation from the scores. A template states the top prospect, the scoring breakdown, and the alternatives. A language model may add one connecting sentence, but that sentence is accepted only if every figure and name in it appears in the facts. Otherwise it is withheld and the template stands alone.

The simulator's trade-off claims work the same way: each claim must cite evidence, and each cited number, name and skill is checked against that evidence before it is shown.

The checks confirm that citations exist, that numbers and their signs match the cited text, and that names and skills are supported. They do not confirm that a cited passage means what the claim says. Read the passages beside each claim before relying on it.

## Data

- **Prospects:** `data/2027_nba_draft_big_board.csv`. ESPN rank entered manually from ESPN's big board, with the date checked. Stats are from each player's 2025-26 season, not their final college season.
- **Team needs:** `data/team_needs.csv`. Six teams (Chicago, Oklahoma City, San Antonio, Brooklyn, New York, Charlotte) have analyst assessments with stated confidence, drawn from the dated sources in `team_research.md`. The other 24 are labelled as simulated. Roster facts are pre-season snapshots as of 22 October 2026, and should be checked against nba.com before presenting.
- **Injuries:** `data/player_injuries.csv`. Shown only for players with a recorded source. Injury and availability reporting is work in progress: the figure shows reported status, not medical assessment.
- **Scouting summaries and video links:** entered by the author from watching the clips listed. The summary is labelled as the author's, not as a review by this project.

## Limitations

- **Small pool, one season.** One board, one season of stats, one team's needs for the main test.
- **No validation against outcomes.** The model has not been tested against how prospects performed later. No accuracy claim is made.
- **Cross-league comparison.** BPM from different leagues is treated as comparable. This affects prospects such as Luigi Suigo, whose BPM comes from the ABA League.
- **Production is one stat.** Defence, role, shooting profile and injury history are not scored in the main tool.
- **Simulated needs.** 24 of the 30 teams use simulated needs. Simulator results for those teams are scenarios, not predictions of how a real team would pick.
- **Browser coverage.** Checks cover the main flows, not every screen size.
- **Not yet built.** A roster-context view for the War Room.

## Setup

Requires Python 3.

Command-line recommendation:

Web interface:

Then open the **mock draft** page from the sidebar.

To use the language-model sentences, create a `.env` file in the project folder:

Without these, the explanations still appear, built from the scores.

## Tests

The suite covers the data loader, scoring, the draft engine (picks, replay and fingerprints), and the grounding checks on model claims.

## Files

- `app.py`: main recommendation page
- `pages/1_Mock_Draft.py`: mock draft simulator
- `scoring.py`: scoring and command-line interface
- `explain.py`: template explanation and checked connector sentence
- `draft_engine.py`, `grounding.py`, `model_config.json`: simulator logic, claim checks and settings
- `percentile.py`: colour helpers for the top-five chart and stat table
- `injury_map.py`: injury figure and records
- `pdf_export.py`: PDF report
- `sensitivity.py`, `sensitivity_report.md`: need-weight sensitivity
- `team_research.md`: sources and confidence for the six researched teams
- `FEEDBACK.md`: feedback on Nebius Token Factory and NVIDIA models
- `check_all.py`: checks the main tool's logic end to end
- `tests/`: test suite
- `data/`: prospect board, team needs, injuries

## Licence

MIT
