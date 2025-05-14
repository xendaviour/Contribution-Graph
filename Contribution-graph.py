import os
import subprocess
from datetime import datetime, timedelta
from collections import Counter
from colorama import init
import calendar

init()

COLORS = [
    "#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"
]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def rgb_escape(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"\033[48;2;{r};{g};{b}m  \033[0m"

def find_git_repos(root_path):
    git_repos = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        if ".git" in dirnames:
            git_repos.append(dirpath)
            dirnames.clear()
    return git_repos

def gather_commit_dates(repo_path):
    try:
        output = subprocess.check_output(
            ["git", "log", "--pretty=format:%ad", "--date=short"],
            cwd=repo_path,
            stderr=subprocess.DEVNULL,
        ).decode()
        return output.strip().split("\n")
    except subprocess.CalledProcessError:
        return []

# Step 1: Find repos and collect all commit dates
master_dir = os.getcwd()
all_dates = []

for repo in find_git_repos(master_dir):
    all_dates.extend(gather_commit_dates(repo))

commit_counts = Counter(all_dates)
total_commits = sum(commit_counts.values())

# Step 2: Build contribution grid
today = datetime(2025, 5, 14)  # Fixed date as per context
start = today - timedelta(weeks=53)

# Adjust start date to the nearest Monday to align weeks properly
start_weekday = start.weekday()
if start_weekday != 0:  # If not Monday
    start = start - timedelta(days=start_weekday)

weeks = [[] for _ in range(53)]
date_labels = []
used_months = set()

# Collect all commits into the grid
for i in range(7 * 53):
    date = start + timedelta(days=i)
    count = commit_counts.get(date.strftime("%Y-%m-%d"), 0)

    if count == 0:
        level = 0
    elif count < 3:
        level = 1
    elif count < 6:
        level = 2
    elif count < 10:
        level = 3
    else:
        level = 4

    block = rgb_escape(COLORS[level])
    week_index = (date - start).days // 7
    while len(weeks[week_index]) < 7:
        weeks[week_index].append(rgb_escape(COLORS[0]))
    weeks[week_index][date.weekday()] = block

    # Use original logic for month labels
    if date.day == 1 and date.month not in used_months:
        date_labels.append((week_index, calendar.month_abbr[date.month]))
        used_months.add(date.month)

# Step 3: Print calendar with labels and legend using original month positioning
month_line = "     "  # Space for day labels
last_pos = -1
for pos, name in date_labels:
    if pos - last_pos > 1 or last_pos == -1:  # Include first month
        if last_pos == -1:
            month_line += " " * (pos * 2) + name
        else:
            month_line += name.ljust((pos - last_pos) * 2)
        last_pos = pos

print(f"\nGitHub-style contribution graph ({total_commits} contributions in the last year)\n")
print(month_line)

for i, day in enumerate(DAYS):
    label = day if day in ["Mon", "Wed", "Fri"] else "   "
    row = f"{label} "
    for week in weeks:
        row += week[i] if i < len(week) else rgb_escape(COLORS[0])
    print(row)

legend = "\n    Less "
for color in COLORS:
    legend += rgb_escape(color)
legend += " More"
print(legend)
