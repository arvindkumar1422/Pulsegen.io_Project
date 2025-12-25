import pytest
from src.crawler import Crawler

def test_is_valid_url():
    crawler = Crawler("https://example.com")
    assert crawler.is_valid_url("https://example.com/page1") == True
    assert crawler.is_valid_url("https://google.com") == False
    assert crawler.is_valid_url("https://example.com/sub/page") == True

def test_crawler_init():
    crawler = Crawler("https://example.com", max_depth=3)
    assert crawler.base_url == "https://example.com"
    assert crawler.max_depth == 3
    assert len(crawler.visited) == 0
