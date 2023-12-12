#
# Modscrape
# Module Scraper
# Tests
#


from importlib.resources import read_text

import test_resources
from modscrape import scrape_modules


def test_scrape_modules_core():
    assert len(scrape_modules(read_text(test_resources, "cs_core_modules.html"))) == 41


def test_scrape_modules_minor():
    assert (
        len(scrape_modules(read_text(test_resources, "art_hist_minor_modules.html")))
        == 30
    )
