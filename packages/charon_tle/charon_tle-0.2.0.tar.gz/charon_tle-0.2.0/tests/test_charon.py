from unittest.mock import Mock, patch

import pytest

from charon.core import CharonTLE


@pytest.fixture
def sample_tle():
    """Sample TLE data for testing."""
    return """STARLINK-11072 [DTC]    
1 58705U 24002A   25190.83095688 -.00002028  00000+0 -11895-4 0  9998
2 58705  53.1598  31.2268 0000359  79.4304 280.6754 15.69704215 88248
STARLINK-11075 [DTC]    
1 58706U 24002B   25190.83585773 -.00000946  00000+0 -29585-5 0  9991
2 58706  53.1598  31.2268 0000359  79.4304 280.6754 15.69704215 88248
STARLINK-11076    
1 58707U 24002C   25190.83585773 -.00000946  00000+0 -29585-5 0  9991
2 58707  53.1598  31.2268 0000359  79.4304 280.6754 15.69704215 88248"""


@pytest.fixture
def charon():
    """CharonTLE instance for testing."""
    return CharonTLE()


def test_extract_cat_ids(charon, sample_tle):
    """Test extracting catalog IDs."""
    cat_ids = charon.extract_catid(sample_tle)
    assert cat_ids == ["58705", "58706", "58707"]


def test_extract_dtc_cat_ids(charon, sample_tle):
    """Test extracting DTC catalog IDs."""
    dtc_ids = charon.extract_catid(sample_tle, keyword="DTC")
    assert dtc_ids == ["58705", "58706"]


def test_filter_tle_by_cat_ids(charon, sample_tle):
    """Test filtering TLE by catalog IDs."""
    filtered = charon.filter_tle_by_catid(sample_tle, ["58705"])
    assert "58705" in filtered
    assert "58706" not in filtered
    assert "58707" not in filtered


def test_parse_tle_entries(charon, sample_tle):
    """Test parsing TLE entries."""
    entries = charon.parse_tle_entries(sample_tle)
    assert len(entries) == 3
    assert entries[0][1] == "58705"  # catalog ID
    assert "[DTC]" in entries[0][0]  # title


@patch("charon.core.requests.Session.get")
def test_download_tle(mock_get, charon):
    """Test downloading TLE data."""
    mock_response = Mock()
    mock_response.text = "test tle content"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = charon.download_tle("starlink")
    assert result == "test tle content"


def test_get_constellation_url(charon):
    """Test getting constellation URL."""
    url = charon.get_constellation_url("starlink")
    expected = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
    assert url == expected


def test_unsupported_group(charon):
    """Test handling unsupported group."""
    with pytest.raises(ValueError, match="Unsupported group"):
        charon.download_tle("unsupported")
