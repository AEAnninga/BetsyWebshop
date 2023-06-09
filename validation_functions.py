from inquirer import errors

def raise_validation_error(validation_type: str,  max_length: int = 0, answer_length: int = 0):
    if validation_type == "float":
        raise errors.ValidationError('', reason='Not a valid number: Please enter an integer or a float!')
    if validation_type == "int":
        raise errors.ValidationError('', reason='Not a valid number: Please enter an integer!')
    if validation_type == "string":
        if answer_length == 0:
            raise errors.ValidationError('', reason=f'PLease use more than {answer_length} characters!')
        else:    
            raise errors.ValidationError('', reason=f'You used {answer_length} characters! Do not use more than {max_length} characters!')


# function for displaying error when selecting own product
def is_own_product(condition: bool):
    if condition == False:    
        raise errors.ValidationError('', reason='Not a valid product_id: You own this product!')
    else:
        return True
    

# function for checking if product_id is in database
def product_exists(condition: bool):
    if condition == False:    
        raise errors.ValidationError('', reason='This product does not exist in the database (anymore)!')
    else:
        return True
    


# function for checking if input can be parsed to float
def is_float(answer) -> bool:
    # if you expect None to be passed:
    if answer is None: 
        raise_validation_error(validation_type="float")
        return False
    try:
        float(answer)
        if float(answer) < 0:
            return False
        else:
            return True
    except ValueError:
        return False
    
  
# function for checking if input can be parsed to int
def is_int(answer) -> bool:
    # if you expect None to be passed:
    if answer is None:
        raise_validation_error(validation_type="int") 
        return False
    try:
        int(answer)
        if int(answer) < 0:
            return False
        else:
            return True
    except ValueError:
        return False


# function for checking if input string is too big
def is_string_not_too_big(answer: str, length: int = 0) -> bool:
    if answer is None:
        raise_validation_error(validation_type="string", max_length=length, answer_length=len(answer))
        return False
    try:
        is_not_too_big = 0 < len(str(answer)) < length
        if is_not_too_big:
            return True
        if not is_not_too_big:
            raise_validation_error(validation_type="string", max_length=length, answer_length=len(answer))
            return False
    except: 
        return False
    

