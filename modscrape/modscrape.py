#
# Modmap
# Modscrape Module Scraper
#

from itertools import chain
from parser import parse
from pprint import pprint
from typing import Dict, cast

import requests
from bs4 import BeautifulSoup, Tag

from lexer import lex
from module import Module

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


def get_course_content(semester: str, course: str) -> str:
    """Get course content HTML for the given semester & course.

    See NTU course Content Site for options

    Args:
        semester: Academic semester to retrieve course content for.
        course: Course to retrieve course content for.
    Returns:
        Course content HTML retrieved from NTU course content site.
    """
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
        return response.content.decode()


def scrape_modules(content_html: str) -> list[Module]:
    """Scrape modules from the given Course Content HTML.

    Args:
        content_html: HTML from NTU course countent website to scrape modules from.
    Returns:
        List of scraped modules.
    Raises:
        ValueError: If the given HTML contains no <table> element to scrape course content from.
    """
    mod_listing = BeautifulSoup(content_html, "lxml")
    mod_tables = mod_listing.select("table")
    if len(mod_tables) == 1:
        # minor, bde & other non core modules: modules is encoded in a single table
        table = mod_tables[0]
        mod_rows: list[list[Tag]] = [[]]
        # skip the first <td> as it contains columns headers
        for tr in table.select("tr")[1:]:
            if tr.text.isspace():
                # <td> with empty newline delimits next module
                mod_rows.append([])
            mod_rows[-1].append(tr)
    elif len(mod_tables) > 1:
        # core modules: each module is encoded as table
        mod_rows = [[tr for tr in table.select("tr")] for table in mod_tables]
    else:
        raise ValueError("Missing <table> to scrape modules from.")

    lines = []
    for rows in mod_rows:
        individual = []
        for row in rows:
            cols = [td.text.strip() for td in cast(Tag, row).children]
            individual.append(cols)
        lines.append(individual)

    unnested = concat_nested(lines)
    nonempty = filter_empty(unnested)
    joined = [" ".join(line) for line in nonempty]
    tokens = lex(joined)
    modules = parse(tokens)
    return modules


# Takes a nested list and concatenates inner list
# e.g. [[[a], [b]]] -> [[a, b]]
def concat_nested(lines: list[list[list[str]]]) -> list[list[str]]:
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

    modules = scrape_modules(get_course_content("2023_1", "CSC;;1;F"))
    pprint(modules)
