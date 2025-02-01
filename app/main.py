from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# =============================
#         VÅRA KLASSER
# =============================

class Product(BaseModel):
    id: int
    productCode: str
    stock: int

class ProductDeleteRequest(BaseModel):
    productCode: str 

class IncreaseStockRequest(BaseModel):
    productCode: str
    quantity: int

# =============================
#       HÅRDKODAD DATA
# =============================

inventory = {
    1: Product(id=1, productCode="0001", stock=100),
    2: Product(id=2, productCode="0002", stock=150),
    3: Product(id=3, productCode="0003", stock=7000)
}

# =============================
#           ENDPOINTS
#              >.<
# =============================

#hämtar alla produkter
@app.get("/inventory", response_model=list[Product])
def get_inventory():
    return list(inventory.values())

#Lägger till en ny produkt
@app.post("/inventory", response_model=Product, status_code=201)
def create_product(product: Product):
    if product.id in inventory:
        raise HTTPException(status_code=400, detail="Produkt med samma id finns redan :(")
    inventory[product.id] = product
    return product

#raderar en produkt baserat på produktkoden
@app.delete("/inventory", status_code=200)
def delete_product(request: ProductDeleteRequest):
    product_id = next((key for key, product in inventory.items() if product.productCode == request.productCode), None)

    if product_id is None:
        raise HTTPException(status_code=404, detail="Produkten finns inte")
    
    deleted_product = inventory.pop(product_id)
    return {"message": f"Produkten {deleted_product.productCode} är borttagen"}

#ökar lagersaldo på specifik produkt
@app.patch("/inventory/increase", response_model=Product)
def increase_stock(request: IncreaseStockRequest):
    product_id = next((key for key, product in inventory.items() if product.productCode == request.productCode), None)
    if product_id is None:
        raise HTTPException(status_code=404, detail="Produkten finns inte")
    product = inventory[product_id]
    product.stock += request.quantity
    inventory[product_id] = product
    return product