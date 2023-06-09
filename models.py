from peewee import *
from betsy_products import products
from betsy_users import users
from betsy_order_util import create_order_data
import random

db = SqliteDatabase('betsy.db', pragmas={'foreign_keys': 1}, autoconnect=False)

class BaseModel(Model):
    class Meta:
        database = db


PRODUCT_TAGS = [
    (1,"women's clothing"),
    (2,"men's clothing"),
    (3,"electronics"),
    (4,"jewelry")
]

BANKS = [
    {'bank_id': 1,'bank_name': 'Rabobank', 'bic_code': 'RABONL2U', 'iban_example': 'NL00RABO0123456'},
    {'bank_id': 2,'bank_name': 'ING', 'bic_code': 'INGBNL2A', 'iban_example': 'NL00INGB0123456'},
    {'bank_id': 3,'bank_name': 'Abn Amro', 'bic_code': 'ABNANL2A', 'iban_example': 'NL00ABNA0123456'},
    {'bank_id': 4,'bank_name': 'SNS', 'bic_code': 'SNSBNL2A', 'iban_example': 'NL00SNSB0123456'},
    {'bank_id': 5,'bank_name': 'Knab', 'bic_code': 'KNABNL2H', 'iban_example': 'NL00KNAB0123456'}
]

class CustomFloatField(FloatField):
    field_type = 'FLOAT'

    def adapt(self, value):
        try:
            return round(float(value),2)
        except ValueError:
            return value
        

class User(BaseModel):
    user_id = AutoField(primary_key=True)
    name = CharField()
    address = CharField()
    country = CharField()


class Tag(BaseModel):
    tag_id = AutoField(primary_key=True)
    tag_name = CharField(unique=True)


class Product(BaseModel):
    product_id = AutoField(primary_key=True)
    product_name = CharField()
    description = TextField()
    unit_price = CustomFloatField()
    units_in_stock = IntegerField()
    made_by_user = ForeignKeyField(User, backref="made_products")
    product_tag = ForeignKeyField(Tag, backref="products")

# when user/buyer orproduct is removed, the related orderitems will be removed too, but when payed, orderitems will be stored as PayedOrderItems
# PayedOrderItems will can be removed directly or when related transaction is deleted. A UserTransaction can only be deleted directly
class OrderItem(BaseModel):
    order_id = AutoField(primary_key=True)
    order_number = IntegerField(unique=False)
    buyer = ForeignKeyField(User, backref="orders")
    product = ForeignKeyField(Product, backref="exists_in_orders")
    buy_quantity = IntegerField()
    sell_price = CustomFloatField()
    is_payed = BooleanField(default=False)


class Bank(BaseModel):
    bank_id = AutoField(primary_key=True)
    bank_name = CharField()
    bic_code = CharField()


class BillingInfo(BaseModel):
    billing_id = AutoField(primary_key=True)
    from_user = ForeignKeyField(User, backref="billing_info")
    bank = ForeignKeyField(Bank, backref="billing_info")
    bank_iban = CharField()

# will not be removed if related buyer/user is removed
class UserTransaction(BaseModel):
    transaction_id = AutoField(primary_key=True)
    buyer = ForeignKeyField(User, backref="has_transactions", null=True)
    order_number = IntegerField()
    order_total_price = CustomFloatField()

# will be removed along with related UserTransaction or can be removed directly
class PayedOrderItem(BaseModel):
    item_id = AutoField(primary_key=True)
    order_number = IntegerField(unique=False)
    seller_id = IntegerField()
    buyer_id = IntegerField()
    product_id = IntegerField()
    product_name = CharField()
    product_price = CustomFloatField()
    buy_quantity = IntegerField()
    sell_price = CustomFloatField()
    transaction = ForeignKeyField(UserTransaction, backref="payed_items")


def create_tables():
    db.create_tables([User,Tag,Product,OrderItem,Bank,BillingInfo,UserTransaction,PayedOrderItem])


def create_users():
    try:
        for user in users:
            User.create(
                name=user['name'],
                address=user['address'],
                country=user['country']
            )
    except IntegrityError as ie:
        print(f"Integrity error:\n\n{ie}")


def create_tags():
    try:
        for tag_info in PRODUCT_TAGS:
            Tag.create(tag_id=tag_info[0],tag_name=tag_info[1])
    except IntegrityError as ie:
        print(f"Integrity error:\n\n{ie}")


def create_products():
    try:
        for product in products:
            Product.create(
                product_name=product['product_name'],
                description=product['description'],
                unit_price=product['unit_price'],
                units_in_stock=product['units_in_stock'],
                made_by_user=product['made_by_user'],
                product_tag=product['product_tag']
            )
    except IntegrityError as ie:
        print(f"Integrity error:\n\n{ie}")


def create_banks():
    try:
        for bank in BANKS:
            Bank.create(bank_name=bank['bank_name'],bic_code=bank['bic_code'])
    except IntegrityError as ie:
        print(f"Integrity error:\n\n{ie}")


def create_billing_info():
    try:
        for i in range(1,101,1):
            bank = random.choice(BANKS)
            example_iban = bank['iban_example']
            random_num = random.choice(range(1,100,1))
            if random_num < 10:
                iban_control_num = "0" + str(random_num)
            if random_num >= 10:
                iban_control_num = str(random_num)
            if i < 10:
                iban_addition = "00" + str(i)
            if 10 <= i < 100:
                iban_addition = "0" + str(i)
            if i == 100:
                iban_addition = str(i)

            user_iban = example_iban.replace("00", iban_control_num) + iban_addition
            BillingInfo.create(
                from_user=int(i),
                bank=int(bank['bank_id']),
                bank_iban=user_iban
            )
    except IntegrityError as ie:
        print(f"Integrity error:\n\n{ie}")


def create_payed_items(order, transaction):
        bought_products = order['products']
        # iterate over product list from order > create order with same order_number for every product  
        for product in bought_products:
            product_index = int(product['product_id'] - 1)
            unit_price = products[product_index]['unit_price']
            sell_price = float(unit_price) * int(product['buy_quantity'])

            PayedOrderItem.create(
                order_number = order['order_number'],
                seller_id = products[product_index]['made_by_user'],
                buyer_id = order['buyer'],
                product_id = product['product_id'],
                product_name = products[product_index]['product_name'],
                product_price = float(unit_price),
                buy_quantity = product['buy_quantity'],
                sell_price = float(sell_price),
                transaction = transaction.transaction_id
            )


def create_user_transaction(transaction: dict):
    transaction = UserTransaction.create(
        buyer = transaction['buyer'],
        order_number = transaction['order_number'],
        order_total_price = transaction['order_total_price'] 
    )
    return transaction


def create_orders():
    orders = create_order_data()
    # create orders
    for order in orders:
        bought_products = order['products']
        sell_prices = []
        # iterate over product list from order > create order with same order_number for every product  
        for product in bought_products:
            product_index = int(product['product_id'] - 1)
            unit_price = products[product_index]['unit_price']
            sell_price = float(unit_price) * int(product['buy_quantity'])
            sell_prices.append(sell_price)
            OrderItem.create(
                order_number = order['order_number'],
                buyer = order['buyer'],
                product = product['product_id'],
                buy_quantity = product['buy_quantity'],
                sell_price = float(sell_price),
                is_payed = order['is_payed']
            )
        if order['is_payed']:
            transaction = {
                'buyer': int(order['buyer']),
                'order_number': int(order['order_number']),
                'order_total_price': float(sum(sell_prices))
            }
            created_transaction = create_user_transaction(transaction)
            create_payed_items(order, created_transaction)
            


def populate_test_database():
    db.connect(reuse_if_open=True)
    create_tables()
    create_tags()
    create_users()
    create_products()
    create_banks()
    create_billing_info()
    create_orders()
    db.close()

