# Pynums
A library for adding configurable Enum-type objects to python!

If you have any issues or suggestions go to the github issues page and raise one! If you have any ideas the are very much welcome :D

## How to create Enums:
    from Pynums import Enum
    
    MyEnum1 = Enum(arg1="hello world")
    
    print(MyEnum1.arg1)
    
Output:

    hello world

Enums can also be created like this, allowing for more specific arguments:

    from Pynums import Enum
    
    class MyEnum1(Enum):
        def __init__(self, requiredarg, **kwargs):
            self.requiredarg = requiredarg
            super().__init__(**kwargs) # **kwargs are here so that you can add required arguments, as well as any other arguments you may want per Enum.
    
    myenum = MyEnum1(requiredarg="hello", otherarg="world") # Note that "otherarg" will not have any auto-completion as it is created at runtime.
    
    print(myenum.requiredarg, myenum.otherarg)

Output:

    hello world
