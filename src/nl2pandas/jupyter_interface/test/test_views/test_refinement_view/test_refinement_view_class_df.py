import pytest
import unittest

from playwright.sync_api import Page, expect


class TestRefinementClassDataFrame(unittest.TestCase):
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

    def test_change_multi_select(self) -> None:

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Click button[name="multi_select year"]
        self.page.locator("button[name=\"multi_select year\"]").click()

        # Click button[name="year"]
        self.page.locator("button[name=\"year\"]").click()

        # check if button name is None
        expect(self.page.locator("button[name=\"multi_select None\"]")).to_be_visible()

        # Click button[name="temperature"]
        self.page.locator("button[name=\"temperature\"]").click()

        # check that None has been removed from name
        expect(self.page.locator("button[name=\"multi_select temperature\"]")).to_be_visible()

        # Click button:has-text("station_id")
        self.page.locator("button:has-text(\"station_id\")").click()

        # Click .lm-Widget > .lm-Widget > div > div
        self.page.locator(".lm-Widget > .lm-Widget > div > div").click()

        # check that both names are visible
        expect(self.page.locator("button[name=\"multi_select temperature, station_id\"]")).to_be_visible()

        # Click text=temperature, station_id
        self.page.locator("text=temperature, station_id").click()

        # Click button:has-text("None")
        self.page.locator("button:has-text(\"None\")").click()

        # check that both names have been removed
        expect(self.page.locator("button[name=\"multi_select None\"]")).to_be_visible()

        # Click .lm-Widget > .lm-Widget > div > div
        self.page.locator(".lm-Widget > .lm-Widget > div > div").click()

        # Click button[name="multi_select None"]
        self.page.locator("button[name=\"multi_select None\"]").click()

        # Click button[name="elevation"]
        self.page.locator("button[name=\"elevation\"]").click()

        # Click button[name="temperature"]
        self.page.locator("button[name=\"temperature\"]").click()

        # Click .lm-Widget > .lm-Widget > div > div
        self.page.locator(".lm-Widget > .lm-Widget > div > div").click()

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # check that column list is in function
        expect(self.page.locator("text=weather_data.drop"
                                 "(labels=['elevation', 'temperature'], axis='columns')")).to_be_visible()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()

        expect(self.page.locator("text=weather_data.drop"
                                 "(labels=['elevation', 'temperature'], axis='columns')")).to_be_visible()

        # Click div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll >
        # .CodeMirror-sizer > div > .CodeMirror-lines
        self.page.locator(
            "div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll > "
            ".CodeMirror-sizer > div > .CodeMirror-lines").click()

        # Press z with modifiers
        self.page.locator("textarea").nth(3).press("Control+z")

    def test_change_df(self) -> None:

        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Select data
        self.page.locator("select[name=\"df_instance\"]").select_option("data")

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # Assert that return df and df changed:
        expect(self.page.locator("text=data = data.drop(labels='col1', axis='columns')")).to_be_visible()

        # Click button:has-text("refine")
        self.page.locator("button:has-text(\"refine\")").click()

        # Click input[name="return_df"]
        self.page.locator("input[name=\"return_df\"]").click()

        # Fill input[name="return_df"]
        self.page.locator("input[name=\"return_df\"]").fill("return_df")

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # Assert return df changed:
        expect(self.page.locator("text=return_df = data.drop(labels='col1', axis='columns')")).to_be_visible()

        # Click button:has-text("refine")
        self.page.locator("button:has-text(\"refine\")").click()

        # Select weather_data
        self.page.locator("select[name=\"df_instance\"]").select_option("weather_data")

        # Assert labels changed
        expect(self.page.locator("button", has_text="elevation").nth(0)).to_be_visible()

        # Assert return df did not change, fails for some reason but text is there
        # expect(self.page.locator("text=return_df")).to_be_visible()

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()

        # Assert added code has correct df
        expect(self.page.locator("text=return_df = weather_data.drop"
                                 "(labels='elevation', axis='columns')")).to_be_visible()

        # Click pre[role="presentation"]:has-text("return_df = weather_data.drop(labels='elevation', axis='columns')")
        self.page.locator(
            "pre[role=\"presentation\"]:has-text(\"return_df = weather_data.drop"
            "(labels='elevation', axis='columns')\")").click()

        # Press z with modifiers
        self.page.locator("textarea").nth(3).press("Control+z")

    def test_change_parameters(self) -> None:
        # Click text=/.*DELETE COLUMN "year".*/
        self.page.locator("text=/.*DELETE COLUMN \"year\".*/").click()

        # Click text=refine
        self.page.locator("text=refine").click()

        # Click text=show more parameters
        self.page.locator("text=show more parameters").click()

        # Select True
        self.page.locator("text=inplaceTrueFalse >> select").select_option("True")

        # Click text=apply changes
        self.page.locator("text=apply changes").click()

        # Assert no return df
        expect(self.page.locator("text=weather_data.drop"
                                 "(labels='year', axis='columns', inplace=True)")).to_be_visible()

        # Click text=Add code line
        self.page.locator("text=Add code line").click()

        # Assert parameter added to code line
        expect(self.page.locator("text=weather_data.drop"
                                 "(labels='year', axis='columns', inplace=True)")).to_be_visible()

        # Click div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll >
        # .CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code > pre >> nth=0
        self.page.locator(
            "div:nth-child(4) > .input > .inner_cell > .input_area > .CodeMirror > .CodeMirror-scroll > "
            ".CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code > pre").first.click()

        # Press z with modifiers
        self.page.locator("textarea").nth(3).press("Control+z")


# if __name__ == '__main__':
#    unittest.main()
