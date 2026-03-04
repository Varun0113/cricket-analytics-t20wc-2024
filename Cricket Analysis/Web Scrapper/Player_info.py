import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SQUADS_URL = "https://www.cricbuzz.com/cricket-series/7476/icc-mens-t20-world-cup-2024/squads"
OUTPUT_CSV = "player_info_t20wc.csv"
TEST_LIMIT = None  # set None for all teams

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

# ---------------- PLAYER PROFILE ----------------
def scrape_player_profile(driver, profile_url, team, player_name):
    driver.get(profile_url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//h3[contains(text(),'PERSONAL INFORMATION')]")
        )
    )

    data = {
        "image": "",
        "player_name": player_name,
        "team": team,
        "role": "",
        "batting_style": "",
        "bowling_style": ""
    }

    # ---------- IMAGE ----------
    try:
        data["image"] = driver.find_element(
            By.CSS_SELECTOR, "img[alt]"
        ).get_attribute("src")
    except:
        pass

    # ---------- PLAYER NAME ----------
    try:
        data["player_name"] = driver.find_element(
            By.CSS_SELECTOR, "div.flex.flex-col h1"
        ).text.strip()
    except:
        pass

    # ---------- PERSONAL INFO (ROBUST) ----------
    info_blocks = driver.find_elements(
        By.XPATH,
        "//h3[contains(text(),'PERSONAL INFORMATION')]/following::div[contains(@class,'flex-col')]"
    )

    for block in info_blocks:
        try:
            label = block.find_element(By.XPATH, ".//div[1]").text.strip().upper()
            value = block.find_element(By.XPATH, ".//div[2]").text.strip()

            if label == "ROLE":
                data["role"] = value
            elif label == "BATTING STYLE":
                data["batting_style"] = value
            elif label == "BOWLING STYLE":
                data["bowling_style"] = value
        except:
            continue

    return data


# ---------------- SCRAPE SQUADS ----------------
def scrape_squads():
    driver = get_driver()
    driver.get(SQUADS_URL)
    time.sleep(3)

    all_players = []

    headers = driver.find_elements(
        By.CSS_SELECTOR, "div.w-full.px-4.py-2.tb\\:cursor-pointer"
    )

    if TEST_LIMIT:
        headers = headers[:TEST_LIMIT]

    print(f"\nFound {len(headers)} teams\n")

    for idx in range(len(headers)):
        driver.get(SQUADS_URL)
        time.sleep(2)

        headers = driver.find_elements(
            By.CSS_SELECTOR, "div.w-full.px-4.py-2.tb\\:cursor-pointer"
        )
        header = headers[idx]

        team_name = header.text.replace(" Squad", "").strip()
        print(f"\n[{idx+1}] Team: {team_name}")

        driver.execute_script("arguments[0].click();", header)
        time.sleep(2)

        links = driver.find_elements(By.XPATH, "//a[contains(@href,'/profiles/')]")

        players = []
        seen = set()

        for link in links:
            name = link.text.strip()
            url = link.get_attribute("href")

            if "(" in name:
                name = name.split("(")[0].strip()

            if name and url and url not in seen:
                seen.add(url)
                players.append((name, url))

        print(f"  Players found: {len(players)}")

        for name, url in players:
            print(f"   → {name}")
            pdata = scrape_player_profile(driver, url, team_name, name)
            all_players.append(pdata)

    driver.quit()
    return all_players

# ---------------- SAVE CSV ----------------
def save_csv(data):
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image",
                "player_name",
                "team",
                "role",
                "batting_style",
                "bowling_style"
            ]
        )
        writer.writeheader()
        writer.writerows(data)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("Starting player scraper...\n")
    players = scrape_squads()
    save_csv(players)
    print("\nScraping completed.")
