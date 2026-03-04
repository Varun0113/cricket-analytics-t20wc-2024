#Bowling Summary

import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MATCHES_CSV = "T20wc.csv"
OUTPUT_CSV = "bowling_summary_all.csv"

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
def load_matches(csv_file):
    with open(csv_file, newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("Link")]

# ---------------- FIX URL ----------------
def get_scorecard_url(link):
    return link.replace("live-cricket-scores", "live-cricket-scorecard")

# ---------------- FORCE FULL PAGE LOAD ----------------
def force_load_full_scorecard(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# ---------------- PARSE BOWLING (ROBUST STATE MACHINE) ----------------
def parse_bowling_from_text(text, match):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    bowling = []

    innings_index = -1
    in_bowling = False
    i = 0

    while i < len(lines):
        line = lines[i]

        # Start bowling section
        if line == "Bowler":
            innings_index += 1
            in_bowling = True
            i += 1
            continue

        # End of innings
        if line == "Fall of Wickets":
            in_bowling = False
            i += 1
            continue

        if not in_bowling or innings_index > 1:
            i += 1
            continue

        bowler = line

        # HARD FILTERS — prevents "O", "M", headers, garbage
        if (
            bowler in {"O", "M", "R", "W", "NB", "WD", "ECO", "Bowler"}
            or len(bowler) <= 2
            or bowler.isupper()
            or any(char.isdigit() for char in bowler)
        ):
            i += 1
            continue

        stats = []
        j = i + 1

        # Collect next numeric stats dynamically
        while j < len(lines) and len(stats) < 7:
            if re.fullmatch(r"\d+(\.\d+)?", lines[j]):
                stats.append(lines[j])
            j += 1

        if len(stats) == 7:
            overs, maidens, runs, wickets, no_balls, wides, economy = stats

            # 🔥 Correct team mapping
            bowling_team = match["Team2"] if innings_index == 0 else match["Team1"]

            bowling.append({
                "match": f"{match['Team1']} vs {match['Team2']}",
                "teamInnings": bowling_team,
                "bowlerName": bowler,
                "overs": overs,
                "maidens": maidens,
                "runs": runs,
                "wickets": wickets,
                "noBalls": no_balls,
                "wides": wides,
                "economy": economy
            })

            i = j  # jump past this bowler
        else:
            i += 1

    return bowling

# ---------------- SCRAPE BOWLING ----------------
def scrape_bowling(driver, match):
    url = get_scorecard_url(match["Link"])
    print("Opening:", url)
    driver.get(url)

    # Open scorecard tab
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Scorecard"))
    ).click()
    time.sleep(3)

    # 🔥 Force lazy-loaded innings to render
    force_load_full_scorecard(driver)

    page_text = driver.find_element(By.TAG_NAME, "body").text
    return parse_bowling_from_text(page_text, match)

# ---------------- SAVE CSV ----------------
def save_csv(data, filename):
    if not data:
        print("❌ No bowling data scraped.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"\n✅ Saved {len(data)} rows to {filename}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    driver = get_driver()
    matches = load_matches(MATCHES_CSV)

    all_bowling = []

    for i, match in enumerate(matches, 1):
        print("\n" + "=" * 60)
        print(f"MATCH {i}/{len(matches)}: {match['Team1']} vs {match['Team2']}")
        print("=" * 60)

        rows = scrape_bowling(driver, match)
        print(f"Bowling rows scraped: {len(rows)}")
        all_bowling.extend(rows)
        time.sleep(2)

    driver.quit()
    save_csv(all_bowling, OUTPUT_CSV)
