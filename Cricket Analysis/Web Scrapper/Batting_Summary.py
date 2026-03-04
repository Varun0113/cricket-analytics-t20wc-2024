#Batting Summary 

import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MATCHES_CSV = "T20wc.csv"
OUTPUT_CSV = "batting_summary.csv"
TEST_LIMIT = None

# ---------------- DRIVER ----------------
def get_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)

# ---------------- LOAD MATCHES ----------------
def load_matches(csv_file, limit):
    matches = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("Link"):
                matches.append(row)
            if limit and len(matches) == limit:
                break
    return matches

# ---------------- FIX URL ----------------
def get_scorecard_url(link):
    return link.replace("live-cricket-scores", "live-cricket-scorecard")

# ---------------- OPEN SCORECARD ----------------
def open_scorecard(driver):
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Scorecard"))
    ).click()
    time.sleep(3)

# ---------------- FORCE FULL LOAD ----------------
def force_load_full_scorecard(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# ---------------- PARSE BATTING (FIXED TEAM LOGIC) ----------------
def parse_batting_from_text(text, match):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    batting = []

    innings_index = -1   # 0 = Team1, 1 = Team2
    in_batting = False
    batting_pos = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Start of a batting innings
        if line == "Batter":
            innings_index += 1
            in_batting = True
            batting_pos = 0
            i += 1
            continue

        # End of batting innings
        if line in ["Extras", "Total", "Did not Bat", "Bowler"]:
            in_batting = False
            i += 1
            continue

        if not in_batting or innings_index > 1:
            i += 1
            continue

        batsman = line

        # Filter invalid names
        if (
            len(batsman) <= 2
            or batsman.isupper()
            or any(char.isdigit() for char in batsman)
        ):
            i += 1
            continue

        stats = []
        dismissal_parts = []
        j = i + 1

        # Collect dismissal + numeric stats
        while j < len(lines) and len(stats) < 5:
            token = lines[j]
            if re.fullmatch(r"\d+(\.\d+)?", token):
                stats.append(token)
            else:
                dismissal_parts.append(token)
            j += 1

        if len(stats) == 5:
            runs, balls, fours, sixes, sr = stats
            dismissal = " ".join(dismissal_parts).strip()

            batting_pos += 1

            team_innings = match["Team1"] if innings_index == 0 else match["Team2"]

            batting.append({
                "match": f"{match['Team1']} vs {match['Team2']}",
                "teamInnings": team_innings,
                "battingPos": batting_pos,
                "batsmanName": batsman,
                "dismissal": dismissal,
                "runs": runs,
                "balls": balls,
                "4s": fours,
                "6s": sixes,
                "SR": sr
            })

            i = j
        else:
            i += 1

    return batting

# ---------------- SCRAPE BATTING ----------------
def scrape_batting(driver, match):
    url = get_scorecard_url(match["Link"])
    print("Opening:", url)

    driver.get(url)
    open_scorecard(driver)
    force_load_full_scorecard(driver)

    text = driver.find_element(By.TAG_NAME, "body").text
    return parse_batting_from_text(text, match)

# ---------------- SAVE CSV ----------------
def save_csv(data, filename):
    if not data:
        print("❌ No batting data scraped.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"\n✅ Saved {len(data)} rows to {filename}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    driver = get_driver()
    matches = load_matches(MATCHES_CSV, TEST_LIMIT)

    all_batting = []

    for i, match in enumerate(matches, 1):
        print("\n" + "=" * 60)
        print(f"MATCH {i}/{len(matches)}: {match['Team1']} vs {match['Team2']}")
        print("=" * 60)

        rows = scrape_batting(driver, match)
        print(f"Batting rows scraped: {len(rows)}")
        all_batting.extend(rows)
        time.sleep(2)

    driver.quit()
    save_csv(all_batting, OUTPUT_CSV)


