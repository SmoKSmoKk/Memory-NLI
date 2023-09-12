import unittest

import pytest
from playwright.sync_api import Page, expect


class TestRefinementClassSeries(unittest.TestCase):
    @pytest.fixture(autouse=True, scope='function')
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
        # Click text=# test series
        page.locator("text=# test series").click()
        # Click [aria-label="Run"]
        page.locator("[aria-label=\"Run\"]").click()
        self.page = page

    def test_str_series_return_df(self) -> None:

        # Click text=/.*ON COLUMN "elevation" STRIP "m".*/
        self.page.locator("text=/.*ON COLUMN \"elevation\" STRIP \"m\".*/").click()

        # Assert return df has selected column
        expect(self.page.locator('text=weather_data["elevation"] = '
                                 'weather_data["elevation"].str.strip(to_strip=\'m\')')).to_be_visible()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Click input[name="return_df"]
        self.page.locator("input[name=\"return_df\"]").click()

        # Fill input[name="return_df"]
        self.page.locator("input[name=\"return_df\"]").fill("elevation_data")

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        expect(self.page.locator('text=elevation_data = '
                                 'weather_data["elevation"].str.strip(to_strip=\'m\')')).to_be_visible()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()

        expect(self.page.locator('text=elevation_data = weather_data["elevation"].str.strip(to_strip=\'m\')')).\
            to_be_visible()

        # Click div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll >
        # .CodeMirror-sizer > div > .CodeMirror-lines
        self.page.locator("text=# test series").click()

        # Press z with modifiers
        self.page.locator("text=# test series").press("Control+z")

    def test_change_values(self) -> None:

        # Click text=/.*ON COLUMN "elevation" STRIP "m".*/
        self.page.locator("text=/.*ON COLUMN \"elevation\" STRIP \"m\".*/").click()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Select data
        self.page.locator("select[name=\"df_instance\"]").select_option("data")

        # Select col2
        self.page.locator("text=apply to columnscol1col2col3col4 >> select").select_option("col2")

        # Click text=Parameters: to_strip >> input[type="text"]
        self.page.locator("text=Parameters: to_strip >> input[type=\"text\"]").click()

        # Fill text=Parameters: to_strip >> input[type="text"]
        self.page.locator("text=Parameters: to_strip >> input[type=\"text\"]").fill("C")

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # Assert changes exist in code
        expect(self.page.locator("text=/.*data\\[\"col2\"\\] = "
                                 "data\\[\"col2\"\\]\\.str\\.strip\\(to_strip='C'\\).*/")).to_be_visible()

        expect(self.page.locator("text=Warning: Can only use .str accessor with string values!"))

        # Click text=Add code line
        self.page.locator("text=Add code anyway").click()

        # Click div:nth-child(5) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll >
        # .CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code > pre:nth-child(2)
        self.page.locator(
            "div:nth-child(5) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll > "
            ".CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code > pre:nth-child(2)").click()

        # Press z with modifiers
        self.page.locator("div:nth-child(5) > .input > .inner_cell > .input_area > .CodeMirror > div > textarea").press(
            "Control+z")

# if __name__ == '__main__':
#    unittest.main()
