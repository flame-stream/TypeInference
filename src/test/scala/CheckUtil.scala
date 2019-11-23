object CheckUtil {
  def assertType[U] = new {
    def apply[T](t: T)(implicit eq: T =:= U) = ()
  }
}
