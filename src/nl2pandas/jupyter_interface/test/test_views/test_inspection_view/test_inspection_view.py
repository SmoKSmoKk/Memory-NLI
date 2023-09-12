import pytest
import unittest

from playwright.sync_api import Page, expect


class TestInspectionView(unittest.TestCase):
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
        self.page = page

    def test_checkbox(self) -> None:
        # Click #run_int button >> nth=3
        self.page.locator("#run_int button").nth(3).click()

        # Click text=Restart and Run All Cells
        self.page.locator("text=Restart and Run All Cells").click()

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Check input[name="checkbox"] >> nth=1
        self.page.locator("input[name=\"checkbox\"]").nth(1).check()
        expect(self.page.locator("input[name=\"checkbox\"]").nth(1)).to_be_checked()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()
        expect(self.page.locator("text=# DELETE COLUMN \"year\""))

        self.page.locator(
            "div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll > "
            ".CodeMirror-sizer > div > .CodeMirror-lines").click()

        # Press z with modifiers
        self.page.locator("textarea").nth(3).press("Control+z")
