from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    LINK_LOGIN = (By.LINK_TEXT, "ログイン")
    INPUT_EMAIL = (By.CSS_SELECTOR, 'input[type="email"]')
    INPUT_PASSWORD = (By.CSS_SELECTOR, 'input[type="password"]')
    BTN_LOGIN = (By.XPATH, "//button[contains(normalize-space(.), 'ログイン')]")
    LINK_MYPAGE = (By.LINK_TEXT, "マイページ")

    def open_login(self, base_url: str):
        self.driver.get(base_url)
        self.click(self.LINK_LOGIN)
        return self

    def login(self, email: str, password: str):
        self.fill(self.INPUT_EMAIL, email)
        self.fill(self.INPUT_PASSWORD, password)
        self.click(self.BTN_LOGIN)
        # 成功の目印
        self.wait_visible(self.LINK_MYPAGE)
        return self
