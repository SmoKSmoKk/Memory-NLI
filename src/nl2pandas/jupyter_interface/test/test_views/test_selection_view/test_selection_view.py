import pytest
import unittest

from playwright.sync_api import Page


class TestSelectionView(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:

        # Go to http://localhost:8880/login?next=%2Fnotebooks%2Ftest.ipynb
        page.goto("http://localhost:8880/login?next=%2Fnotebooks%2Ftest.ipynb")

        # Click text=Password or token: Log in >> input[name="password"]
        page.locator("text=Password or token: Log in >> input[name=\"password\"]").click()

        # Fill text=Password or token: Log in >> input[name="password"]
        page.locator("text=Password or token: Log in >> input[name=\"password\"]").fill(
            "7c7113d4-126a-4c28-b13c-54cc0fcbcb7e")

        # Click #login_submit
        page.locator("#login_submit").click()
        page.wait_for_url("http://localhost:8880/notebooks/test.ipynb")

        # Click #run_int button >> nth=2
        page.locator("#run_int button").nth(2).click()
        # Click button:has-text("Restart")
        page.locator("button:has-text(\"Restart\")").click()
        # Click text=import pandas as pd
        page.locator("text=import pandas as pd").click()
        # Click [aria-label="Run"]
        page.locator("[aria-label=\"Run\"]").click()
        # Click [aria-label="Run"]
        page.locator("[aria-label=\"Run\"]").click()
        # Click [aria-label="Run"]
        page.locator("[aria-label=\"Run\"]").click()

        # Click [aria-label="Run"]
        page.locator("[aria-label=\"Run\"]").click()
        self.page = page

    def test_selection(self) -> None:

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=change program
        self.page.locator("text=change program").click()

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()

        # Click span:has-text("'year'") >> nth=3
        self.page.locator("span:has-text(\"'year'\")").nth(3).click()

        # Press z with modifiers
        self.page.locator("textarea").nth(3).press("Control+z")
