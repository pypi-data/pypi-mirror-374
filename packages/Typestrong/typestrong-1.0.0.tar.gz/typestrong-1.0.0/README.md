# Typestrong

## Aggressive Typehints

With this decorator, at runtime a function's arguments are compared against the typehints 
and if they don't match, an excpetion is thrown.   
This essentially makes your function arguments dynamically typed.  
This is not the same as static analysis like mypy, which trusts you'll pass in values to match the typehints.   

## Install 
<tt>pip install typestrong</tt>  

## Import  
<tt>from Typestrong import typsestrict</tt> 

## Use
Simply attach 

```python
@typestrong
def addition(val1: int, val2: int):
    print(val1 + val2)
```  
To any function.   
Now if you pass in an argument during runtime it's assessed against the typehints 
and if they don't match up an exception is thrown.  

For example if I call that above function with  
```python
addition('test', 1)
```
I will get the exception   
<tt>Argument "arg3" in function "examplefunc" expected value of type "<class \'list\'>", got "<class \'int\'>"</tt>
run tests with
```pytest Test_Typestrong.py -v```

## Usage with __init__ and classes
Don't attach the decorator to a class, attach it to the __init__ function if required.  
For instance methods it assumes that <tt>self</tt> is the first argument in the function defintion. This follows PEP standards.  
Example

```python
class ExampleClass:
    @typestrong
    def __init__(self, var1: str):
        self.var1 = var1
    
    @typestrong
    def examplefunc(self), val2: str:
        return(f'example value {val2}')
```  
In this example the __init__ function is now strictly enforcing the typehints, and so is the examplefunc

## Subclasses
Yes it recognises a subclass being passed into a function in-place of a typehinted parent class, and will consider this a matching argument.  (No exception)
```python
class ParentClass:
   
class ChildClass(ParentClass)

@typestrong
def exampleFunc(var1: ParentClass):
    print('in here')
```  
exampleFunc will work if ppased a ParentClass instance of a childClass instance  

## Literals 
I'm a big fan of typing.Literal, it allows you to pass in a list of possible values,  
Typestrong will ensure the incoming value is found within the Literal options.  So 
```python 
@typestrong
def exampleFunc(var1: Literal['Cat', 'Dog', 'Fish']):
    print('var1')
```
Will work if passed a 'Cat' value, but not if passed a 'Cow' or integer.  

## Unions 
Unions are honoured as well, so if you write 
```python
@typestrong
def exampleFunc(var1: (str | int)):
    pass
```  
It will check that the incoming value matches one of those.  
The typechecking makes a recursive call, so any value it can check outside a union it is able to check inside one.  

