# pyptrs
This library provides real pointers (as in languages like C) and some memory access utilites.

# Installation
```pip install pyptrs```

# Creating A Pointer
You should never create pointers directly. Instead, use the functions below:

pyptrs.**pointer_to_object**(obj, c_object = False)

Return a pointer to _obj_. _c_object_ specifies whether to treat the obj as a python object or a C object.
If _c_object_ is True, obj must be an instance of a ctypes C data type. 
You can learn more information about these data types from [here](https://docs.python.org/3/library/ctypes.html#fundamental-data-types), [here](https://docs.python.org/3/library/ctypes.html#arrays) and [here](https://docs.python.org/3/library/ctypes.html#structures-and-unions)

pyptrs.**pointer_to_address**(address, ctype = None)

Return a pointer that points to the given _address_. If _ctype_ is None, a python object is assumed to be living in that address. 
Otherwise, _ctype_ must be the ctypes C data type corresponding to the type of the object living in _address_.
You can learn more information about these data types from [here](https://docs.python.org/3/library/ctypes.html#fundamental-data-types), [here](https://docs.python.org/3/library/ctypes.html#arrays) and [here](https://docs.python.org/3/library/ctypes.html#structures-and-unions)

# Pointer Objects
Pointer.**get_size**()

Return the number of bytes occupied by the pointed object in memory.

Pointer.**get_mem**()

Return a bytes object representing the pointed object.

Pointer.**temp_value**(value, force_write = False)

Dereference and assign _value_ to the pointed object, then return a context manager that reverts this assignment at exit.
If size of _value_ is bigger than the pointed object, a MemoryError will be raised. In order to prevent this, pass True to _force_write_.

# Simulated Operators

pyptrs.**dereference**(pointer, *value, force_write = False)

If _value_ is not given, it just dereferences the pointer. 
If _value_ is given, it must be a single argument and it dereferences the pointed object and assigns _value_ to it then returns a _backup_id_ that can be passed to pyptrs.mem_restore(). 
If size of _value_ is bigger than the pointed object, a MemoryError will be raised. In order to prevent this, pass True to _force_write_.
Type of value can be anything if the pointed object is a python object.
If the type of the pointed object is a C type, type of _value_ must be the corresponding ctypes C data type.

pyptrs.**address_of**(obj, c_object = False)

Return address of the _obj_. If _c_object_ is True type of _obj_ must be a ctypes C data type. 
You can learn more information about these data types from [here](https://docs.python.org/3/library/ctypes.html#fundamental-data-types), [here](https://docs.python.org/3/library/ctypes.html#arrays) and [here](https://docs.python.org/3/library/ctypes.html#structures-and-unions)
If _c_object_ is True, address of the actual C object is returned, not the address of its ctypes wrapper.

# Utils
pyptrs.**mem_read**(address, amount = 1)

Read _amount_ bytes starting from _address_ and return them as a bytes object.

pyptrs.**mem_write**(address, data = b"")

Write the bytes represented by _data_ to _address_ and return a _backup_id_ that can be passed to pyptrs.mem_restore().

pyptrs.**mem_restore**(backup_id)

Revert the changes done to memory by the function that returned _backup_id_.

pyptrs.**mem_restore_last**()

Revert the last change done to memory either by pyptrs.dereference() or pyptrs.mem_write().
