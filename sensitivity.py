import scoring
from data_loader import load_prospects

TEAM_NEEDS = ["SG"]
SETTINGS = [(0.70, 0.00), (0.65, 0.05), (0.60, 0.10), (0.50, 0.20)]  # (rank, need)
PROD_WEIGHT = 0.30

players = load_prospects(scoring.DATA_PATH)

print(f"Need: {', '.join(TEAM_NEEDS)} | production weight fixed at {PROD_WEIGHT}\n")
print(f"{'rank':>5} {'need':>5}  {'top pick':<22} {'score':>6}  {'runner-up':<22} {'gap':>5}")

for w_rank, w_need in SETTINGS:
    assert abs(w_rank + PROD_WEIGHT + w_need - 1.0) < 1e-9
    scoring.W_RANK = w_rank
    scoring.W_NEED = w_need

    top, alts, _, _ = scoring.recommend(players, TEAM_NEEDS)
    score, name, _ = top
    runner_score, runner_name, _ = alts[0]
    gap = score - runner_score

    print(f"{w_rank:>5.2f} {w_need:>5.2f}  {name:<22} {score:>6.1f}  {runner_name:<22} {gap:>5.1f}")
