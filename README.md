# Type-level execution graph descriptions

Our goal is to design unified type-level descriptions for heterogeneous execution graphs.

## Concepts
* *Execution graph* &mdash; a set of parallel and consequtive opertaions on data resources represented in form of a graph. In current state of the problem we consider execution plans of SQL queries and Java Streams pipelines as a desired domain, aiming to generalize results to other execution graph specifications such as Apache Flink, CQL, etc. 

* *Type-level description* &mdash; data-oriented declarative specification of pre- and postconditions on arguments and outputs of operations abstracted from implementation. Essentially, an external type system that rejects invalid execution graphs.

* *Unified* descriptions as opposed to *heterogeneous* graphs suggest a way of maintaining system-wide invariants in an execution graph independently of underlying frameworks used in graph's operations.

<p align="center">
  <img src="https://sun9-33.userapi.com/c858124/v858124352/10e687/H5HP_JjePys.jpg">
</p>

## Motivation
* Schematization makes intents clearer, resulting in better maintainance and testing 
* In particular, type system makes specification more expressive by allowing user-defined types (data specifications). For example, operation's signature may tell about an applied change to the argument's sign or persistance of the argument's distribution
* Transparent prerequisites of obtaining a desired data resource enable automatic graph construction?

## Subtask

Express graphs produced by SQL and Java Streams (or any other functional pipeline abstraction i.e. C++ Ranges or a chain of higher order functions in Haskell) in terms of an existing type system.

## Milestone

An attempt to typecheck functional pipelines and SQL with use of Scala's structural subtyping and paramentric polymorphism to simulate row polymorphism. See a brief [explanation](https://brianmckenna.org/blog/row_polymorphism_isnt_subtyping) of structural subtyping and row polymorphism in comparison.

## Functional style pipelines 

Let's say we want to type the pipeline:

```cpp
stream.of({ x: 1, y: "hey" }).filter(x > 0).map(x -> x^2).project(x,y -> x)       // { x: 1 }
```

From perspective of a graph we are given one initial source of data and three consecutive operations that take a single source and produce a single outcome. Consider someone used the following type declarations to specify the operations and the source:

```scala
trait X                                    // traits represent properties of a data resource
trait Y                                
type Src = { val x: X; val y: Y }          // structural type represents an initial data resource 
```

```scala
trait XGreaterThan0 extends X              // inherited traits represent consecutive 
trait XGreaterThan0Squared extends XGreaterThan0       // operations over a property
```

```scala 
// operations' type declarations without implementation
def filter[S <: { val x: X }]: S => S { val x: XGreaterThan0 } = ???
def map[S <: { val x: XGreaterThan0 }]: S => S { val x: XGreaterThan0Squared } = ???
def project[XProp <: X]: { val x: XProp } => { val x: XProp } = ???
def src: Src = ???
```

The operations above could be defined simplier and still allow `project(map(filter(src)))` to compile. However, with polymorphic signatures we have here, we allow `map(project(filter(src)))` and `map(filter(project(src)))` to compile as well. Moreover, the types of the three expressions are all equivalent to `{ val x: XGreaterThan0Squared }` (see [below](#type-equivalence-in-functional-style-pipelines)). 

Two rules of subtyping allow the operation rearranging in this example:
* Covariance to express states of data that are neccessary consecutive
  ```scala
  implicitly[{val x: XGreaterThan0; val y: Y} <:< {val x: X; val y: Y}]
  implicitly[{val x: XGreaterThan0Squared; val y: Y} <:< {val x: XGreaterThan0; val y: Y}]
  ```
* Structural subtyping to express independently aquired properties

  ```scala
  type x = {val x: X}
  type y = {val y: Y}
  implicitly[{val x: X; val y: Y} <:< {val x: X}]
  implicitly[{val x: X; val y: Y} <:< {val y: Y}]

  type both = x with y
  implicitly[{val x: X; val y: Y} =:= both]  
  ```

It is a suggestion that similarly organized operation signatures can express all possible execution graphs for in an arbitrary case. 

The common type `{ val x: XGreaterThan0Squared }` of the statements raises a question of exhaustiveness of our examples. If there can be found all combinations of given operations and data sources that typecheck to a certain type, this would be equivalent to generation of all possible graphs that produce the desired resource.   

## Type inhabitation

There are [libraries](https://github.com/Chymyst/curryhoward) that generate a function body by provided type via Curry-Howard isomorphism and intuitionistic propositional logic teorem prover, e.g.:

```scala
scala> import io.chymyst.ch.anyOfType
import io.chymyst.ch.anyOfType

scala> def graphs[A, B, C, D, E] = anyOfType[A => (A => B) => (B => (C, D)) => (C, B)]()
graphs: [A, B, C, D, E]=> Seq[io.chymyst.ch.Function1Lambda[A,(A => B) => ((B => (C, D)) => (C, B))]]
```
This could be helpful if row polymorphism or subtyping and polymorphic types were supported.

## Describing SQL

An example of how join operations can be rearranged:

```scala
  // select count(*)
  // from ownership
  //  join pets on ownership.petId == pets.id
  //  join people on ownership.ownerId == people.id
  // where people.age < pets.age

  trait petId
  trait ownerId
  trait petAge
  trait ownerAge

  trait petAgeFiltered extends petAge
  trait ownerAgeFiltered extends ownerAge

  trait count

  type ownership = {val pId: petId; val o: ownerId}
  type pets = {val pId: petId; val pAge: petAge}
  type people = {val oId: ownerId; val oAge: ownerAge}

  def src1: ownership = ???
  def src2: pets = ???
  def src3: people = ???

  def join[S1, S2]: S1 => S2 => S1 with S2 = ???

  def where[S <: { val pAge: petAge; val oAge: ownerAge }]
    : S => S {val pAge: petAgeFiltered; val oAge: ownerAgeFiltered } = ???

  def select[S <: { val oAge: ownerAge; val oId: ownerId; val pId: petId; val pAge: petAgeFiltered }]
    : S => count = ???
  ```
  
  ```scala
  val tree1 = reify { select(where(join(join(src1)(src2))(src3))) }.tree      // compiles
  val tree2 = reify { select(where(join(src1)(join(src2)(src3)))) }.tree      // compiles
  val tree3 = reify { select(join(join(where(src1))(src2))(src3)) }.tree      // won't compile!!
  ```

## Summary of questions yet to answer
* Solvability of the inhabitation problem for types that describe functional pipelines and SQL
  * Is there any hope for automatic graph generation from row types?   
* Descriptiveness of the proposed type system at least for SQL 
  * Row types look good enough at a first glance...
* Any other approaches to schematization?
  * Try path-dependent instead of records?

## Type equivalence in Functional style pipelines

```scala
scala> import scala.reflect.runtime.universe._
       import scala.tools.reflect.ToolBox
       
       // ASTs of the expressions to typecheck
       val tree1 = reify { map(filter(project(src))) }.tree 
       val tree2 = reify { map(project(filter(src))) }.tree
       val tree3 = reify { project(map(filter(src))) }.tree
    
       val tb = runtimeMirror(getClass.getClassLoader).mkToolBox()
       
       // typechecking
       val typ1 = tb.typecheck(tree1).tpe
       val typ2 = tb.typecheck(tree2).tpe
       val typ3 = tb.typecheck(tree3).tpe
...
scala> typ1 // not normalized type representation of typ1
res0: tb.u.Type = scala.AnyRef{val x: X}{val x: XGreaterThan0}{val x: XGreaterThan0Squared}

scala> typ2 // not normalized type representation of typ1
res1: tb.u.Type = scala.AnyRef{val x: XGreaterThan0}{val x: XGreaterThan0Squared}

scala> typ3 // not normalized type representation of typ1
res2: tb.u.Type = scala.AnyRef{val x: XGreaterThan0Squared}

scala> type tX = scala.AnyRef{val x: X}
       type tXgt0 = tX{val x: XGreaterThan0}
       type tGt0 = scala.AnyRef{val x: XGreaterThan0}
       
       // checking type equivalence
       implicitly[tXgt0{val x: XGreaterThan0Squared} =:= {val x: XGreaterThan0Squared}]
       implicitly[tGt0{val x: XGreaterThan0Squared} =:= {val x: XGreaterThan0Squared}]
       implicitly[scala.AnyRef{val x: XGreaterThan0Squared} =:= {val x: XGreaterThan0Squared}]

defined type alias tX
defined type alias tXgt0
defined type alias tGt0
res3: =:=[tXgt0{val x: XGreaterThan0Squared},AnyRef{val x: XGreaterThan0Squared}] = <function1>
res4: =:=[tGt0{val x: XGreaterThan0Squared},AnyRef{val x: XGreaterThan0Squared}] = <function1>
res5: =:=[AnyRef{val x: XGreaterThan0Squared},AnyRef{val x: XGreaterThan0Squared}] = <function1>
```


