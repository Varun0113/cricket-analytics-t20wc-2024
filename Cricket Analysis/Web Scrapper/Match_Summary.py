#Match Summary

import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

URL = "https://www.cricbuzz.com/cricket-series/7476/icc-mens-t20-world-cup-2024/matches"

def scrape_cricbuzz_with_selenium(url):
    matches = []

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)

    match_links = driver.find_elements(By.CSS_SELECTOR, "a.w-full.bg-cbWhite.flex.flex-col")

    match_number = 1
    current_date = "N/A"

    for match_link in match_links:
        try:
            # ✅ INITIALIZE ALL FIELDS (CRITICAL FIX)
            match_data = {
                'Match_No': match_number,
                'Date': 'N/A',
                'Team1': 'N/A',
                'Score_Team1': 'N/A',
                'Team2': 'N/A',
                'Score_Team2': 'N/A',
                'Margin/Result': 'N/A',
                'Ground': 'N/A',
                'Link': 'N/A'
            }

            match_data['Link'] = match_link.get_attribute("href")

            try:
                date_elem = match_link.find_element(
                    By.XPATH,
                    "./preceding::div[contains(@class,'bg-cbGrpHdrBkg')][1]"
                )
                current_date = date_elem.text.strip()
            except:
                pass

            match_data['Date'] = current_date

            try:
                match_data['Ground'] = match_link.find_element(
                    By.CSS_SELECTOR, "span.text-xs"
                ).text.strip()
            except:
                pass

            teams = match_link.find_elements(By.CSS_SELECTOR, "div.flex.items-center.gap-2")
            if len(teams) >= 2:
                match_data['Team1'] = teams[0].text.strip()
                match_data['Team2'] = teams[1].text.strip()

            scores = match_link.find_elements(
                By.XPATH,
                ".//span[contains(@class,'font-medium') and contains(@class,'w-1/2') and contains(@class,'truncate')]"
            )

            if len(scores) >= 2:
                match_data['Score_Team1'] = scores[0].text.strip()
                match_data['Score_Team2'] = scores[1].text.strip()

            try:
                match_data['Margin/Result'] = match_link.find_element(
                    By.CLASS_NAME, "text-cbComplete"
                ).text.strip()
            except:
                pass

            matches.append(match_data)
            print(f"{match_number}. {match_data['Team1']} vs {match_data['Team2']}")
            match_number += 1

        except Exception as e:
            print("Skipped match:", e)

    driver.quit()
    return matches

def save_to_csv(matches, filename):
    fieldnames = [
        'Match_No', 'Date', 'Team1', 'Score_Team1',
        'Team2', 'Score_Team2', 'Margin/Result',
        'Ground', 'Link'
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for match in matches:
            writer.writerow(match)

def display_sample_data(matches, num_samples=3):
    print("\n" + "=" * 60)
    print("SAMPLE MATCHES")
    print("=" * 60)

    for match in matches[:num_samples]:
        print(f"\nMatch {match['Match_No']}")
        print("-" * 60)
        print(f"{match['Team1']} {match['Score_Team1']}  vs  {match['Team2']} {match['Score_Team2']}")
        print(f"Result : {match['Margin/Result']}")
        print(f"Ground : {match['Ground']}")
        print(f"Date   : {match['Date']}")

    print("=" * 60)

if __name__ == "__main__":
    matches = scrape_cricbuzz_with_selenium(URL)
    display_sample_data(matches)

    filename = f"t20wc.csv"
    save_to_csv(matches, filename)

    print(f"\n✓ Saved {len(matches)} matches to {filename}")
