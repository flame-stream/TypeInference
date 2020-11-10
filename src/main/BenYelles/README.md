## Ongoing notes

This is may be not a Ben-Yelles algorithm. :) It looks([one](https://youtu.be/g42JGNkz4YU) [two](https://youtu.be/UUF67seAoxc) [rus]) like one though.

But it works for simple types. It is, honestly speaking, just a bfs.

### Dependencies

* [frozen dictionary](https://pypi.org/project/frozendict/)
* [lark](https://pypi.org/project/lark/)

### Testing

Types are provided in ```.hs``` files in test folder. They are predictably in haskell-like syntax.
Along with them testing script is provided. If you have all dependencies installed in is sufficient
just to run ```python3 test.py```.
 * ```cntx.hs``` - file with given terms which will be used to inhabitate the given type
 * ```inh.hs``` - file with *one* term to inhabitate
 
 
### How does it work?

#### Simple types

Usually this algorithm is suitable for simply typed lambda calculus. 
It uses three basic rules to construct type inhabitants:

```
       x:a -> G
(I)   ----------
       G |- x:a 

       G |- e : a -> b  G |- x : a
(E->) ------------------------------
               G |- e x : b

       G |- e : b   G |- x : a
(I->) ------------------------------
          G |- \x -> e : a -> b
```

Small english letters denote simple types. 

The usual way to solve inhabitation problem is to construct
inhabitation machine but I can't draw here, so I will write:
There are: Context(it is ```G``` from above) and desired type ```t```.

```inhabitate t```:
1. Check all variables in context and choose those which have type ```t```.
2. Add them to answers.
3. Check all functions in context and choose those which return ```t```.
4. For each function for each argument ```inhabitate``` it's type.

It looks simple until we realise that our context is infinite,
because it is possible to construct infinite lambda with different types.
So in our algorithm we pretend that rule of ```(I->)``` does not exist.

Than our context ```G``` is restricted to our initial context that we provide
in the begging of the search.

On this point we can't say this algorithm is solving inhabitation problem. 
It enumerates some terms of the given type, but some terms will never appear
in our enumeration.

#### Motivation
It must be mentioned that if we will describe our execution graph in terms of  ```λ->``` 
we will fix our graph and there will be no room for optimization. There are two ways to fight it. 
There are two systems that will provide some room: ```λ∩``` and ```λ2```. 

The worst thing is that inhabitation problem is undecidable for ```λ2``` and decidable
, but with big constraints for ```λ∩```. 
But as it was mentioned above we *do not need* to solve it. We want some terms of given type.

#### System F (```λ2```)
First of all the type inhabitation problem is undecidable for it.
It is possible to adapt algorithm from ```λ->``` for it to produce some terms.
In general we need to define the ```is inhabitant``` relation. 
Which is possible to define for any pair of terms which are simple types, functions or polymormphic types.

#### ```λ∩```
It is not very explored area, but this system is basically allowing term to have multiple types.
In general the type inhabitation problem is undecidable for it. 

At first we add some more rules:

```
      G |- M : a    G |- M : b    
(I∩) --------------------------
           G |- M : a∩b

      G |- M:a
(<)  ----------   a < b
      G |- M:b
      
(w)   G |- x:w

```

Everything below works only with an assumption that we can solve ```a < b```.

Then let us define rank for types:
```
    rank(a) = 0
    rank(a -> b) = max(rank(a) + 1, rank(b))
    rank(a ∩ b) = max(1, rank(a), rank(b))
```

If our system has only rank 2, then [there is](https://compsciclub.ru/courses/2017-autumn/6.331-type-inhabitation-problems/about/) ```EXPTIME```-hard inhabitation algorithm. 



 
 






  
