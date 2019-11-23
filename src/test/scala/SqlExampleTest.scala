import org.scalatest._
import scala.reflect.runtime.universe._
import scala.tools.reflect.ToolBox

trait Age extends Attr                 // named stream attribute
trait AgeGreaterThan18 extends Age     // sequence of modifications

trait Name extends Attr                // named stream attribute
trait Surname extends Attr             // named stream attribute
trait Id extends Attr                  // named stream attribute

object SqlExampleTest {
  implicit val IAN: Id with Name with Age = new Id with Name with Age
  implicit val IANS: Id with Age with Name with Surname = new Id with Name with Surname with Age
  implicit val IAgt18NS: Id with AgeGreaterThan18 with Name with Surname = new Id with Name with Surname with AgeGreaterThan18
  implicit val IN: Name with Age = new Name with Age
  implicit val ANS: Name with Surname with AgeGreaterThan18 = new Name with Surname with AgeGreaterThan18

  type PersonFilter = Transition[Age, AgeGreaterThan18]
  type PersonProjection = Projection[Name with Surname with Age]
  type IdJoin = Join[Id, Id]
  type NameJoin = Join[Name, Name]

  type Src1 = Name with Id
  type Src2 = Age with Id
  type Src3 = Name with Surname
  type Dst = Name with Surname with AgeGreaterThan18

  type Empty = Object
}

class SqlExampleTest extends FlatSpec with Matchers {
  import SqlExampleTest._

  "Type assertions" should "stand" in {

    val ageFilter = new PersonFilter
    val nameIdProjection = new PersonProjection
    val idJoin = new IdJoin
    val nameJoin = new NameJoin

    // select name, age
    // from names
    //  join ages on names.id == ages.id
    //  join surnames on names.name == surnames.name
    // where age >= 18
    val src1: Src1 = new Name with Id
    val src2: Src2 = new Age with Id
    val src3: Src3 = new Name with Surname

    val dst1 = nameIdProjection[Id, Name with Surname with AgeGreaterThan18](
      ageFilter[Id with Name with Surname](
        nameJoin[Id with Age, Name, Surname, Name](
          idJoin[Name, Id, Age, Id](src1, src2), src3)))

    val dst2 = nameIdProjection[Id, Name with Surname with AgeGreaterThan18](
      ageFilter[Id with Name with Surname](
        idJoin[Name with Surname, Id, Age, Id](
          nameJoin[Id, Name, Surname, Name](
            src1, src3), src2)))

    val dst3 = nameIdProjection[Id, Name with Surname with AgeGreaterThan18](
      nameJoin[Id with AgeGreaterThan18, Name, Surname, Name](
        idJoin[Name, Id, AgeGreaterThan18, Id](
          src1,
          ageFilter[Id](src2)),
        src3))

    CheckUtil.assertType[Dst](dst1)
    CheckUtil.assertType[Dst](dst2)
    CheckUtil.assertType[Dst](dst3)
  }
}
