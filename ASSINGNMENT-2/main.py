from fastapi import FastAPI,Query
from pydantic import BaseModel,Field

app = FastAPI()

# --- Pydantic model ---
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

# — Temporary data – acting as our database for now —
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price': 99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',        'price': 799, 'category': 'Electronics', 'in_stock': False },
    {'id': 4, 'name': 'Pen Set',        'price': 49,  'category': 'Stationery',  'in_stock': True },
]

orders = []
order_counter = 1

# == HELPER FUNCTIONS ===========================================
#== one helper ==== one job
def find_product(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None

def calculate_total(product: dict, quantity: int) -> int:
    return product['price'] * quantity

def filter_products_logic(category=None, min_price=None, 
                          max_price=None, in_stock=None):
    result = products
    if category is not None: result = [p for p in result if p['category']==category]
    if min_price is not None: result = [p for p in result if p['price']>=min_price]
    if max_price is not None: result = [p for p in result if p['price']<=max_price]
    if in_stock is not None: result = [p for p in result if p['in_stock']==in_stock]
    return result

# — Endpoint 0 - Home —
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# — Endpoint 1 - Return all products —
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

@app.get('/products/filter')
def filter_products(
    category: str = Query(None, description='Electronics or Stationery'),
    max_price: int = Query(None, description='Maximum price'),
    in_stock: bool = Query(None, description='True = in stock only')
):
    result = products        

    if category:
        result = [p for p in result if p['category'] == category]

    if max_price:
        result = [p for p in result if p['price'] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]

    return {'filtered_products': result, 'count': len(result)}

@app.get('/products/compare')
def compare_products(product_id_1:int=Query(...), product_id_2:int=Query(...)):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1: return {'error': f'Product {product_id_1} not found'}
    if not p2: return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {'product_1':p1, 'product_2':p2, 
    'better_value':cheaper['name'], 
    'price_diff':abs(p1['price']-p2['price'])}

# — Endpoint 2 - Return one product by its ID —
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    product = next((p for p in products if p['id']==order_data.product_id), None)
    if product is None:
        return {'error': 'Product not found'}
    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}
    total_price = product['price'] * order_data.quantity
    order = {'order_id': order_counter, 'customer_name': order_data.customer_name, 
    'product': product['name'], 'quantity': order_data.quantity, 
    'delivery_address': order_data.delivery_address, 
    'total_price': total_price, 'status': 'confirmed'}
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}

@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}
