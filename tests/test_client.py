import pytest
import sys
import os

# Dynamically add the SDK source folder to sys.path
sdk_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, sdk_src)

from imei_info import ImeiClient, AsyncImeiClient, BlacklistStatus, ImeiCheckResponse
from imei_info.exceptions import (
    ImeiAuthenticationError,
    ImeiInsufficientCreditsError,
    ImeiValidationError,
)

# Test Tokens
VALID_TOKEN = "test_bearer_token"


# =====================================================================
# 1. Synchronous Client Tests (ImeiClient)
# =====================================================================

def test_sync_client_success(server_url):
    """Test successful IMEI check (iPhone 12 Pro Max, CLEAN)."""
    with ImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        report = client.check_imei("353541326469521")
        
        assert report.imei == "353541326469521"
        assert report.brand == "Apple"
        assert report.model == "iPhone 12 Pro Max"
        assert report.blacklist_status == BlacklistStatus.CLEAN
        assert report.carrier_lock is False
        assert report.original_carrier == "T-Mobile Polska"
        assert report.purchase_country == "Poland"
        
        # Verify specifications nested model
        assert report.specifications is not None
        assert report.specifications.cpu == "Apple A14 Bionic"
        assert report.specifications.ram_gb == 6
        assert report.specifications.storage_gb == 128
        assert report.specifications.screen_size == "6.7 inches"


def test_sync_client_instant_success(server_url):
    """Test successful synchronous instant IMEI check using /api-sync/ endpoint."""
    with ImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        report = client.check_imei("353541326469521", sync=True)
        
        assert report.imei == "353541326469521"
        assert report.brand == "Apple"
        assert report.model == "iPhone 12 Pro Max"
        assert report.blacklist_status == BlacklistStatus.CLEAN


def test_sync_client_blacklist(server_url):
    """Test successful IMEI check returning BLACKLISTED status."""
    with ImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        report = client.check_imei("355030794352540")
        
        assert report.imei == "355030794352540"
        assert report.brand == "Google"
        assert report.model == "Pixel 8 Pro"
        assert report.blacklist_status == BlacklistStatus.BLACKLISTED
        assert report.carrier_lock is True
        assert report.original_carrier == "T-Mobile USA"
        assert report.purchase_country == "United States"


def test_sync_client_validation_error(server_url):
    """Test validation error for invalid Luhn checksum (422)."""
    with ImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        with pytest.raises(ImeiValidationError) as excinfo:
            client.check_imei("353541326469529")
            
        assert excinfo.value.status_code == 422
        assert excinfo.value.code == "invalid_luhn_checksum"
        assert excinfo.value.error_type == "Unprocessable Entity"
        assert "Luhn" in excinfo.value.message


def test_sync_client_insufficient_credits(server_url):
    """Test insufficient credits error (402)."""
    with ImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        with pytest.raises(ImeiInsufficientCreditsError) as excinfo:
            client.check_imei("358742099999999") # Any other IMEI triggers 402
            
        assert excinfo.value.status_code == 402
        assert excinfo.value.code == "insufficient_credits"
        assert excinfo.value.error_type == "Payment Required"
        assert "balance" in excinfo.value.message


def test_sync_client_unauthorized(server_url):
    """Test unauthorized response due to empty/invalid Authorization header (401)."""
    # Initialize with an empty token (server.py expects it to start with 'Bearer ')
    # Using an invalid empty/broken client
    with ImeiClient(token="", base_url=server_url) as client:
        # Override header to simulate missing bearer
        client.client.headers.pop("Authorization", None)
        
        with pytest.raises(ImeiAuthenticationError) as excinfo:
            client.check_imei("358742091234567")
            
        assert excinfo.value.status_code == 401
        assert excinfo.value.code == "missing_api_key"
        assert excinfo.value.error_type == "Unauthorized"


# =====================================================================
# 2. Asynchronous Client Tests (AsyncImeiClient)
# =====================================================================

@pytest.mark.asyncio
async def test_async_client_success(server_url):
    """Test successful async IMEI check."""
    async with AsyncImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        report = await client.check_imei("353541326469521")
        
        assert report.imei == "353541326469521"
        assert report.brand == "Apple"
        assert report.blacklist_status == BlacklistStatus.CLEAN
        assert report.specifications.cpu == "Apple A14 Bionic"


@pytest.mark.asyncio
async def test_async_client_validation_error(server_url):
    """Test async validation error."""
    async with AsyncImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        with pytest.raises(ImeiValidationError) as excinfo:
            await client.check_imei("353541326469529")
        assert excinfo.value.status_code == 422


@pytest.mark.asyncio
async def test_async_client_insufficient_credits(server_url):
    """Test async insufficient credits."""
    async with AsyncImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        with pytest.raises(ImeiInsufficientCreditsError) as excinfo:
            await client.check_imei("358742099999999")
        assert excinfo.value.status_code == 402


# =====================================================================
# 3. Model Serialization & Helper Tests
# =====================================================================

def test_model_serialization():
    """Test that dataclass models serialize and deserialize correctly."""
    raw_data = {
        "imei": "123456789012345",
        "brand": "Samsung",
        "model": "Galaxy S24",
        "tac": "12345678",
        "blacklist_status": "CLEAN",
        "carrier_lock": True,
        "original_carrier": "T-Mobile",
        "purchase_country": "US",
        "specifications": {
            "cpu": "Snapdragon",
            "ram_gb": 12,
            "storage_gb": 512,
            "screen_size": "6.2 inches"
        }
    }
    
    report = ImeiCheckResponse.from_dict(raw_data)
    assert report.brand == "Samsung"
    assert report.specifications.ram_gb == 12
    assert report.blacklist_status == BlacklistStatus.CLEAN
    
    # Check serialization
    serialized = report.to_dict()
    assert serialized["brand"] == "Samsung"
    assert serialized["specifications"]["ram_gb"] == 12
    assert serialized["blacklist_status"] == "CLEAN"


def test_sync_client_get_search_result(server_url):
    """Test retrieving history status and specs report synchronously."""
    with ImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        report = client.get_search_result(177586273)
        assert report.status == "Done"
        assert report.brand == "Apple"
        assert report.model == "iPhone 12 Pro Max"
        assert report.specifications.cpu == "Apple A14 Bionic"


@pytest.mark.asyncio
async def test_async_client_get_search_result(server_url):
    """Test retrieving history status and specs report asynchronously."""
    async with AsyncImeiClient(token=VALID_TOKEN, base_url=server_url) as client:
        report = await client.get_search_result(177586273)
        assert report.status == "Done"
        assert report.brand == "Apple"
        assert report.model == "iPhone 12 Pro Max"
        assert report.specifications.cpu == "Apple A14 Bionic"
