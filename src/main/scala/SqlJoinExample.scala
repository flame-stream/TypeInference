import scala.reflect.runtime.universe._
import scala.tools.reflect.ToolBox

object SqlJoinExample {

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

  def select[S <: { val oAge: ownerAge; val oId: ownerId; val pId: petId; val pAge: petAgeFiltered }]: S => count = ???

  def main(args: Array[String]): Unit = {
    val tree1 = reify { select(where(join(join(src1)(src2))(src3))) }.tree
    val tree2 = reify { select(where(join(src1)(join(src2)(src3)))) }.tree
//    val tree3 = reify { select(join(join(where(src1))(src2))(src3)) }.tree
    val expTree = reify { new count {} }.tree

    val tb = runtimeMirror(getClass.getClassLoader).mkToolBox()
    val typ1 = tb.typecheck(tree1).tpe
    val typ2 = tb.typecheck(tree2).tpe
    val expTyp = tb.typecheck(expTree).tpe
  }
}
