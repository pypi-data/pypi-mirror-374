import sys
sys.path.insert(1,"/workspaces/BradleysStrings-python/src/BradleysStrings/")
sys.path.insert(2,"/home/runner/work/BradleysStrings-python/BradleysStrings-python/src/BradleysStrings/")
import BradleysStrings
def test_1():
    print("Testing insert(\"aaaaa\",2,\"b\")!")
    print(BradleysStrings.insert("aaaaa",2,"b"))
def test_2():
    print("Testing replaceatpos(\"aaaaa\",2,\"b\")!")
    print(BradleysStrings.replaceatpos("aaaaa",2,"b"))
def test_3():
    print("Testing replaceinstr(...)!")
    print(BradleysStrings.replaceinstr("aaaaabbbbbccccc123",replacedarray = ["b","1"],replacewitharr = ["r","4"]))

test_1()
test_2()
test_3()