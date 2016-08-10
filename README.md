## Conanfile for the [BGFX](https://github.com/bkaradzic/bgfx) rendering library.


># Please submit pull requests if you can improve this package!


## Compiling/Testing instructions for this package

**Note:** These instructions are only for anyone wanting to help improve *this package*.
If you're just trying to use this package as a dependency in your own project, simply add
`bgfx/1.0@ckohnert/stable` to your requires section (in either `conanfile.txt` or
`conanfile.py`).

When iterating on this package itself, please follow the sequence below to
test whether the package is working for you.

```bash
$ conan export demo/testing
$ conan test_package 
```

Subsequent tests can skip building the package from source every time (it can take a
while and if you're iterating quickly, it's a pain).

```bash
$ conan test_package --build=never
```
