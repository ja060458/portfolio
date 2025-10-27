import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from e2e.pages.login_page import LoginPage
from e2e.pages.plans_page import PlansPage

def build_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")  # まずは .env で false にして目視推奨
    opts.add_argument("--window-size=1280,900")
    return webdriver.Chrome(options=opts)  # Selenium Manager がドライバ解決

def main():
    load_dotenv()
    base_url = os.getenv("HOTEL_BASE_URL", "https://hotel-example-site.takeyaqa.dev/ja/")
    email = os.getenv("HOTEL_EMAIL")
    password = os.getenv("HOTEL_PASSWORD")
    headless = os.getenv("HEADLESS", "false").lower() == "true"  # まずは false で

    driver = build_driver(headless=headless)
    os.makedirs("artifacts", exist_ok=True)

    try:
        # 1) ログイン（メール/パス未設定ならゲスト進行）
        if email and password:
            LoginPage(driver).open_login(base_url).login(email, password)
            print("[OK] ログイン完了")
        else:
            driver.get(base_url)
            print("[INFO] ゲストで進行（.envにメール/パスを入れるとログイン）")

        # 2) プラン一覧 → 予約
        plans = PlansPage(driver).open_from_top(base_url)
        plans.reserve_first_plan()
        total = plans.set_people_and_nights(adults=2, nights=1)
        print(f"[OK] 合計金額: {total if total else '(未取得)'}")

        # 3) 内容確認へ
        plans.go_to_confirm()
        print("[OK] 予約内容の確認に到達")

        # 4) スクリーンショット保存
        out = os.path.join("artifacts", "confirm.png")
        driver.save_screenshot(out)
        print(f"[OK] スクリーンショット: {out}")

    except Exception as e:
        # 失敗時のダンプ（これがあると修正が早い）
        driver.save_screenshot(os.path.join("artifacts", "failed.png"))
        with open(os.path.join("artifacts", "page.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("[ERR] 失敗。artifacts/failed.png と artifacts/page.html を保存しました。")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
