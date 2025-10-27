from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

DEFAULT_TIMEOUT = 10  # Ajax考慮で少し長め

class BasePage:
    def __init__(self, driver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_visible(self, locator):
        """locator の要素が可視になるまで待つ"""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator):
        """locator の要素がクリック可能になるまで待つ"""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_dom_ready(self):
        """document.readyState == 'complete' になるまで待つ"""
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def click(self, locator):
        """通常クリック→ダメならJSクリックのフォールバック"""
        try:
            self.wait_clickable(locator).click()
            return
        except Exception:
            el = self.wait_visible(locator)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            self.driver.execute_script("arguments[0].click();", el)

    def fill(self, locator, text: str):
        """テキスト入力（既存値クリア）"""
        el = self.wait_visible(locator)
        el.clear()
        el.send_keys(text)
        return el

    def wait_any_visible(self, locators):
        """複数候補のうち、最初に可視になった要素を返す"""
        last_err = None
        for loc in locators:
            try:
                el = self.wait_visible(loc)
                return el, loc
            except Exception as e:
                last_err = e
        raise last_err or TimeoutException("None of the locators became visible")
