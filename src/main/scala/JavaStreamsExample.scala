import scala.reflect.runtime.universe._
import scala.tools.reflect.ToolBox

object JavaStreamsExample {

  trait X
  trait XGreaterThan0 extends X
  trait XGreaterThan0Squared extends XGreaterThan0

  trait Y

  // stream.filter(x > 0).map(x^2).project(x,y->x)
  type Src = { val x: X; val y: Y }
  def filter[S <: { val x: X }]: S => S { val x: XGreaterThan0 } = ???
  def map[S <: { val x: XGreaterThan0 }]: S => S { val x: XGreaterThan0Squared } = ???
  def project[XProp <: X]: { val x: XProp } => { val x: XProp } = ???
  def src: Src = ???

  def main(args: Array[String]): Unit = {
    val tree1 = reify { map(filter(project(src))) }.tree
    val tree2 = reify { map(project(filter(src))) }.tree
    val tree3 = reify { project(map(filter(src))) }.tree
    val expectedTree = reify { new { val x: XGreaterThan0Squared = new XGreaterThan0Squared {} } }.tree

    val tb = runtimeMirror(getClass.getClassLoader).mkToolBox()
    val typ1 = tb.typecheck(tree1).tpe
    val typ2 = tb.typecheck(tree2).tpe
    val typ3 = tb.typecheck(tree3).tpe
    val expectedTyp = tb.typecheck(expectedTree).tpe

    implicitly[{val x: XGreaterThan0; val y: Y} <:< {val x: X; val y: Y}]
    implicitly[{val x: XGreaterThan0Squared; val y: Y} <:< {val x: XGreaterThan0; val y: Y}]

    type x = {val x: X}
    type y = {val y: Y}
    implicitly[{val x: X; val y: Y} <:< {val x: X}]
    implicitly[{val x: X; val y: Y} <:< {val y: Y}]

    type both = x with y
    implicitly[{val x: X; val y: Y} =:= both]

    tb.typecheck(q"implicitly[$typ1 =:= $expectedTyp]")
  }
}
