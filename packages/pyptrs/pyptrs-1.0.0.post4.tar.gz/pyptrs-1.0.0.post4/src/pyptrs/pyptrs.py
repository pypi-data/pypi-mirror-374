#Python uses references, actual pointers are almost never needed.
#Use this library only if you have a very special use case (like injecting python interpreter into a process and manipulating the process memory)


import ctypes
import sys


mem_backups = []
backup_counter = 0


class Pointer():          
    def _refer_to_cdata(self, pointable, implicit_object = True):
        self.garbage_lock1 = pointable # protect from garbage collection
        self.pointer_type = type(pointable)
        self._address = ctypes.addressof(pointable)
        self.c_memory = True
        self.implicit_object = implicit_object
        
    def refer_to_cdata(self, cdata):
        self._refer_to_cdata(cdata, implicit_object = False)
        
    def refer_to(self, obj):
        # py_object internally stores a second level pointer to obj
        # Address of the first level pointer can be obtained with ctypes.addressof(py_object)
        # Then, this pointer can be used to get back obj
        py_object = ctypes.py_object(obj)
        self._refer_to_cdata(py_object)
        
    def change_address(self, address, ctype = None):
        self._address = address
        if ctype is None:
            c_memory = False
        else:
            c_memory = True
        self.c_memory = c_memory
        self.implicit_object = False
        self.pointer_type = ctype

    def get_address(self):
        if  self.c_memory == False:
            address = ctypes.cast(self._address, ctypes.c_void_p).value
        else:
            if self.implicit_object:
                first_level = ctypes.cast(self._address, ctypes.POINTER(ctypes.c_void_p)).contents
                address = first_level.value
            else:
                address = self._address
        return address

    def dereference(self):
        if self.c_memory == False:           
            return ctypes.cast(self._address, ctypes.py_object).value
        else:
            pointer = ctypes.cast(self._address, ctypes.POINTER(self.pointer_type))
            c_data = pointer.contents
            if self.implicit_object == True:
                return c_data.value
            return c_data

    def get_size(self):
        value = self.dereference()
        if self.c_memory and not self.implicit_object:
            size = ctypes.sizeof(value)
        else:
            size = sys.getsizeof(value)
        return size

    def get_mem(self):
        size = self.get_size()
        memory = mem_read(self.get_address(), size)
        return memory

    def overwrite_mem(self, data, force_write = False):
        """Passing True to force_write may not do any observable harm if the overflow is small but this is a very bad habit. It's undefined behavior after all."""
        size_limit = self.get_size()
        if len(data) > size_limit and not force_write:
            error = "Size of data argument "
            error = error + "(" + str(len(data)) + ") "
            error = error + "is bigger than size of the pointed object "
            error = error + "(" + str(size_limit) + ")\n"
            error = error + "If you are sure of allocated memory is enough, pass force_write = True.\n"
            error = error + "Misuse of this argument can cause a buffer overflow and crash the python interpreter"
            raise MemoryError(error)
        backup_id = mem_write(self.get_address(), data = data)
        return backup_id
    
    def change_value(self, value, force_write = False):
        """Byte copy of value to the pointed address

        This is a very powerful function. But great power brings great responsibility.
        If you modify immutable literals (yes you can do it), you will never be able to use them again but their modified forms.
        This can mess up not only your main script, but also other modules you use. Literals are shared through the whole runtime.
        Only way to solve this problem is calling mem_restore() function."""
        if type(value) != type(self.dereference()) and self.c_memory and not self.implicit_object:
            raise TypeError("type of value argument is different than type of the ctypes object which hold the address of the C object this Pointer instance refers to.")
        self.garbage_lock2 = value
        if self.c_memory and not self.implicit_object:
            pointer = pointer_to_object(value, c_object = True)
        else:
            pointer = pointer_to_object(value)
        self.garbage_lock3 = pointer
        new_mem = pointer.get_mem()
        backup_id = self.overwrite_mem(new_mem, force_write = force_write)        
        return backup_id

    class ChangeValue:
        def __init__(self, owner, value, force_write = False):            
            self.owner = owner
            self.value = value
            self.force_write = force_write
            
        def __enter__(self):
            self.backup_id = self.owner.change_value(self.value, force_write = self.force_write)
            return self.owner
        
        def __exit__(self, exc_type, exc_value, traceback):
            mem_restore(self.backup_id)

    def temp_value(self, value, force_write = False):
        """Return a context manager for change_value() method. Memory will always be restored on exit."""
        temp_changer = self.ChangeValue(self, value, force_write = force_write)
        return temp_changer
            
    @property
    def value(self):
        return self.dereference()

    @value.setter
    def value(self, new_value):
        return self.change_value(new_value)


def pointer_to_object(obj, c_object = False):
    pointer = Pointer()
    if c_object == False:
        pointer.refer_to(obj)
    else:
        try:
            pointer.refer_to_cdata(obj)
        except TypeError:
            raise TypeError("type of obj must be a ctypes type when c_object is True")
    return pointer


def pointer_to_address(address, ctype = None):
    pointer = Pointer()
    pointer.change_address(address, ctype = ctype)
    return pointer


def dereference(pointer, *value, force_write = False):
    """This function acts like dereference operator (*) of C"""
    if len(value) > 1:
        raise TypeError(f"dereference() takes max 2 positional arguments but {len(value)+1} was given")
    if not value:
        return pointer.dereference()
    else:
        return pointer.change_value(value[0], force_write = force_write)


def address_of(obj, c_object = False):
    """This function acts like address-of operator (&) of C"""
    pointer = pointer_to_object(obj, c_object = c_object)
    return pointer.get_address()


def get_memory_proxy(address, array_type = ctypes.c_char * 1):
    pointer = pointer_to_address(address, ctype = array_type)
    data = dereference(pointer)
    return data


def mem_read(address, amount = 1):
    data = get_memory_proxy(address, array_type = ctypes.c_char * amount)
    return data[:]


def mem_write(address, data = b""):
    current_data = get_memory_proxy(address, array_type = ctypes.c_ubyte * len(data))
    global mem_backups
    global backup_counter
    backup = list(current_data)
    backup_id = backup_counter
    backup_counter += 1
    mem_backups.append([current_data, backup])
    current_data[:] = data
    return backup_id

    
def mem_restore(backup_id):
    global mem_backups
    global backup_counter    
    info = mem_backups[backup_id]
    del mem_backups[backup_id]
    backup_counter -= 1 
    backup = info.pop()
    memory_region = info.pop()
    memory_region[:] = backup


def mem_restore_last():
    global mem_backups
    global backup_counter
    info = mem_backups.pop()
    backup_counter -= 1
    backup = info.pop()
    memory_region = info.pop()
    memory_region[:] = backup    
    
    

