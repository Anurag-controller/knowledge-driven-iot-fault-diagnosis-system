"""
Capture screenshots of all views by clicking sidebar navigation within the authenticated session.
"""

import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By

ARTIFACT_DIR = Path(r"C:\Users\anura\OneDrive\Documents\GitHub\knowledge-driven-iot-fault-diagnosis-system") / "screenshots"
BRAIN_DIR = Path(r"C:\Users\anura\.gemini\antigravity\brain\679b99c3-1e27-41e9-b8d7-54f55a0ecb0f")
BRAIN_DIR.mkdir(parents=True, exist_ok=True)

def main():
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1600,1100")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 1. Open Portal & Login
        print("Navigating to http://localhost:8501...")
        driver.get("http://localhost:8501")
        time.sleep(3)
        driver.save_screenshot(str(BRAIN_DIR / "1_Login_Portal.png"))
        print("Saved: 1_Login_Portal.png")
        
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) >= 2:
            inputs[0].clear()
            inputs[0].send_keys("admin")
            inputs[1].clear()
            inputs[1].send_keys("Admin@2026")
            
            for b in driver.find_elements(By.TAG_NAME, "button"):
                if "AUTHENTICATE" in b.text.upper() or "SIGN IN" in b.text.upper():
                    b.click()
                    break
            time.sleep(4)
        
        driver.save_screenshot(str(BRAIN_DIR / "2_Main_Portal.png"))
        print("Saved: 2_Main_Portal.png")

        # Page targets in order
        targets = [
            ("Overview", "3_Overview.png"),
            ("Live Monitoring", "4_Live_Monitoring.png"),
            ("Fault Diagnosis", "5_Fault_Diagnosis.png"),
            ("Historical Analytics", "6_Historical_Analytics.png"),
            ("Alerts", "7_Alerts.png"),
            ("Settings", "8_Settings.png"),
            ("Model Performance", "9_Model_Performance.png")
        ]

        for title, filename in targets:
            print(f"Searching sidebar for: {title}...")
            # Re-query sidebar links each time
            links = driver.find_elements(By.TAG_NAME, "a")
            clicked = False
            for l in links:
                if title.lower() in l.text.lower():
                    print(f"Clicking: {l.text} -> {filename}")
                    driver.execute_script("arguments[0].scrollIntoView(true);", l)
                    time.sleep(0.5)
                    l.click()
                    clicked = True
                    break
            
            if clicked:
                time.sleep(4)
                # Extra wait for charts/plotly to finish rendering
                save_path = str(BRAIN_DIR / filename)
                driver.save_screenshot(save_path)
                print(f"Successfully captured {filename}")
            else:
                print(f"Could not find link for {title}")

        print("Finished capturing all pages!")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
