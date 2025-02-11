from fastapi import FastAPI, HTTPException
from app.classes import  *
from app.inventory import inventory
from app.utils import *

app = FastAPI()

# =============================
#           INVENTORY
#         get/post/delete      
# =============================

@app.get("/inventory", response_model=list[Product])
def get_inventory():
    return list(inventory.values())

@app.post("/inventory", response_model=Product, status_code=201)
def create_product(product: ProductCreate):
    check_if_product_exists(inventory, product.productCode)  
    new_id = max(inventory.keys(), default=0) + 1  
    new_product = Product(id=new_id, productCode=product.productCode, stock=product.stock)
    inventory[new_id] = new_product
    return new_product

@app.post("/inventory/multiple", response_model=list[Product], status_code=201)
def create_multiple_products(products: list[ProductCreate]):
    created = []
    for product in products:
        check_if_product_exists(inventory, product.productCode) 
        new_id = max(inventory.keys(), default=0) + 1
        new_product = Product(id=new_id, productCode=product.productCode, stock=product.stock)
        inventory[new_id] = new_product
        created.append(new_product)
    return created

@app.delete("/inventory", status_code=200)
def delete_product(request: ProductDeleteRequest):
    product_id = check_product_exists(inventory, request.productCode) 
    deleted_product = inventory.pop(product_id)
    return {"message": f"Produkten {deleted_product.productCode} är borttagen"}


@app.delete("/inventory/multiple", response_model=list[Product], status_code=200)
def delete_multiple_products(request: ProductDeleteMultipleRequest):
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
    updated_products = []
    for item in request.items:
        product_id = check_product_exists(inventory, item.productCode)
        ensure_valid_quantity(item.quantity)

        product = inventory[product_id]
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Inte tillräckligt med lagersaldo för {item.productCode}")

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