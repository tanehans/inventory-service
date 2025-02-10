import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.inventory import inventory
from app.classes import Product


#denna resettar inventory för varje test, ÄNDRA INTE
@pytest.fixture(autouse=True)
def reset_inventory():
    inventory.clear()
    inventory.update({
        1: Product(id=1, productCode="0001", stock=100),
        2: Product(id=2, productCode="0002", stock=150),
        3: Product(id=3, productCode="0003", stock=7000)
    })

client = TestClient(app)

#Testar endpoints
def test_get_inventory():
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert any(prod["productCode"] == "0001" for prod in data)
    assert any(prod["productCode"] == "0002" for prod in data)
    assert any(prod["productCode"] == "0003" for prod in data)

def test_create_product():
    new_product = {"productCode": "0004", "stock": 200}
    response = client.post("/inventory", json=new_product)
    assert response.status_code == 201
    data = response.json()
    assert data["productCode"] == "0004"
    assert data["stock"] == 200
    assert "id" in data

def test_delete_existing_product():
    payload = {"productCode": "0002"}
    response = client.request("DELETE", "/inventory", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "0002" in data["message"]

    response = client.get("/inventory")
    data = response.json()
    assert not any(prod["productCode"] == "0002" for prod in data)