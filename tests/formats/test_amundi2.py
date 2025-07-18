import pytest
from ..conftest import single_page_tests
from . import (
    generic_test_pdf_filter,
    generic_test_text_extract,
    generic_test_deserialize,
    generic_test_pipeline,
)


fmt = "AMUNDI2"
pages = single_page_tests[fmt]


@pytest.mark.parametrize("page", pages)
def test_pdf_filter(page):
    generic_test_pdf_filter(fmt, page)


@pytest.mark.parametrize("page", pages)
def test_text_extract(page):
    generic_test_text_extract(fmt, page)


@pytest.mark.parametrize("page", pages)
def test_deserialize(page):
    generic_test_deserialize(fmt, page)


@pytest.mark.integration_tests
def test_pipeline():
    generic_test_pipeline(fmt)
