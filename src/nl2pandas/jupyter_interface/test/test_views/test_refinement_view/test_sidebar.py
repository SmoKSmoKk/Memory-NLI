import pytest
import unittest

from playwright.sync_api import Page, expect


class TestSidebar(unittest.TestCase):
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

    def test_read_docs(self):

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Click text=Read docs
        self.page.locator("text=Read docs").click()

        # Assert that docs are shown
        # assert self.page.locator("text=Remove rows or column by specific names").is_visible()
        expect(self.page.locator("text=Remove rows or columns by specifying label names and")).to_be_visible()

        # Click text=Hide docs
        self.page.locator("text=Hide docs").click()

        # Assert that docs are hidden
        expect(self.page.locator("text=Remove rows or columns by specifying label names and")).not_to_be_visible()

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()

        # Click div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll >
        # .CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code > pre >> nth=0
        self.page.locator(
            "div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll > "
            ".CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code > pre").first.click()

        # Press z with modifiers
        self.page.locator("textarea").nth(3).press("Control+z")

    def test_apply_suggestion(self) -> None:

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Click button[name="multi_select year"]
        self.page.locator("button[name=\"multi_select year\"]").click()

        # Click button[name="year"]
        self.page.locator("button[name=\"year\"]").click()

        # Click button[name="year"]
        self.page.locator("button[name=\"year\"]").click()

        # Click button[name="temperature"]
        self.page.locator("button[name=\"temperature\"]").click()

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()

        # Click text=/.*# %pandas remove the column "year".*/
        self.page.locator("text=/.*# %nl2pandas remove the column \"year\".*/").click()

        # Press z with modifiers
        self.page.locator("textarea").nth(3).press("Control+z")

        # Click #run_int button >> nth=2
        self.page.locator("#run_int button").nth(2).click()
        # Click button:has-text("Restart")
        self.page.locator("button:has-text(\"Restart\")").click()
        # Click text=import pandas as pd
        self.page.locator("text=import pandas as pd").click()
        # Click [aria-label="Run"]
        self.page.locator("[aria-label=\"Run\"]").click()
        # Click [aria-label="Run"]
        self.page.locator("[aria-label=\"Run\"]").click()
        # Click [aria-label="Run"]

        self.page.locator("[aria-label=\"Run\"]").click()
        # Click [aria-label="Run"]
        self.page.locator("[aria-label=\"Run\"]").click()

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Click [placeholder="search"]
        self.page.locator("[placeholder=\"search\"]").click()

        # Assert previous action is present in suggestions
        expect(self.page.locator("button[name=\"suggestions_labels\"]")).to_contain_text("['year', 'temperature']")

        # Click text=labels = ['year', 'temperature']
        self.page.locator("text=labels = ['year', 'temperature']").click()

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()

        # Click span:has-text("'temperature'") >> nth=3
        self.page.locator("span:has-text(\"'temperature'\")").nth(3).click()

        # Press z with modifiers
        # page.locator("textarea").nth(3).press("Control+z")

        # Click div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll >
        # .CodeMirror-sizer > div > .CodeMirror-lines
        self.page.locator("div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll > "
                          ".CodeMirror-sizer > div > .CodeMirror-lines").click()

    def test_search_and_select_arguments(self) -> None:

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Click [placeholder="search"]
        self.page.locator("[placeholder=\"search\"]").click()

        # Fill [placeholder="search"]
        self.page.locator("[placeholder=\"search\"]").fill("inpl")

        # Click text=levelinplaceerrorslabelsaxisindexcolumnschange DataFramechange return instance >>
        # button[name="inplace"]
        self.page.locator("button[name=\"inplace\"]").click()

        # Assert options visibility
        expect(self.page.locator("text=Parameters:")).to_be_visible()
        expect(self.page.locator("text=Scope:")).not_to_be_visible()
        expect(self.page.locator("text=DataFrame Instance:")).not_to_be_visible()

        # Click [placeholder="search"]
        self.page.locator("[placeholder=\"search\"]").click()

        # Fill [placeholder="search"]
        self.page.locator("[placeholder=\"search\"]").fill("")

        # Click text=change return instance
        self.page.locator("text=change return instance").click()

        # Assert options visibility
        expect(self.page.locator("text=Parameters:")).not_to_be_visible()
        expect(self.page.locator("text=Scope:")).not_to_be_visible()
        expect(self.page.locator("text=DataFrame Instance:")).to_be_visible()

        # Click [placeholder="search"]
        self.page.locator("[placeholder=\"search\"]").click()

        # Fill [placeholder="search"]
        self.page.locator("[placeholder=\"search\"]").fill("labe")

        # Click text=levelinplaceerrorslabelsaxisindexcolumnschange DataFramechange return instance >>
        # button[name="labels"]
        self.page.locator("button[name=\"labels\"]").click()

        # Assert options visibility
        expect(self.page.locator("text=Parameters:")).not_to_be_visible()
        expect(self.page.locator("text=Scope:")).to_be_visible()
        expect(self.page.locator("text=DataFrame Instance:")).not_to_be_visible()

        # Click text=apply changes
        self.page.locator("text=apply changes").click()


# if __name__ == '__main__':
#    unittest.main()
