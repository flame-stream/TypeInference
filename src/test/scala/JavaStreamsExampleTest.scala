import org.scalatest._

trait X extends Attr                 // named stream attribute
trait XGreaterThan2 extends X        // sequence of modifications
trait XGreaterThan2Squared extends XGreaterThan2

trait Y extends Attr                 // named stream attribute

object JavaStreamsExampleTest {
  implicit val Xgt2wY: XGreaterThan2 with Y = new XGreaterThan2 with Y
  implicit val Xgt2swY: XGreaterThan2Squared with Y = new XGreaterThan2Squared with Y
  implicit val Xgt2s: XGreaterThan2Squared = new XGreaterThan2Squared {}

  type XFilter = Transition[X, XGreaterThan2]
  type XMap = Transition[XGreaterThan2, XGreaterThan2Squared]
  type XProjection = Projection[X]

  type Src = X with Y
  type Dst = XGreaterThan2Squared

  type Empty = Object
}

class JavaStreamsExampleTest extends FlatSpec with Matchers {

  import JavaStreamsExampleTest._

  "Type assertions" should "stand" in {

    val xFilter = new XFilter
    val xMap = new XMap
    val xProjection = new XProjection

    // stream.filter(x > 2).map(x^2).project(x,y->x)
    val src: Src = new X with Y
    val dst1 = xProjection[Y, XGreaterThan2Squared](xMap[Y](xFilter[Y](src)))
    val dst2 = xMap[Empty](xProjection[Y, XGreaterThan2](xFilter[Y](src)))
    val dst3 = xMap[Empty](xFilter[Empty](xProjection[Y, X](src)))

    dst1 shouldBe a [Dst]
    dst2 shouldBe a [Dst]
    dst3 shouldBe a [Dst]
  }
}
