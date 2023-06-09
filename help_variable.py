manually_add_product_error_text = f"""
Please use following schema / key-value pairs for a product:

product={'{'}
'product_name':'example_name',
'description':'example_description',
'unit_price':12.95,
'units_in_stock':12
{'}'}

product_name must not be empty or exceed 40 characters
description must not be empty or exceed 250 characters
unit_price must be a FLOAT and CANNOT BE NEGATIVE
units_in_stock must be an INTEGER and CANNOT BE NEGATIVE

For the product_tag or category you will be prompted to choose from a list
"""
