from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

#produkt klass så vi följer samma struktur, lägg till/ta bort om jag glömt nåt
class Product(BaseModel):
    id: int
    productCode: str
    saldo: int


#hårdkodad data
inventory = {
    1: Product(id=1, productCode="Karhu", saldo=100),
    2: Product(id=2, productCode="Sandels", saldo=150),
    3: Product(id=2, productCode="Pepsi max", saldo=7000)
}

###
### VÅRA ENDPOINTS
###

#Returnerar alla items i vårt inventory
@app.get("/inventory", response_model=list[Product])
def get_inventory():
    return list(inventory.values())
