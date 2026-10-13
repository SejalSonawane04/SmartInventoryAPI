# Import json module to read and verify JSON data
import json

# Import app.py and give it the name inventory_app
import app as inventory_app


# Helper function to create a temporary database for testing
def prepare_database(monkeypatch, tmp_path):

    # Create a temporary inventory.json file
    test_file = tmp_path / "inventory.json"

    # Initialize the file with an empty list []
    test_file.write_text("[]", encoding="utf-8")

    # Replace the real DB_FILE in app.py with this temporary file
    # This prevents tests from modifying actual data
    monkeypatch.setattr(
        inventory_app, "DB_FILE", test_file
    )

    # Create and return a test client for sending requests
    return inventory_app.app.test_client()


# Test the home endpoint (/)
def test_home():

    # Create test client
    client = inventory_app.app.test_client()

    # Send GET request to home page
    response = client.get("/")

    # Check if response status code is 200 (Success)
    assert response.status_code == 200

    # Check whether expected message is returned
    assert "Smart Inventory API" in response.get_json()["message"]


# Test the inventory endpoint (/inventory)
def test_get_inventory(monkeypatch, tmp_path):

    # Create temporary database and test client
    client = prepare_database(monkeypatch, tmp_path)

    # Send GET request to inventory endpoint
    response = client.get("/inventory")

    # Verify API returns success
    assert response.status_code == 200

    # Verify inventory is empty initially
    assert response.get_json() == []


# Test adding a new product
def test_add_item(monkeypatch, tmp_path):

    # Create temporary database and test client
    client = prepare_database(monkeypatch, tmp_path)

    # Sample product data
    item = {
        "ProductID": "TEST001",
        "ProductName": "Wire Coil",
        "Stock": 20,
        "Price": 300.0
    }

    # Send POST request to add product
    response = client.post("/add", json=item)

    # Check if item was created successfully
    assert response.status_code == 201

    # Check success flag in response
    assert response.get_json()["success"] is True

    # Read data from temporary inventory file
    saved_data = json.loads(
        (tmp_path / "inventory.json").read_text(encoding="utf-8")
    )

    # Verify only one item was saved
    assert len(saved_data) == 1

    # Verify correct ProductID was saved
    assert saved_data[0]["ProductID"] == "TEST001"


# Test duplicate product validation
def test_duplicate_product(monkeypatch, tmp_path):

    # Create temporary database and test client
    client = prepare_database(monkeypatch, tmp_path)

    # Sample product
    item = {
        "ProductID": "TEST001",
        "ProductName": "Wire Coil",
        "Stock": 20,
        "Price": 300.0
    }

    # Add product first time
    first_response = client.post("/add", json=item)

    # Add same product second time
    second_response = client.post("/add", json=item)

    # First request should succeed
    assert first_response.status_code == 201

    # Second request should fail because ProductID already exists
    assert second_response.status_code == 409

# ✅ Home API

# ✅ Get Inventory API

# ✅ Add Item API

# ✅ Data Actually Saved

# ✅ Duplicate Product Validation

# ✅ Temporary Database Isolation