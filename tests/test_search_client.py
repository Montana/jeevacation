import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from epstein_enhanced.core.search_client import EpsteinSearchClient, search_synchronous


@pytest.fixture
def mock_response():
    return {
        "results": [
            {
                "file_path": "/dataset1/doc001.pdf",
                "excerpt": "John Doe testified...",
                "page": 5
            },
            {
                "file_path": "/dataset2/doc002.pdf",
                "excerpt": "...John Doe mentioned...",
                "page": 12
            }
        ]
    }


class TestEpsteinSearchClient:
    
    @pytest.mark.asyncio
    async def test_search_name_success(self, mock_response):
        async with EpsteinSearchClient() as client:
            with patch.object(client.session, 'get') as mock_get:
                mock_resp = AsyncMock()
                mock_resp.json = AsyncMock(return_value=mock_response)
                mock_resp.raise_for_status = Mock()
                mock_get.return_value.__aenter__.return_value = mock_resp
                
                results = await client.search_name("John Doe")
                
                assert len(results) == 2
                assert results[0]['file_path'] == "/dataset1/doc001.pdf"
    
    @pytest.mark.asyncio
    async def test_search_name_no_results(self):
        async with EpsteinSearchClient() as client:
            with patch.object(client.session, 'get') as mock_get:
                mock_resp = AsyncMock()
                mock_resp.json = AsyncMock(return_value={"results": []})
                mock_resp.raise_for_status = Mock()
                mock_get.return_value.__aenter__.return_value = mock_resp
                
                results = await client.search_name("Unknown Person")
                
                assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_batch_search(self, mock_response):
        async with EpsteinSearchClient() as client:
            with patch.object(client, 'search_name', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = mock_response['results']
                
                names = ["John Doe", "Jane Smith"]
                results = await client.batch_search(names, batch_size=2)
                
                assert len(results) == 2
                assert "John Doe" in results
                assert "Jane Smith" in results
    
    def test_get_pdf_url(self):
        client = EpsteinSearchClient()
        
        url = client.get_pdf_url("/dataset1/doc001.pdf")
        assert url == "https://www.justice.gov/epstein/files/dataset1/doc001.pdf"
        
        url = client.get_pdf_url("dataset1/doc001.pdf")
        assert url == "https://www.justice.gov/epstein/files/dataset1/doc001.pdf"


def test_search_synchronous(mock_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()
        
        results = search_synchronous("John Doe")
        
        assert len(results) == 2
        assert results[0]['file_path'] == "/dataset1/doc001.pdf"


def test_search_synchronous_error():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Network error")
        
        results = search_synchronous("John Doe")
        
        assert len(results) == 0
