#
# Modmap
# Modscrape Module Scraper
#

from typing import Dict, cast
import requests
from bs4 import BeautifulSoup, Tag
from itertools import chain
from lexer import lex
from parser import parse
from pprint import pprint

COURSE_CONTENT_URL = "https://wis.ntu.edu.sg/webexe/owa/aus_subj_cont"


def extract_options(page: BeautifulSoup, name: str) -> Dict[str, str]:
    """Extract options from the select element with the given name attribute.

    Args:
        page: Page to extract select options from.
        name: 'name' attribute assigned to the select to extract options from.
    Returns:
        Mapping of  option 'value' attribute as key to option text as value.
    """
    select = cast(Tag, page.find("select", attrs={"name": name}))
    return {o.attrs["value"]: o.string.rstrip() for o in select.find_all("option")}


def scrape_modules(semester: str, course: str):
    # scrape modules
    year, term = semester.split("_")
    with requests.post(
        f"{COURSE_CONTENT_URL}.main_display1",
        {
            # for some reason, the client side post request sends 'acadsem'
            # we emulate that behavior here.
            "acadsem": [
                semester,
                semester,
            ],
            "r_course_yr": course,
            "r_subj_code": "Enter+Keywords+or+Course+Code",
            "boption": "CLoad",
            "acad": year,
            "semester": term,
        },
    ) as response:
        mod_listing = BeautifulSoup(response.content.decode(), "lxml")
        # each module is encoded as table
        mod_tables = mod_listing.find_all("table")
        # print(mod_tables)
        # for every table:
        lines = []
        for table in mod_tables:
            individual = []
            rows = table.find_all("tr")
            for row in rows:
                cols = [ele.text.strip() for ele in row.find_all("td")]
                individual.append(cols)
            lines.append(individual)
        return lines


# Takes a nested list and concatenates inner list
# e.g. [[a], [b]] -> [[a, b]]
def concat_nested(lines: list[list[str]]) -> list[list[str]]:
    return [list(chain(*line)) for line in lines]


# Takes a nested list and filters out all empty strings
# e.g. [[a, b, ''], [c, '']] -> [[a, b], [c]]
def filter_empty(lines: list[list[str]]) -> list[list[str]]:
    return [list(filter(None, line)) for line in lines]


if __name__ == "__main__":
    # scrape main page
    with requests.get(f"{COURSE_CONTENT_URL}.main") as response:
        # lxml parser is used to handle malformed html (eg. unclosed tags)
        mainpage = BeautifulSoup(response.content.decode(), "lxml")
    # scrape semesters from main page
    semesters = extract_options(mainpage, "acadsem")
    # scrape courses from main page
    courses = extract_options(mainpage, "r_course_yr")

    lines = scrape_modules("2023_1", "CSC;;1;F")
    lines = concat_nested(lines)
    lines = filter_empty(lines)
    lines = [" ".join(line) for line in lines]

    tokens = lex(lines)
    modules = parse(tokens)

    pprint(modules)
