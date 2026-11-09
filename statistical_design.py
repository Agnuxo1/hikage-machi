"""Exact design arithmetic; synthetic planning assumptions, no measured effect."""
import itertools
import json
import math
from pathlib import Path


def upper_binomial_tail(n, k, probability):
    return sum(math.comb(n,j)*probability**j*(1-probability)**(n-j) for j in range(k,n+1))


def sign_test_design(n, win_probability, alpha=0.025):
    critical=next((k for k in range(n+1) if upper_binomial_tail(n,k,0.5)<=alpha),None)
    return {"independent_units":n,"one_sided_alpha":alpha,"critical_wins":critical,
            "assumed_win_probability":win_probability,
            "power_under_assumption":0 if critical is None else upper_binomial_tail(n,critical,win_probability)}


def main():
    signed_sums=[sum(s*r for s,r in zip(signs,[1,2,3])) for signs in itertools.product([-1,1],repeat=3)]
    exact_p=sum(abs(s)>=6 for s in signed_sums)/len(signed_sums)
    assert exact_p==0.25
    rows=[sign_test_design(n,p) for n in [3,7,12,20,24,30] for p in [0.7,0.8,0.9]]
    sample=next(x for x in rows if x["independent_units"]==20 and x["assumed_win_probability"]==0.8)
    assert sample["critical_wins"]==15 and 0.8042<sample["power_under_assumption"]<0.8043
    out={"historical_n3_signed_rank":{"all_eight_signed_sums":signed_sums,"smallest_two_sided_exact_p":exact_p,"alpha005_attainable":False},
         "planning_only_sign_test_power":rows,
         "not_measured_effects":True,
         "warning":"These are sign-test planning calculations under independent Bernoulli wins, not power calculations for Wilcoxon and not evidence of actual performance."}
    path=Path(__file__).resolve().with_name("STATISTICAL_DESIGN_EVIDENCE.json")
    path.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"n3_minimum_two_sided_p":exact_p,"planning_example":sample,"confirmatory_sample_enrolled":False}))


if __name__=="__main__": main()
