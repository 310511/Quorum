import json
import sys

path = sys.argv[1]
d = json.load(open(path, encoding="utf-8"))
for mode in ("raw", "structured"):
    print("===", mode)
    for e in d["per_pair"][mode]:
        wrong = "  WRONG" if e["policy_C"] not in ("escalate", e["ground_truth"]) else ""
        votes = {
            m: (v["verdict"], round(v["rationale_score"], 2), v["confidence"])
            for m, v in e["model_verdicts"].items()
        }
        print(
            f"{e['pair'][:48]:50} truth={e['ground_truth']:12} "
            f"C={e['policy_C']:12} rule={e['policy_C_rule']:24}{wrong}"
        )
        print("   ", votes)
