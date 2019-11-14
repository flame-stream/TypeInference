trait Attr

trait Operation {
  //  type Src
  //  type Dst
}

trait Type

trait Exact[T] extends Type

trait AtLeast[T] extends Exact[T]

class Transition[A <: Attr, B <: A] extends Operation {
  //  type Src = AtLeast[A]
  //  type Dst = AtLeast[B]

  def apply[T](a: A with T)(implicit ret: B with T): B with T = ret
}

class Join[A <: Attr, B <: Attr] extends Operation {
  def apply[T, J <: A, S, K <: B](a: J with T, b: K with S)
                                 (implicit ret: J with T with K with S): J with T with K with S = ret
}

class Projection[A <: Attr] {
  //  type Src = AtLeast[A]
  //  type Dst = Exact[A]

  def apply[T, P <: A](a: P with T)(implicit ret: P): P = ret
}
