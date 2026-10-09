"""GODI bike simulation — turnaround analysis.

Builds the four storytelling charts for the portfolio case from the extracted CSVs.
All numbers are ledger-bound to the simulation reports listed in ../data/SOURCES.md.
Run: python3 godi_turnaround.py (writes ../charts/*.png)
"""
import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
CHARTS = os.path.join(BASE, "charts")
os.makedirs(CHARTS, exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.figsize": (9, 5.2),
})

GODI_GREEN = "#2f7d4f"
ALERT_RED = "#c0392b"
SLATE = "#5d6d7e"
GOLD = "#b7950b"


def read_csv(name):
    with open(os.path.join(DATA, name), newline="") as f:
        return list(csv.DictReader(f))


def save(fig, name, caption):
    fig.text(0.01, 0.01, caption, fontsize=8, color="#7f8c8d", ha="left")
    fig.tight_layout(rect=[0, 0.04, 1, 0.96])
    fig.savefig(os.path.join(CHARTS, name), dpi=150)
    plt.close(fig)
    print("wrote", name)


# ---- data ----
fin = read_csv("quarterly_financials.csv")
quarters = [int(r["quarter"]) for r in fin]
op_profit = [int(r["operating_profit"]) for r in fin]
revenues = [int(r["revenues"]) for r in fin]
advertising = [int(r["advertising"]) for r in fin]
internet = [int(r["internet_marketing"]) for r in fin]

demand = read_csv("market_demand.csv")
godi_q3 = next(int(r["total"]) for r in demand if r["quarter"] == "3" and r["company"] == "GODI")
godi_q6 = next(int(r["total"]) for r in demand if r["quarter"] == "6" and r["company"] == "GODI")
mkt_q3 = next(int(r["total"]) for r in demand if r["quarter"] == "3" and r["company"] == "TOTAL")
mkt_q6 = next(int(r["total"]) for r in demand if r["quarter"] == "6" and r["company"] == "TOTAL")

SRC = "Source: six quarters of venture strategy simulation data (see data/SOURCES.md)"

# ---- chart 1: the turnaround (operating profit) ----
fig, ax = plt.subplots()
colors = [GODI_GREEN if v >= 0 else ALERT_RED for v in op_profit]
bars = ax.bar(quarters, op_profit, color=colors, edgecolor="white")
ax.axhline(0, color="black", linewidth=0.8)
for b, v in zip(bars, op_profit):
    ax.text(b.get_x() + b.get_width() / 2,
            v + (30000 if v >= 0 else -30000),
            f"${v/1000:,.0f}K",
            ha="center", va="bottom" if v >= 0 else "top", fontsize=10,
            fontweight="bold")
ax.set_xticks(quarters)
ax.set_xticklabels([f"Q{q}" for q in quarters])
ax.set_ylabel("Operating profit ($)")
ax.set_title("The bounce-back: operating profit by quarter", fontweight="bold", pad=12)
ax.annotate("Q3 collapse", xy=(3, -359704), xytext=(1.6, -560000),
            arrowprops=dict(arrowstyle="->", color=SLATE), color=SLATE)
ax.annotate("Audit pivot", xy=(4, -19707), xytext=(4.6, -260000),
            arrowprops=dict(arrowstyle="->", color=SLATE), color=SLATE)
ax.annotate("R&D investment quarter", xy=(5, -716766), xytext=(5.6, -560000),
            arrowprops=dict(arrowstyle="->", color=SLATE), color=SLATE)
ax.annotate("Profitable", xy=(6, 702512), xytext=(5.1, 480000),
            arrowprops=dict(arrowstyle="->", color=SLATE), color=SLATE,
            fontweight="bold")
save(fig, "chart1_profit_turnaround.png", SRC)

# ---- chart 2: revenue recovery ----
fig, ax = plt.subplots()
bars = ax.bar(quarters, revenues, color="#2e86c1", edgecolor="white")
for b, v in zip(bars, revenues):
    if v > 0:
        ax.text(b.get_x() + b.get_width() / 2, v + 60000,
                f"${v/1e6:.2f}M" if v >= 1e6 else f"${v/1000:.0f}K",
                ha="center", va="bottom", fontsize=10)
ax.set_xticks(quarters)
ax.set_xticklabels([f"Q{q}" for q in quarters])
ax.set_ylabel("Revenue ($)")
ax.set_title("Revenue: 13x from the Q3 trough to Q6", fontweight="bold", pad=12)
save(fig, "chart2_revenue_recovery.png", SRC)

# ---- chart 3: the marketing mix shift (the fix, in dollars) ----
qs = quarters[1:]  # Q2-Q6 have spend
adv = advertising[1:]
net = internet[1:]
fig, ax = plt.subplots()
x = range(len(qs))
w = 0.36
b1 = ax.bar([i - w/2 for i in x], adv, width=w, label="Traditional advertising",
            color="#5d6d7e", edgecolor="white")
b2 = ax.bar([i + w/2 for i in x], net, width=w, label="Internet marketing (SEM/SEO)",
            color=GOLD, edgecolor="white")
for b, v in list(zip(b1, adv)) + list(zip(b2, net)):
    if v >= 50000:
        ax.text(b.get_x() + b.get_width()/2, v + 4000, f"${v/1000:.0f}K",
                ha="center", va="bottom", fontsize=9)
ax.set_xticks(list(x))
ax.set_xticklabels([f"Q{q}" for q in qs])
ax.set_ylabel("Spend ($)")
ax.set_title("The fix, in dollars: digital goes from $0 to a real channel",
             fontweight="bold", pad=12)
ax.legend(frameon=False)
ax.annotate("$0 paid SEM\nin Q3", xy=(1 + w/2, 3000), xytext=(0.15, 150000),
            arrowprops=dict(arrowstyle="->", color=ALERT_RED), color=ALERT_RED,
            fontweight="bold")
save(fig, "chart3_marketing_mix_shift.png", SRC)

# ---- chart 4: denominator story (absolute growth vs share) ----
fig, ax = plt.subplots()
labels = ["Q3", "Q6"]
x = range(2)
w = 0.36
b1 = ax.bar([i - w/2 for i in x], [mkt_q3, mkt_q6], width=w,
            label="Total market demand", color="#aab7b8", edgecolor="white")
b2 = ax.bar([i + w/2 for i in x], [godi_q3, godi_q6], width=w,
            label="GODI demand", color=GODI_GREEN, edgecolor="white")
for b, v in list(zip(b1, [mkt_q3, mkt_q6])) + list(zip(b2, [godi_q3, godi_q6])):
    ax.text(b.get_x() + b.get_width()/2, v + 500, f"{v:,}",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_xticks(list(x))
ax.set_xticklabels([f"Q3\n({godi_q3/mkt_q3:.1%} share)", f"Q6\n({godi_q6/mkt_q6:.1%} share)"])
ax.set_ylabel("Units demanded")
ax.set_title("The denominator moved: market grew 5.9x, GODI demand grew 4.7x",
             fontweight="bold", pad=12)
ax.legend(frameon=False)
save(fig, "chart4_demand_vs_market.png", SRC)

# ---- chart 5: marketing efficiency (gross profit per marketing dollar) ----
# Q1 excluded: zero gross profit and zero marketing spend (undefined ratio).
eff_qs = [q for q in quarters if q >= 2]
eff = []
for r in fin:
    if int(r["quarter"]) >= 2:
        gp = int(r["gross_profit"])
        mkt = int(r["advertising"]) + int(r["internet_marketing"])
        eff.append(gp / mkt)
fig, ax = plt.subplots()
bars = ax.bar(eff_qs, eff, color=[ALERT_RED if v < 2 else "#2e86c1" for v in eff],
              edgecolor="white")
ax.axhline(1.5, color=SLATE, linestyle="--", linewidth=1)
ax.text(6.05, 1.5, "audit target: 1.5", va="center", fontsize=9, color=SLATE)
for b, v in zip(bars, eff):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.12, f"{v:.1f}x",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_xticks(eff_qs)
ax.set_xticklabels([f"Q{q}" for q in eff_qs])
ax.set_ylabel("Gross profit per $1 of marketing spend")
ax.set_title("Marketing efficiency: the reallocation, measured", fontweight="bold", pad=12)
ax.annotate("Collapse quarter", xy=(3, eff[1]), xytext=(1.7, 4.6),
            arrowprops=dict(arrowstyle="->", color=SLATE), color=SLATE)
save(fig, "chart5_marketing_efficiency.png",
     SRC + " · marketing = traditional advertising + internet marketing (SEM/SEO)")

print("done")
