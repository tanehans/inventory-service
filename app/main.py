from fastapi import FastAPI, HTTPException
from classes import  *
from inventory import inventory

app = FastAPI()

# =============================
#           INVENTORY
#         get/post/delete      
# =============================

@app.get("/inventory", response_model=list[Product])
def get_inventory():
    return list(inventory.values())

@app.post("/inventory", response_model=Product, status_code=201)
def create_product(product: ProductCreate):  # Använder nu ProductCreate
    new_id = max(inventory.keys(), default=0) + 1
    new_product = Product(id=new_id, productCode=product.productCode, stock=product.stock)
    inventory[new_id] = new_product
    return new_product

@app.delete("/inventory", status_code=200)
def delete_product(request: ProductDeleteRequest):
    product_id = next((key for key, product in inventory.items() if product.productCode == request.productCode), None)
    if product_id is None:
        raise HTTPException(status_code=404, detail="Produkten finns inte")
    deleted_product = inventory.pop(product_id)
    return {"message": f"Produkten {deleted_product.productCode} är borttagen"}

# =============================
#        INVENTORY SALDO
#        öka/sänka saldo
# =============================

@app.patch("/inventory/increase", response_model=Product)
def increase_stock(request: StockRequest):
    product_id = next((key for key, product in inventory.items() if product.productCode == request.productCode), None)
    if product_id is None:
        raise HTTPException(status_code=404, detail="Produkten finns inte")
    if request.quantity < 0:
        raise HTTPException(status_code=400, detail="Mängden måste vara större än 0")
    product = inventory[product_id]
    product.stock += request.quantity
    inventory[product_id] = product
    return product

@app.post("/inventory/decrease", response_model=list[Product])
def decrease_stock(request: DecreaseStockMultipleRequest):
    updated_products = []
    for item in request.items:
        product_id = next((key for key, product in inventory.items() if product.productCode == item.productCode), None)
        if product_id is None:
            raise HTTPException(status_code=404, detail=f"Produkten {item.productCode} finns inte")
        if item.quantity < 0:
            raise HTTPException(status_code=400, detail="Mängden måste vara större än 0")
        product = inventory[product_id]
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Inte tillräckligt med lagersaldo för {item.productCode}")
        product.stock -= item.quantity
        inventory[product_id] = product
        updated_products.append(product)
    
    send_shipping_confirmation(request.email, updated_products)
    return updated_products

# =============================
#           SHIPPING
#     Kalla på shipping api
# =============================

def send_shipping_confirmation(email: str, products: list[Product]):
    print(f"Skickar shippingbekräftelse till {email} för produkterna:")
    for product in products:
        print(f"{product.productCode}: {product.stock}st")