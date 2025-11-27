import csv
import time
import math
import os
from collections import defaultdict

# ----------------- globals & defaults -----------------

drug_reports = {}
adr_reports = {}
drugs = set()
adrs = set()

# default priors 
DEFAULT_G11 = 1.0
DEFAULT_ALP = 2.0
DEFAULT_BET = 2.0
DEFAULT_ALP1 = 1.0
DEFAULT_BET1 = 1.0

start = time.time()

# math functions 


def gamma_fucn(a, b, c, d, alp, alp1, bet, bet1, g11):
    N = a + b + c + d
    numerato = (N + alp) * (N + bet)
    denomo = (b + alp1) * (c + bet1)
    val = numerato / denomo
    val = g11 * val
    return val


def expectation(a, b, c, d, alp, alp1, bet, bet1, g11):
    N = a + b + c + d
    numearto = (a + g11) * (N + alp) * (N + bet)
    denomo = (
        N + gamma_fucn(a, b, c, d, alp, alp1, bet, bet1, g11)
    ) * (a + b + alp1) * (a + c + bet1)
    val = numearto / denomo
    return math.log(val, 2)


def variance_function(a, b, c, d, alp, alp1, bet, bet1, g11):
    logValue = 1 / (math.log(2, math.e) ** 2)
    N = a + b + c + d
    gam = gamma_fucn(a, b, c, d, alp, alp1, bet, bet1, g11)
    numerator = (N - a + gam - g11)
    d1 = (a + g11) * (1 + N + gam)
    d2num = (N - a - b + alp - alp1)
    d2den = (a + b + alp1) * (1 + N + alp)
    d2 = d2num / d2den
    d3num = (N - a - c + bet - bet1)
    d3den = (a + c + bet1) * (1 + N + bet)
    d3 = d3num / d3den
    denom = d1 + d2 + d3
    val = numerator / denom
    val = val * logValue
    return val


def standard_deviation(value):
    # guard against tiny negative due to floating-point noise
    if value < 0:
        value = 0.0
    return math.sqrt(value)


#data loading 


def drug_data(fname):
    """Fill drug_reports: report_id -> [drug, ...]"""
    with open(fname, mode="r", encoding="latin-1") as f:
        csv_reader = csv.reader(f, delimiter="$")
        next(csv_reader, None) 
        for l in csv_reader:
            if not l or len(l) <= 4:
                continue
            report_id = l[0]
            drug = l[4]
            if report_id in drug_reports:
                drug_reports[report_id].append(drug)
            else:
                drug_reports[report_id] = [drug]
            drugs.add(drug)


def adr_data(fname):
    """Fill adr_reports: report_id -> [adr, ...]"""
    with open(fname, mode="r", encoding="latin-1") as f:
        csv_reader = csv.reader(f, delimiter="$")
        next(csv_reader, None) 
        for l in csv_reader:
            if not l or len(l) <= 2:
                continue
            report_id = l[0]
            adr = l[2]
            if report_id in adr_reports:
                adr_reports[report_id].append(adr)
            else:
                adr_reports[report_id] = [adr]
            adrs.add(adr)


def func():
    return []


#load FAERS data

#use files
drug_data("data/drug_small.txt")
adr_data("data/adr_small.txt")

finaldic = {}
dcount = {}
acount = {}
n = 0

# only IDs that appear in both files
common_ids = set(drug_reports.keys()) & set(adr_reports.keys())

for i in common_ids:
    for bu in drug_reports[i]:
        if bu not in finaldic:
            finaldic[bu] = {}
        for k in adr_reports[i]:
            finaldic[bu][k] = finaldic[bu].get(k, 0) + 1
            acount[k] = acount.get(k, 0) + 1
            dcount[bu] = dcount.get(bu, 0) + 1
            n += 1

print("number of common reports:", len(common_ids))
print("hi")
with open("adr-drug.txt", "w+") as f:
    pass
print("bye")

#load priors (optional)

addic = defaultdict(lambda: defaultdict(func))

if os.path.exists("adr-drug.csv"):
    with open("adr-drug.csv", mode="r", encoding="latin-1") as f:
        csv_reader = csv.reader(f, delimiter="$")
        for l in csv_reader:
            if len(l) < 8:
                continue
            drug = l[0]
            adr = l[1]
            try:
                alp = float(l[3])
                alp1 = float(l[4])
                bet = float(l[5])
                bet1 = float(l[6])
                g11 = float(l[7])
            except ValueError:
                continue
            addic[drug][adr].append(alp)
            addic[drug][adr].append(alp1)
            addic[drug][adr].append(bet)
            addic[drug][adr].append(bet1)
            addic[drug][adr].append(g11)
else:
    print("Warning: adr-drug.csv not found, using default priors for all pairs.")

#main scoring loop

sl = 0  # strong
wl = 0  # weak
ml = 0  # moderate
nl = 0  # none

# store per-pair results here: (drug, adr) -> info dict
pair_results = {}

for drug in finaldic:
    for adr in finaldic[drug]:
        a = finaldic[drug][adr]
        b = dcount[drug] - a
        c = acount[adr] - a
        d = n - a - b - c

        params = addic.get(drug, {}).get(adr, None)
        if params is None or len(params) < 5:
            alp = DEFAULT_ALP
            alp1 = DEFAULT_ALP1
            bet = DEFAULT_BET
            bet1 = DEFAULT_BET1
            g11 = DEFAULT_G11
        else:
            alp, alp1, bet, bet1, g11 = params

        try:
            exp = expectation(a, b, c, d, alp, alp1, bet, bet1, g11)
            var = variance_function(a, b, c, d, alp, alp1, bet, bet1, g11)
        except (ZeroDivisionError, ValueError):
            # skip numerically unstable pairs
            continue

        std = standard_deviation(var)
        ans = exp - (2 * std)

        if 0 < ans <= 1.5:
            category = "weak"
            wl += 1
        elif 1.5 < ans <= 3.0:
            category = "moderate"
            ml += 1
        elif ans > 3.0:
            category = "strong"
            sl += 1
        else:
            category = "none"
            nl += 1

        pair_results[(drug, adr)] = {
            "drug": drug,
            "adr": adr,
            "a": a,
            "b": b,
            "c": c,
            "d": d,
            "exp": exp,
            "var": var,
            "std": std,
            "ans": ans,
            "category": category,
        }

print("answers")
print("weak    :", wl)
print("moderate:", ml)
print("strong  :", sl)
print("none    :", nl)

#show top-k strongest pairs

TOP_K = 20

# sort by ans descending
sorted_pairs = sorted(
    pair_results.values(),
    key=lambda x: x["ans"],
    reverse=True,
)

print("\nTop", TOP_K, "strongest (drug, ADR) pairs by adjusted score (ans):")
for i, info in enumerate(sorted_pairs[:TOP_K], start=1):
    print(
        f"{i:2d}. Drug: {info['drug']:<30} "
        f"ADR: {info['adr']:<40} "
        f"ans: {info['ans']:.4f}  category: {info['category']}"
    )

#query mode

print("\n--- Query mode ---")
print("You can now check a specific (drug, ADR) pair.")
print("Example: DRUG: ASPIRIN, ADR: GASTROINTESTINAL HAEMORRHAGE")
print("Press Enter with empty drug name to skip.\n")

q_drug = input("Enter drug name (exact as in data, or leave blank to skip): ").strip()
if q_drug:
    q_adr = input("Enter ADR name (exact as in data): ").strip()
    key = (q_drug, q_adr)
    if key in pair_results:
        info = pair_results[key]
        print("\nResult for pair:")
        print("Drug      :", info["drug"])
        print("ADR       :", info["adr"])
        print("a (both)  :", info["a"])
        print("b (drug only) :", info["b"])
        print("c (adr only)  :", info["c"])
        print("d (neither)   :", info["d"])
        print(f"Expectation (exp): {info['exp']:.4f}")
        print(f"Variance        : {info['var']:.6f}")
        print(f"Std dev         : {info['std']:.6f}")
        print(f"Adjusted score  : {info['ans']:.4f}")
        print(f"Category        : {info['category']}")
    else:
        print("\nThis (drug, ADR) pair was not observed in the data or was skipped due to instability.")

print("\nTime taken (s):", time.time() - start)
