from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://hotel-example-site.takeyaqa.dev/ja/"

opts = Options()
# まずは目で見るためヘッドレスOFF
# 後で速く回すときは True に
# opts.add_argument("--headless=new")
opts.add_argument("--window-size=1280,900")

driver = webdriver.Chrome(options=opts)
try:
    driver.get(URL)
    print("[SMOKE] title:", driver.title)
    driver.save_screenshot("artifacts/smoke.png")
    print("[SMOKE] screenshot -> artifacts/smoke.png")
finally:
    driver.quit()
