from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

#Produktklasser
class Product(BaseModel):
    id: int
    productCode: str
    saldo: int

class ProductDeleteRequest(BaseModel):
    productCode: str 

#Hårdkodad data
inventory = {
    1: Product(id=1, productCode="Karhu", saldo=100),
    2: Product(id=2, productCode="Sandels", saldo=150),
    3: Product(id=3, productCode="Vatten", saldo=7000)
}

###                 ###
### VÅRA ENDPOINTS  ###
###       >.<       ###

#Returnerar alla items i vårt inventory
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