"""Tests for the MarvelClient."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from marvelpy.client import MarvelClient


class TestMarvelClient:
    """Test cases for MarvelClient."""
    
    @pytest.fixture
    def client(self):
        """Create a MarvelClient instance for testing."""
        return MarvelClient(
            public_key="test_public_key",
            private_key="test_private_key",
            timeout=5.0,
            max_retries=1,
        )
    
    def test_client_initialization(self, client):
        """Test MarvelClient initialization."""
        assert client.public_key == "test_public_key"
        assert client.private_key == "test_private_key"
        assert client.timeout == 5.0
        assert client.max_retries == 1
        assert client.base_url == MarvelClient.BASE_URL
    
    def test_client_initialization_with_custom_base_url(self):
        """Test MarvelClient initialization with custom base URL."""
        custom_url = "https://custom.marvel.com/v1/public/"
        client = MarvelClient(
            public_key="test_public_key",
            private_key="test_private_key",
            base_url=custom_url,
        )
        assert client.base_url == custom_url
    
    def test_get_auth_params(self, client):
        """Test authentication parameter generation."""
        auth_params = client._get_auth_params()
        
        assert "apikey" in auth_params
        assert "ts" in auth_params
        assert "hash" in auth_params
        assert auth_params["apikey"] == "test_public_key"
        assert isinstance(auth_params["ts"], str)
        assert isinstance(auth_params["hash"], str)
    
    def test_build_url(self, client):
        """Test URL building."""
        # Test with endpoint starting with /
        url = client._build_url("/characters")
        assert url == f"{MarvelClient.BASE_URL}characters"
        
        # Test with endpoint not starting with /
        url = client._build_url("characters")
        assert url == f"{MarvelClient.BASE_URL}characters"
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, client):
        """Test successful request making."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"results": []}}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(client._client, 'request', return_value=mock_response):
            result = await client._make_request("GET", "characters")
            
            assert result == {"data": {"results": []}}
            client._client.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_with_params(self, client):
        """Test request making with parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"results": []}}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(client._client, 'request', return_value=mock_response):
            params = {"name": "spider-man"}
            result = await client._make_request("GET", "characters", params)
            
            assert result == {"data": {"results": []}}
            call_args = client._client.request.call_args
            assert "name" in call_args[1]["params"]
            assert "apikey" in call_args[1]["params"]  # Auth params should be added
    
    @pytest.mark.asyncio
    async def test_get_method(self, client):
        """Test GET method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"results": []}}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(client._client, 'request', return_value=mock_response):
            result = await client.get("characters")
            
            assert result == {"data": {"results": []}}
            call_args = client._client.request.call_args
            assert call_args[1]["method"] == "GET"
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"results": []}}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(client._client, 'request', return_value=mock_response):
            result = await client.health_check()
            
            assert result == {"data": {"results": []}}
            call_args = client._client.request.call_args
            assert call_args[1]["method"] == "GET"
            assert "characters" in call_args[1]["url"]
            assert call_args[1]["params"]["limit"] == 1
    
    @pytest.mark.asyncio
    async def test_get_characters(self, client):
        """Test get_characters method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"results": []}}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(client._client, 'request', return_value=mock_response):
            result = await client.get_characters()
            
            assert result == {"data": {"results": []}}
            call_args = client._client.request.call_args
            assert call_args[1]["method"] == "GET"
            assert "characters" in call_args[1]["url"]
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        with patch('marvelpy.client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            async with MarvelClient("pub", "priv") as client:
                assert client is not None
            
            mock_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close(self, client):
        """Test close method."""
        with patch.object(client._client, 'aclose') as mock_close:
            await client.close()
            mock_close.assert_called_once()