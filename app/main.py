from fastapi import FastAPI, HTTPException
from app.classes import  *
from app.inventory import inventory
from app.utils import *

app = FastAPI()

# =============================
#           INVENTORY
#         get/post/delete      
# =============================

@app.get("/inventory")
def get_inventory():
    return [product.dict(exclude={"id"}) for product in inventory.values()]

@app.post("/inventory", response_model=list[Product], status_code=201)
def create_products(products: list[ProductCreate]):
    created = []
    for product in products:
        check_if_product_exists(inventory, product.productCode) 
        new_id = max(inventory.keys(), default=0) + 1
        new_product = Product(id=new_id, productCode=product.productCode, stock=product.stock)
        inventory[new_id] = new_product
        created.append(new_product)
    return created

@app.delete("/inventory", response_model=list[Product], status_code=200)
def delete_products(request: ProductDeleteMultipleRequest):
    deleted = []
    for code in request.productCodes:
        product_id = check_product_exists(inventory, code)
        deleted.append(inventory.pop(product_id))
    return deleted

# =============================
#        INVENTORY SALDO
#        öka/sänka saldo
# =============================

@app.post("/inventory/increase", response_model=Product)
def increase_stock(request: StockRequest):
    product_id = check_product_exists(inventory, request.productCode)
    ensure_valid_quantity(request.quantity)

    inventory[product_id] = inventory[product_id].model_copy(
        update={"stock": inventory[product_id].stock + request.quantity})
    return inventory[product_id]

@app.post("/inventory/decrease", response_model=list[Product])
def decrease_stock(request: DecreaseStockMultipleRequest):
    for item in request.items:
        product_id = check_product_exists(inventory, item.productCode)
        ensure_valid_quantity(item.quantity)
        
        product = inventory[product_id]
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Inte tillräckligt med lagersaldo för {item.productCode}. Tillgängligt: {product.stock}, Efterfrågat: {item.quantity}"
            )

    updated_products = []
    for item in request.items:
        product_id = check_product_exists(inventory, item.productCode)
        product = inventory[product_id]
        inventory[product_id] = product.model_copy(update={"stock": product.stock - item.quantity})
        updated_products.append(inventory[product_id])

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