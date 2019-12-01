import scala.reflect.runtime.universe._
import scala.tools.reflect.ToolBox

object SQLGroupByExample {

  trait flightId
  trait day
  trait price

  trait ledFlightId extends flightId
  trait ledDay extends day
  trait ledPrice extends price

  trait helFlightId extends flightId
  trait helDay extends day
  trait helPrice extends price

  trait lhrFlightId extends flightId
  trait lhrDay extends day
  trait lhrPrice extends price

  type ledSchedule = {val fLed: ledFlightId; val dLed: ledDay; val pLed: ledPrice}
  type helSchedule = {val fHel: helFlightId; val dHel: helDay; val pHel: helPrice}
  type lhrSchedule = {val fLhr: lhrFlightId; val dLhr: lhrDay; val pLhr: lhrPrice}

  def leftSchedulesJoin[S1 <: helSchedule, S2 <: lhrSchedule]: S1 => S2 => S1 with S2 = ???

  def rightSchedulesJoin[S1 <: ledSchedule, S2 <: helSchedule]: S1 => S2 => S1 with S2 = ???

  trait ledFlightFiltered extends ledFlightId
  trait lhrFlightFiltered extends lhrFlightId
  def filterNulls[S <: {val fLed : ledFlightId; val fLhr : lhrFlightId}]
  : S => S {val fLed: ledFlightFiltered; val fLhr: lhrFlightFiltered} = ???

  trait helDayGrouped extends helDay
  trait priceAggregated extends price
  type groupedByDay = {val dHel: helDayGrouped; val minPr1: priceAggregated; val minPr2: priceAggregated}

  def groupByDayHavingMinPrice[S <: helSchedule]
  : S => groupedByDay = ???

  trait pricePlus extends price
  def selectMin[S <: groupedByDay]: S => groupedByDay = ???

  def selectPlus[S <: groupedByDay]: S => {val day: helDayGrouped; val price: pricePlus} = ???

  val led: ledSchedule = new {
    val fLed: ledFlightId = new ledFlightId {}
    val dLed: ledDay = new ledDay {}
    val pLed: ledPrice = new ledPrice {}
  }

  val hel: helSchedule = new {
    val fHel: helFlightId = new helFlightId {}
    val dHel: helDay = new helDay {}
    val pHel: helPrice = new helPrice {}
  }

  val lhr: lhrSchedule = new {
    val fLhr: lhrFlightId = new lhrFlightId {}
    val dLhr: lhrDay = new lhrDay {}
    val pLhr: lhrPrice = new lhrPrice {}
  }

  def main(args: Array[String]): Unit = {
    {
      val tree1 = reify {
        selectPlus(
          selectMin(
            groupByDayHavingMinPrice(
              filterNulls(
                rightSchedulesJoin
                (led)
                (leftSchedulesJoin
                (hel)
                (lhr))
              ))))
      }.tree

      val tree2 = reify {
        selectPlus(
          selectMin(
            groupByDayHavingMinPrice(
              filterNulls(
                leftSchedulesJoin(
                  rightSchedulesJoin
                  (led)
                  (hel))
                (lhr)
              ))))
      }.tree

      //    val tree3 = reify {
      //      selectPlus(
      //        selectMin(
      //            filterNulls(
      //              leftSchedulesJoin(
      //                rightSchedulesJoin
      //                (groupByDayHavingMinPrice(led))
      //                (groupByDayHavingMinPrice(hel)))
      //              (lhr)
      //            )))
      //    }.tree

      val tb = runtimeMirror(getClass.getClassLoader).mkToolBox()
      val typ1 = tb.typecheck(tree1).tpe
      val typ2 = tb.typecheck(tree2).tpe

      tb.typecheck(q"implicitly[$typ1 =:= $typ2]")
    }
  }
}
