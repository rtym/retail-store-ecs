# Runs collect_evidence.py tolerating accounts with no Savings Plans history.
import runpy, sys
P = "~/workspace/aws-well-architected-and-analysis"
sys.path.insert(0, P)
from shared.awslib.collectors import cost
orig = cost.savings_plans_utilization
def tolerant(*a, **k):
    try:
        return orig(*a, **k)
    except Exception as e:
        if "DataUnavailable" in type(e).__name__:
            return {"Total": {}, "_note": "No Savings Plans data (DataUnavailableException)"}
        raise
cost.savings_plans_utilization = tolerant
_ta = cost.trusted_advisor_cost_checks
def ta(*a, **k):
    try:
        return _ta(*a, **k)
    except Exception as e:
        return [{"_note": f"Trusted Advisor unavailable: {type(e).__name__}"}]
cost.trusted_advisor_cost_checks = ta
sys.argv = [P + "/skills/aws-well-architected-review/scripts/collect_evidence.py"] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
