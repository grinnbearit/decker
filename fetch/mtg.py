import requests as r
from scrapy.selector import Selector


def fetch(card):
    """
    returns the most likely image url for the passed card
    """
    base = "https://magiccards.info"
    response = r.get(base + "/query", params={"q": "forest"})
    src = Selector(text=response.text).xpath("//td/img[@style='border: 1px solid black;']/@src").extract()[0]
    url = base + src
    return url
