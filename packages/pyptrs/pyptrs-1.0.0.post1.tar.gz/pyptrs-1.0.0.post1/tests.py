from pyptrs import *
import ctypes


def test1():
    x = 1234
    pointer = pointer_to_object(x)
    if dereference(pointer) is x:        
        return True
    else:
        return False


def test2():
    x = [1,2,3]
    address = address_of(x)
    pointer = pointer_to_address(address)
    dereference(pointer).append(4)
    if dereference(pointer) is x:
        return  True
    else:
        return False


def test3():
    """Equivalent c++ code:

    int pointer_test2()
    {
        int x[4] = { 1,2,3,0 };
        int(*pointer)[4] = &x;
        (*pointer)[3] = 4;
        for (int i = 0; i < 4; i++)
        {
            if ((*pointer)[i] != x[i])
            {
                return false;
            }
        }
        return true;
    }
    
    """
    x = [1,2,3,0]
    address = address_of(x)
    pointer = pointer_to_address(address)
    dereference(pointer)[3] = 4
    for i in range(4):
        if not (dereference(pointer)[i] is x[i]):            
            return False
    return True


def test4():
    a = 24532
    p = pointer_to_object(a)
    c_memory = p._address
    p2 = pointer_to_address(c_memory, ctype = ctypes.py_object)
    if p2.dereference().value == a:
        return True
    else:
        return False


def test5():
    x = [1,2,3]
    pointer = pointer_to_address(address_of(x))
    if dereference(pointer) is x:
        return True
    else:
        return False


def test6():
    a = 0xaaaaaaaaaaaaa
    pointer = pointer_to_object(a)
    b = 0xfffffffffffff
    dereference(pointer, b)
    if a == b:
        mem_restore_last()
        return True
    else:
        return False

def test7():
    a = "abc"
    pointer = pointer_to_object(a)
    pointer.change_value("def")
    if a == "def":
        mem_restore_last()
        return True
    else:
        return False


def test8():
    a = bytes(b"abc")
    pointer = pointer_to_object(a)
    pointer.change_value(bytes(b"def"))
    if a == bytes(b"def"):
        mem_restore_last()
        return True
    else:
        return False


def test9():
    a = bytes(b"abc")
    pointer = pointer_to_object(a)
    pointer.change_value(12354087532633467)
    if a == 12354087532633467:
        mem_restore_last()
        return True
    else:
        return False


def test10():    
    a = 0x1235ab
    b = ctypes.c_int(a)
    pointer = pointer_to_object(b, c_object = True)
    pointer.value = ctypes.c_int(5)
    if b.value == 5:
        return True
    else:
        return False


def test11():
    pointer = pointer_to_object("a" * 4096) 
    pointer.change_value("b")
    pointer2 = pointer_to_object("c" * 4097) 
    pointer2.change_value("d")
    var = "e" * 4097
    pointer3 = pointer_to_object(var) 
    pointer3.change_value("f")
    if "a" * 4096 == "b" and "c" * 4097 != "d" and var == "f":
        mem_restore_last()
        mem_restore_last()
        mem_restore_last()
        return True
    else:
        return False


def test12():    
    pointer = pointer_to_object("abc")
    backup_id = pointer.change_value("def")
    if "abc" == "def":
        mem_restore(backup_id)
        return True
    else:
        return False

def test13():
    pointer = pointer_to_object(True)
    backup_id = pointer.change_value(False)
    if True == False:
        mem_restore(backup_id)
        return True
    else:
        return False


def test14():
    a = [1,2,3]
    pointer = pointer_to_object(a)
    backup_id = pointer.change_value([4,5,6])
    if a == [4,5,6]:
        mem_restore(backup_id)
        return True
    else:
        return False


def test15(): # doesnt work on some python versions
    class MyClass:
        def __init__(self, var):
            self.var = var    
    a = "a" * 10000
    pointer = pointer_to_object(a)
    x = MyClass(5)
    pointer.change_value(x)
    if a.var == 5: # a != x because ctypes doesn't have original object return but all their attributes are common        
        return True
    else:        
        return False


def test16():    
    a = "abc"
    pointer = pointer_to_object(a)
    pointer.temp_value("def")
    check1 = a == "abc"
    with pointer.temp_value("def") as p:        
        check2 = a == "def"
        check3 = p is pointer
    check4 = a == "abc"
    if check1 and check2 and check3 and check4:
        return True
    else:
        return False


def test17():    
    class MyClass:
        __slots__ = ["var"]
        def __init__(self, var):
            self.var = var
    a = MyClass(10)
    pointer = pointer_to_object(a)
    x = MyClass(20)
    pointer.change_value(x)
    if a.var == 20:        
        return True
    else:
        return False


def test18():
    a = ctypes.c_int(10)
    p1 = pointer_to_address(address_of(a, c_object = True), ctype = ctypes.c_int)
    if p1.dereference().value == 10:
        return True
    else:
        return False
    
    
if __name__ == "__main__":
    if test1() and test2() and test3() and test4() and test5() and test6() and test7() and test8() and test9() and test10() and test11() and test12() and test13() and test14() and test16() and test17() and test18():
        print("[+] all tests are successful")
    else:
        print("some tests are failed")
