import random

def create_order_data():
    orders = []
    # create 50 orders
    for i in range(1,51,1):
        user_num = random.choice(range(1,101,1))
        order_num = int(i)
        # number of products per order
        num_of_products = random.choice(range(2,7,1))
        products = []
        for j in range(1, num_of_products, 1):
            while True:
                product = {"product_id": random.choice(range(1,301,1)), "buy_quantity": random.choice(range(1,11,1))}
                if product not in products:
                    products.append(product)
                    break
        order = {
            'order_number': order_num,
            'buyer': int(user_num),
            'products': products, # products is a list of products belonging to same order
            'is_payed': random.choice([False,True])
        }
        orders.append(order)
    return orders
