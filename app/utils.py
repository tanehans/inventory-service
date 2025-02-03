from fastapi import HTTPException
from typing import Dict, Optional
from classes import Product

# =============================
#  Om ni har funktioner som 
#  upprepas, lägg hit dem :)))
# =============================

def find_product_by_code(inventory: Dict[int, Product], product_code: str) -> Optional[int]:
    """Hitta produktens ID baserat på dess produktkod"""
    return next((key for key, product in inventory.items() if product.productCode == product_code), None)

def check_product_exists(inventory: Dict[int, Product], product_code: str) -> int:
    """Checka att produkten finns i inventoryt, annars kasta ett HTTP 404-fel""" # tack dennis för du visa mig att man kan göra docstrings
    product_id = find_product_by_code(inventory, product_code)
    if product_id is None:
        raise HTTPException(status_code=404, detail=f"Produkten {product_code} finns inte")
    return product_id

def ensure_valid_quantity(quantity: int):
    """Validera att kvantiteten är större än 0, annars kasta ett HTTP 400-fel"""
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Mängden måste vara större än 0")
