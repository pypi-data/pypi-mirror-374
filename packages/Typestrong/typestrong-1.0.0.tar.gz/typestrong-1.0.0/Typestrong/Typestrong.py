import typing
import types
import inspect 
from collections.abc import Callable

class ComparisonResult:
        
    passes: bool
    error_message: str
    
    def __init__(self, passes: bool, error_message: str):
        self.passes = passes
        self.error_message = error_message       


def _check_matching(funcname: str, key: str, value: any, typehint: type | types.GenericAlias) -> ComparisonResult:
    """
    #### Inputs:
        -@funcname: Function being tested 
        -@key: key from that function's kwargs
        -@value: value passed to that kwarg in calling the function
        -@typehint: the typehint associated with incoming_key in the function definition
    #### Expected Behaviour:
        - If Typing.get_origin returns a value on the typehint, this was typehinted with a parameter 
            e.g Typing Literal, or List[str], or UnionType 
        - if you put a typing instance into the union it becomes a typing.Union, otherwise it's a types.UnionType
        - #case 1: within this subset of values, if it was UnionType, then for each of the values in the union 
            check if the incoming value matches one of their types, if it does match one return True 
        - #case 2: if it doesn't match any of them, return an error
        - #case 3: within this subset of values, if it was typing.literal, it's a list of valid values for the argument so
            check if the incoming value was within those value, if not return ComparisonResult with failure message 
        - #case 4: The typehint is a literal, and the value is found within it, so return passing
        - #case 5: it's it's not Typing.Literal but it's some other non-fundamental type, we can only compare the base of this type 
            agains the incoming value, case 3 it doesn't match
        - #case 6:it does match the base type
        - The rest of the cases are primitives of classes, (non-parameterised types),
        - # case 7: The incoming type is subclass of the typehint, it passes 
        - # case 8: The incoming value's type doesn't match the hint, fails
        - # case 9, else it must pass, it matches the type
    #### Returns:
        - Either a ComparisonResult with True, '' (empty error string),
            or False '...'
    #### Side Effects:
        - None   
    """
    if(typing.get_origin(typehint) != None): 
        if(typing.get_origin(typehint) is typing.Union or typing.get_origin(typehint) is types.UnionType):
            for union_val in typing.get_args(typehint):
                assessment = _check_matching(funcname, key, value, union_val)
                if(assessment.passes == True): #case 1
                    return(ComparisonResult(True, ''))
            return(ComparisonResult(False, f'Argument "{key}" in function "{funcname}" expected value in {typing.get_args(typehint)}, got "{type(value)}" of value "{value}"')) # case 2
        elif(typing.get_origin(typehint) is typing.Literal): 
            expected_values = typing.get_args(typehint)
            if(value not in expected_values): #case 3
                return(ComparisonResult(False, f'Argument "{key}" in function "{funcname}" expected value in "{expected_values}", got "{value}"'))
            else:
                return(ComparisonResult(True, '')) #case 4
        
        else: 
            if(typing.get_origin(typehint) != type(value)): #case 5
                return(ComparisonResult(False, f'Argument "{key}" in function "{funcname}" expected value of type "{typing.get_origin(typehint)}", got "{type(value)}"' ))
            else: #case 6
                return(ComparisonResult(True, ''))
    else:
        if(issubclass(type(value), typehint)): #case 7
            return(ComparisonResult(True, ''))
        elif(typehint != type(value)): #case 8
            return(ComparisonResult(False, f'Argument "{key}" in function "{funcname}" expected value of type "{typehint}", got "{type(value)}"'))
        else: # case 9
            return(ComparisonResult(True, ''))
        

def _check_kwargs(funcname: str, kwargs_dict: dict, typehint_dict: dict) -> ComparisonResult:
    """
    #### Inputs:
        -@funcname: function these kwargs/hints relates to 
        -@kwargs_dict: dict of keyword->values 
        -@typehint_dict: dict of all the typehints for the funcname function, stored against their keywords
    #### Expected Behaviour:
        - For each item in the kwargs_dict, it's possible there was no typehint for 
            it, in which case there's nothing to compare, skip
        - if it is in the typehint dict, check the typehint matches the incoming value 
            using the _check_matching function
        - _check_matching returns a ComparisonResult, if a comparison doesn't pass then return
            early with this ComparisonResult
        - if all comparisons pass then return a passing ComparisonResult
    #### Returns:
        - ComparisonResult instance
    #### Side Effects:
        - None
    """
    for key, value in kwargs_dict.items():
        if(key not in typehint_dict):
            continue
        typehint = typehint_dict[key]
        result = _check_matching(funcname, key, value, typehint)
        if(not result.passes):
            return(result)
    return(ComparisonResult(True, ''))


def _construct_kwargs(args_list: list, kwargs_dict: dict, hint_dict: dict) -> dict:
    """
    #### Inputs:
        -@args_list: list of arguments passed into a function
        -@kwargs_dict: dict of keyword arguments passed into a function
        -@hint_dict: dict of typehints for the function (expected to be the result of func.__annotations__)
    #### Expected Behaviour:
        - This function turns args into kwargs, using the typehints
        - it relies on 2 facts of python
            1. arguments come first in function calls, followed by keyword arguments
            2. dicts are ordered
        - Using these 2 facts, if you have an argument passed in, it must correspond to the first
            typehinted argument, the second with the second typehinted etc
        - so loop through all the arguments and add them to the returned under the keyword found for them.
        - for kwargs passed in, just add them to the returned dict
    #### Returns:
        - Dict of function's arguments, with their corresponding 
    """
    return_dict = {}
    hint_name_list = list(hint_dict.keys())
    for arg, hint_name in zip(args_list, hint_name_list): 
        return_dict[hint_name] = arg
  
    for key, value in kwargs_dict.items():
        return_dict[key] = value
    return(return_dict)


def typestrong(func: Callable):
    
    def analyse_arguments(*args, **kwargs):    
        """
        #### Inputs:
            -@args:  tuple of any number of args 
            -@kwargs: dict of any number of kwargs
        #### Expected Behaviour:
            - analyses the incoming arguments of a function compared with that function's
                typehints, raising an exception if any of them don't match. 
            - If the first arg in the function being called is self, it's in 
                instance method, drop the instance argument, as it doesn't need checking
            - if there aren't any arguments or kwargs, nothing to analyse, return early
            - else, infer a dict of kwargs for the incoming mixture of args/kwargs, and compare 
                it with the typehints 
            - if the resulting comparison fails raise an exception
        #### Returns:
            - the incoming function, as it's a decorator 
        #### Side Effects:
            - None 
        #### Exceptions:
            - Thrown if the arguments don't match the typehints 
        """   
        args_used = list(args)
        kwargs_used = {x: y for x, y in kwargs.items()}
        if(len(inspect.getfullargspec(func).args) > 0 and inspect.getfullargspec(func).args[0] == 'self'): ### how does this not index out of bounds
            if('self' in kwargs_used):
                del(kwargs_used['self'])
            else:
                args_used.pop(0)
        if(len(args_used) + len(kwargs_used) > 0):
            hints = func.__annotations__
            kwarg_dict = _construct_kwargs(args_used, kwargs_used, hints)
            result = _check_kwargs(funcname=func.__name__, kwargs_dict=kwarg_dict, typehint_dict=hints)
            if(not result.passes):
                raise Exception(result.error_message)
        return(func(*args, **kwargs))
        
    return(analyse_arguments)
