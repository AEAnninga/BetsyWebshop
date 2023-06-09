__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

from peewee import *
from models import db, PRODUCT_TAGS, User, Tag, Product, OrderItem, Bank, BillingInfo, UserTransaction, PayedOrderItem
import inquirer
from rich.prompt import Confirm
from validation_functions import is_float, is_int, is_string_not_too_big, is_own_product, product_exists
from help_variable import manually_add_product_error_text

def search(term):
    products = []
    db.connect(reuse_if_open=True)
    search_term = str(term).lower()
    product_query = Product.select()
    for product in product_query:
        name = str(product.product_name).lower()
        description = str(product.description).lower()
        if search_term in name or search_term in description:
            print(f"""
            Product id:                 {product.product_id}
            Product name:               {product.product_name}
            Product description:        {product.description}
            Product unit price :        {product.unit_price}
            Units in stock:             {product.units_in_stock}
            Made by user :              {product.made_by_user.name}
            User id :                   {product.made_by_user.user_id}   
            Product tag :               {product.product_tag.tag_name}     
            """)
            products.append(product)
    db.close()
    print(f"Products list:\n")
    return products


def list_user_products(user_id):
    db.connect(reuse_if_open=True)

    user_ids_query = User.select(User.user_id)
    user_ids = [int(user.user_id) for user in user_ids_query]
    max_user_id = max(user_ids)
    valid_user_id = is_int(user_id) and 0 < int(user_id) <= max_user_id and int(user_id) in user_ids
    if not valid_user_id:
        db.close()
        return print(f"Please enter valid user_id > integer from 1 - {max_user_id}! User could also have been removed from database! ")
    
    id = int(user_id)
    user_products = []
    user = User.select().where(User.user_id == id).get()

    for product in user.made_products:
        user_products.append(product)
        print(f"""
        Product id:                 {product.product_id}
        Product name:               {product.product_name}
        Product description:        {product.description}
        Product unit price :        {product.unit_price}
        Units in stock:             {product.units_in_stock}
        Made by user :              {product.made_by_user.name}
        User id :                   {product.made_by_user.user_id}   
        Product tag :               {product.product_tag.tag_id}: {product.product_tag.tag_name}
        """)
    db.close()
    print(f"Products list:\n")
    return user_products



def list_products_per_tag(tag_id):
    db.connect(reuse_if_open=True)

    tag_ids_query = Tag.select(Tag.tag_id)
    max_tag_id = max([int(tag.tag_id) for tag in tag_ids_query])
    valid_tag_id = is_int(tag_id) and 0 < int(tag_id) <= max_tag_id 
    if not valid_tag_id:
        db.close()
        return print(f"Please enter valid tag_id > integer from 1 - {max_tag_id}!")
    
    id = int(tag_id)
    tag = Tag.select().where(Tag.tag_id == id).get()
    product_query = Product.select().where(Product.product_tag == tag)
    tag_products = []
    for product in product_query:
        tag_products.append(product)

    for product in tag_products:
        print(f"""
        Tag id :                    {product.product_tag.tag_id}   
        Product tag :               {product.product_tag.tag_name}     
        Product id:                 {product.product_id}
        Product name:               {product.product_name}
        Product description:        {product.description}
        Product unit price :        {product.unit_price}
        Units in stock:             {product.units_in_stock}
        Made by user :              {product.made_by_user.name}
        User id :                   {product.made_by_user.user_id}
        """)

    db.close()
    print(f"Products list:\n")
    return tag_products


# when using a product, user can manually fill in a product as a dict, but must follow the schema (which is displayed)
# Best is to only give a user_id > user will be prompted to fill in product details
def add_product_to_catalog(user_id, product: dict = None):
    db.connect(reuse_if_open=True)

    user_ids_query = User.select(User.user_id)
    user_ids = [int(user.user_id) for user in user_ids_query]
    max_user_id = max(user_ids)
    valid_user_id = is_int(user_id) and 0 < int(user_id) <= max_user_id and int(user_id) in user_ids
    if not valid_user_id:
        db.close()
        return print(f"Please enter valid user_id > integer from 1 - {max_user_id}! User could also have been removed from database!")
    
    id = int(user_id)
    user = User.select().where(User.user_id == id).get()
    tags = Tag.select()

    if not product:
        print(f"""
        You are about to add a product made by following user:
        User id : {user.user_id}
        User name: {user.name}      
        """)
        continue_question = [inquirer.Confirm("continue", message="Do you want to continue?", default=False)]
        answer_continue = inquirer.prompt(continue_question)
        if answer_continue['continue']:
            product_questions = [
                inquirer.Text("product_name", message="Fill in the product_name (max 40 characters) ", validate=lambda _, product_name: is_string_not_too_big(product_name, 40)),
                inquirer.Text("description", message="Product description (max 250 characters) ", validate=lambda _, description: is_string_not_too_big(description, 250)),
                inquirer.Text("unit_price", message="Unit price (float) ", validate=lambda _, unit_price: is_float(unit_price)),
                inquirer.Text("units_in_stock", message="Units in stock (integer) ", validate=lambda _, units_in_stock: is_int(units_in_stock)),
                inquirer.List("product_tag", message="Choose a category/tag", choices=[{tag.tag_id: tag.tag_name} for tag in tags], carousel=True)
            ]

            product_answers = inquirer.prompt(product_questions)
            product_answers['product_tag'] = [key for key in product_answers['product_tag'].keys()][0]

            print(f"""
            You are going to add:
            product_name    :   {product_answers['product_name']}
            description     :   {product_answers['description']}    
            unit_price      :   {product_answers['unit_price']}    
            units_in_stock  :   {product_answers['units_in_stock']}    
            made_by_user    :   {id} (id)  {user.name} (name)   
            product_tag     :   {product_answers['product_tag']} ({[tag.tag_name for tag in tags if tag.tag_id == int(product_answers['product_tag'])][0]})       
            """)

            continue_adding_product_question = [inquirer.Confirm("continue", message="Continue adding product? ", default=False)]
            continue_adding_product_answer = inquirer.prompt(continue_adding_product_question)

            if not continue_adding_product_answer['continue']:
                db.close()
                return print('exiting...')
            
            Product.create(
                product_name=product_answers['product_name'],
                description=product_answers['description'],
                unit_price=float(product_answers['unit_price']),
                units_in_stock=int(product_answers['units_in_stock']),
                made_by_user=id,
                product_tag=int(product_answers['product_tag'])
            )
            db.close()
        else:
            db.close()
            return print("exiting...")
    else:
        try:
            product_to_add = product
            product_to_add['made_by_user'] = id

            tag_question = [inquirer.List("product_tag", message="Choose a category/tag:", choices=[{tag.tag_id: tag.tag_name} for tag in tags], carousel=True)]
            tag_answer = inquirer.prompt(tag_question)
            product_to_add['product_tag'] = [key for key in tag_answer['product_tag'].keys()][0]

            print(f"""
            You are going to add:
            product_name    :   {product_to_add['product_name']}
            description     :   {product_to_add['description']}    
            unit_price      :   {product_to_add['unit_price']}    
            units_in_stock  :   {product_to_add['units_in_stock']}    
            made_by_user    :   {id} (id)  {user.name} (name)   
            product_tag     :   {product_to_add['product_tag']} ({[tag.tag_name for tag in tags if tag.tag_id == int(product_to_add['product_tag'])][0]})       
            """)

            continue_adding_product_question = [inquirer.Confirm("continue", message="Continue adding product? ", default=False)]
            continue_adding_product_answer = inquirer.prompt(continue_adding_product_question)

            if not continue_adding_product_answer['continue']:
                db.close()
                return print('exiting...')
            
            valid_product_name = is_string_not_too_big(product_to_add['product_name'],40)
            valid_description = is_string_not_too_big(product_to_add['description'],250)
            valid_unit_price = is_float(product_to_add['unit_price'])
            valid_stock = is_int(product_to_add['units_in_stock'])
            if not valid_product_name or not valid_description or not valid_unit_price or not valid_stock:
                db.close()
                return print(manually_add_product_error_text)
            
            Product.create(
                product_name=product_to_add['product_name'],
                description=product_to_add['description'],
                unit_price=float(product_to_add['unit_price']),
                units_in_stock=int(product_to_add['units_in_stock']),
                made_by_user=id,
                product_tag=int(product_to_add['product_tag'])
            )
            db.close()
        except:
            print(manually_add_product_error_text)
            db.close()


def update_stock(product_id: int, new_quantity: int):
    db.connect(reuse_if_open=True)

    product_ids_query = Product.select(Product.product_id)
    product_ids = [int(product.product_id) for product in product_ids_query]
    max_id = max(product_ids)
    valid_id = is_int(product_id) and int(product_id) <= max_id and int(product_id) in product_ids
    valid_quantity = is_int(new_quantity)

    if not valid_id or not valid_quantity:
        db.close()
        return print("Please enter valid id or quantity!")

    update_stock_query = Product.update(units_in_stock=new_quantity).where(Product.product_id == product_id)
    update_stock_query.execute()
    db.close()


def purchase_product(product_id, buyer_id, quantity, is_product_payed: bool = True):
    db.connect(reuse_if_open=True)

    product_ids_query = Product.select(Product.product_id)
    user_ids_query = User.select(User.user_id)

    product_ids = [int(product.product_id) for product in product_ids_query]
    user_ids = [int(user.user_id) for user in user_ids_query]

    max_product_id = max(product_ids)
    max_buyer_id = max(user_ids)
    valid_product_id = is_int(product_id) and int(product_id) <= max_product_id and int(product_id) in product_ids
    valid_buyer_id = is_int(buyer_id) and 0 < int(buyer_id) <= max_buyer_id and int(buyer_id) in user_ids 
    if not valid_product_id or not valid_buyer_id:
        db.close()
        return print("Please enter valid id for product or buyer ( = user)! (Product or user may not exist anymore in the database!)")
  
    product = Product.select().where(Product.product_id == int(product_id)).get()
    seller = product.made_by_user
    max_quantity = int(product.units_in_stock)
    valid_quantity = is_int(quantity) and 0 < int(quantity) <= max_quantity 

    if not valid_quantity:
        db.close()
        return print(f"Quantity cannot be 0 of exceed {max_quantity}")
    
    user = User.select().where(User.user_id == int(buyer_id)).get()
    user_product_ids = [int(product.product_id) for product in user.made_products]
    if int(product_id) in user_product_ids:
        db.close()
        return print(f"Buyer cannot buy his own products!")

    new_quantity = int(product.units_in_stock) - int(quantity)
    price = int(quantity) * float(product.unit_price)
    order_numbers = OrderItem.select(OrderItem.order_number)
    new_order_number = max([int(item.order_number) for item in order_numbers]) + 1

    print(f"""
    Purchase info:
    
    Buyer id (user):    {user.user_id}
    Buyer name:         {user.name}
    Buyer iban:         {user.billing_info[0].bank_iban}
    product id:         {product.product_id}
    product name:       {product.product_name}
    In stock:           {product.units_in_stock}
    Purchase quantity:  {quantity}
    New stock:          {new_quantity}
    Total price:        {price}
    New order number:   {new_order_number}
    Seller id:          {seller.user_id}
    Seller name:        {seller.name}
    Seller iban:        {seller.billing_info[0].bank_iban}
    """)

    continue_buying_product_question = [inquirer.Confirm("continue", message="Continue buying product? ", default=False)]
    continue_buying_product_answer = inquirer.prompt(continue_buying_product_question)
    if not continue_buying_product_answer['continue']:
        db.close()
        return print('exiting...')

    OrderItem.create(
        order_number = int(new_order_number),
        buyer = int(user.user_id),
        product = int(product.product_id),
        buy_quantity = int(quantity),
        sell_price = float(price),
        is_payed = is_product_payed
    )

    if is_product_payed:
        transaction = UserTransaction.create(
            buyer = int(user.user_id),
            order_number = int(new_order_number),
            order_total_price = float(price) 
        )
        PayedOrderItem.create(
            order_number = int(new_order_number),
            seller_id = int(seller.user_id),
            buyer_id = int(user.user_id),
            product_id = int(product.product_id),
            product_name = product.product_name,
            product_price = float(product.unit_price),
            buy_quantity = int(quantity),
            sell_price = float(price),
            transaction = transaction.transaction_id
        )
    
    # update_stock for product > executed last because update_stock will close the database connection
    update_stock(int(product.product_id),int(new_quantity))
    # close database connection just to be sure
    db.close()


def remove_product(product_id):
    db.connect(reuse_if_open=True)

    product_ids_query = Product.select(Product.product_id)
    product_ids = [int(product.product_id) for product in product_ids_query]
    max_product_id = max(product_ids)
    valid_product_id = is_int(product_id) and 0 < int(product_id) <= max_product_id and int(product_id) in product_ids
    if not valid_product_id:
        db.close()
        return print("Please enter valid product_id! (Product may not exist anymore in the database!)")

    product = Product.get(Product.product_id == int(product_id))
    
    print(f"""
    You are going to delete following product from the database:
          
    product_id: {product.product_id}
    product_name: {product.product_name}
    description: {product.description}
    unit_price: {product.unit_price}
    units_in_stock: {product.units_in_stock}
    made_by_user: {product.made_by_user.name}
    product_tag: {product.product_tag.tag_id}: {product.product_tag.tag_name}
    """)

    continue_removing_product_question = [inquirer.Confirm("continue", message="Continue removing product? ", default=False)]
    continue_removing_product_answer = inquirer.prompt(continue_removing_product_question)
    if not continue_removing_product_answer['continue']:
        db.close()
        return print('exiting...')
    
    # deleting instance after confirmation 
    print(f"Removing product from database...")
    product.delete_instance(recursive=True)
 
    db.close()


# extra: purchase multiple products in 1 order(number):
def purchase_multiple_products(buyer_id: int, are_products_payed: bool = True):
    db.connect(reuse_if_open=True)

    user_ids_query = User.select(User.user_id)
    user_ids = [int(user.user_id) for user in user_ids_query]
    max_buyer_id = max(user_ids)
    valid_buyer_id = is_int(buyer_id) and 0 < int(buyer_id) <= max_buyer_id and int(buyer_id) in user_ids
    if not valid_buyer_id:
        db.close()
        return print("Please enter valid id for buyer ( = user)! (User may not exist anymore in the database!)")
    
    user = User.select().where(User.user_id == int(buyer_id)).get()
    products = []

    while True:
            product_ids_query = Product.select(Product.product_id)
            product_ids = [int(product.product_id) for product in product_ids_query]
            max_product_id = max(product_ids)
            user_product_ids = [int(product.product_id) for product in user.made_products]
            product_id_question = [
                inquirer.Text(
                    "product_id", 
                    message=f"Choose product_id from 1 - {max_product_id} ", 
                    validate=lambda _, product_id: is_int(product_id) and 0 < int(product_id) <= max_product_id and is_own_product(int(product_id) not in user_product_ids) and product_exists(int(product_id) in product_ids)
                )
            ]
            product_id_answer = inquirer.prompt(product_id_question)

            product_to_buy = Product.select().where(Product.product_id == int(product_id_answer['product_id'])).get()

            max_quantity = product_to_buy.units_in_stock
            buy_quantity_question = [
                inquirer.Text("buy_quantity", 
                    message=f"Choose quantity from 1 - {max_quantity} ", 
                    validate=lambda _, buy_quantity: is_int(buy_quantity) and 0 < int(buy_quantity) <= max_quantity
                )
            ]
            buy_quantity_answer = inquirer.prompt(buy_quantity_question)
            buy_quantity = int(buy_quantity_answer['buy_quantity'])
            new_quantity = int(product_to_buy.units_in_stock) - buy_quantity

            print(f"""
            You are going to buy:
            product_id      :   {product_to_buy.product_id}
            product_name    :   {product_to_buy.product_name}    
            unit_price      :   {product_to_buy.unit_price}     
            buy_quantity    :   {buy_quantity}    
            """)

            continue_adding_product_question = [inquirer.Confirm("continue", message="Continue adding product? ", default=False)]
            continue_adding_product_answer = inquirer.prompt(continue_adding_product_question)

            if not continue_adding_product_answer['continue']:
                db.close()
                return print('exiting...')
            
            product_tuple = (product_to_buy, buy_quantity, new_quantity)
            products.append(product_tuple)

            continue_next_product_question = [inquirer.Confirm("continue", message="Do you want to add another product? ", default=False)]
            continue_next_product_answer = inquirer.prompt(continue_next_product_question)

            if not continue_next_product_answer['continue']:
                break

    order_numbers = OrderItem.select(OrderItem.order_number)
    new_order_number = max([int(item.order_number) for item in order_numbers]) + 1
    sell_prices = []

    print(f"Buying {len(products)} products with ordernumber {new_order_number} ...")

    for item in products:
        sell_price = float(item[0].unit_price) * int(item[1])
        sell_prices.append(sell_price)
        OrderItem.create(
            order_number = int(new_order_number),
            buyer = int(buyer_id),
            product = item[0].product_id,
            buy_quantity = int(item[1]),
            sell_price = float(sell_price),
            is_payed = are_products_payed
        )
    # create single transaction with total price of all products from 1 order
    if are_products_payed:
        transaction = UserTransaction.create(
            buyer = int(buyer_id),
            order_number = int(new_order_number),
            order_total_price = float(sum(sell_prices))
        )
        for item in products:
            sell_price = float(item[0].unit_price) * int(item[1])
            PayedOrderItem.create(
                order_number = int(new_order_number),
                seller_id = int(item[0].made_by_user.user_id),
                buyer_id = int(user.user_id),
                product_id = int(item[0].product_id),
                product_name = item[0].product_name,
                product_price = float(item[0].unit_price),
                buy_quantity = int(item[1]),
                sell_price = float(sell_price),
                transaction = transaction.transaction_id
            )
    # update_stock for products > executed last because update_stock will close the database connection
    for item in products:
        update_stock(int(item[0].product_id),int(item[2]))
    # close database connection just to be sure
    db.close()
