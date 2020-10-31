## Ongoing notes

This is may be not a Ben-Yelles algorithm. :) 

But it works for simple types. It is, honestly speaking, just a dfs.

### Dependencies

* [frozen dictionary](https://pypi.org/project/frozendict/)
* [lark](https://pypi.org/project/lark/)

### Testing

Types are provided in ```.hs``` files in test folder. They are predictably in haskell-like syntax.
Along with them testing script is provided. If you have all dependencies installed in is sufficient
just to run ```python3 test.py```.
 * ```cntx.hs``` - file with given terms which will be used to inhabitate the given type
 * ```inh.hs``` - file with *one* term to inhabitate
 
  