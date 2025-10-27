from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage
import time

class PlansPage(BasePage):
    def open_from_top(self, base_url: str):
        """トップからリンクは使わず、/plans に直アクセス（確実）"""
        url = base_url.rstrip("/") + "/plans"
        self.driver.get(url)
        self.wait_dom_ready()
        # 「予約」ボタン候補（button/aどちらでもヒット）
        candidates = [
            (By.XPATH, "//button[contains(., '予約') or contains(., '予約する')]"),
            (By.XPATH, "//a[contains(., '予約') or contains(., '予約する')]"),
            (By.CSS_SELECTOR, "button[data-testid*='reserve'], a[role='button']"),
        ]
        self.wait_any_visible(candidates)
        return self

    def reserve_first_plan(self):
        """最初の『予約』を押し、新しいタブ/ウィンドウが開けば自動で切替える"""
        before = set(self.driver.window_handles)
        for loc in [
            (By.XPATH, "(//button[contains(., '予約') or contains(., '予約する')])[1]"),
            (By.XPATH, "(//a[contains(., '予約') or contains(., '予約する')])[1]"),
        ]:
            try:
                self.click(loc)
                break
            except Exception:
                continue

        # 新規タブ/ウィンドウに切替え（開かない場合もあるので柔軟に）
        for _ in range(20):  # 最大 ~10秒
            after = set(self.driver.window_handles)
            newly = list(after - before)
            if newly:
                self.driver.switch_to.window(newly[0])
                break
            time.sleep(0.5)
        return self

    # 内部ヘルパ：name候補とlabelキーワードで select/input のどちらにも対応
    def _set_select_or_input(self, name_candidates, value, label_keywords=None):
        # 1) name 属性で探す
        for name in name_candidates:
            try:
                el = self.wait_visible((By.NAME, name))
                try:
                    Select(el).select_by_value(str(value))
                except Exception:
                    el.clear(); el.send_keys(str(value))
                return True
            except Exception:
                pass

        # 2) label 文言から辿る（<label for> または 近傍のinput/select）
        if label_keywords:
            for kw in label_keywords:
                try:
                    lab = self.wait_visible((By.XPATH, f"//label[contains(., '{kw}')]"))
                    for_attr = lab.get_attribute("for")
                    if for_attr:
                        el = self.driver.find_element(By.ID, for_attr)
                    else:
                        el = lab.find_element(By.XPATH, ".//following::*[self::select or self::input][1]")
                    try:
                        Select(el).select_by_value(str(value))
                    except Exception:
                        el.clear(); el.send_keys(str(value))
                    return True
                except Exception:
                    continue
        return False

    def set_people_and_nights(self, adults=2, nights=1):
        """人数と泊数を設定（name/labelの違いに強い）"""
        ok1 = self._set_select_or_input(
            name_candidates=["adults", "adult", "guests", "num_adults", "guestCount"],
            value=adults,
            label_keywords=["大人", "人数", "ご利用人数", "宿泊人数"]
        )
        ok2 = self._set_select_or_input(
            name_candidates=["nights", "night", "stay_nights", "num_nights", "stayLength"],
            value=nights,
            label_keywords=["泊数", "宿泊数", "日数"]
        )

        # 合計金額の候補（先に見つかったものを採用）
        for loc in [
            (By.CSS_SELECTOR, ".total-price"),
            (By.CSS_SELECTOR, "[data-testid='total-price']"),
            (By.XPATH, "//*[contains(., '合計') and contains(., '¥')]"),
        ]:
            try:
                return self.wait_visible(loc).text
            except Exception:
                pass
        return ""

    # e2e/pages/plans_page.py

    def go_to_confirm(self):
        """送信/確認ボタンを広めの条件で探してクリック→見出し確認"""
        # 候補（順に試す）：type=submit / 「確認」含む / 「内容確認へ」/ 「次へ」系
        candidates = [
            (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"),
            (By.XPATH, "//button[contains(., '確認') or contains(., '内容確認') or contains(., '次へ') or contains(., '次に進む')]"),
            (By.XPATH, "//a[contains(., '確認') or contains(., '内容確認') or contains(., '次へ') or contains(., '次に進む')]"),
        ]

        # どれかが見えるまで待つ→JSフォールバック付きclick()で押す
        el, loc = self.wait_any_visible(candidates)
        self.click(loc)

        # ページ遷移/モーダル描画の完了待ち
        self.wait_dom_ready()

        # 到達判定も広めに（見出し or 文言）
        self.wait_any_visible([
            (By.XPATH, "//*[contains(., '予約内容の確認') or contains(., '内容の確認') or contains(., '確認画面')]")
        ])

