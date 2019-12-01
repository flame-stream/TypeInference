abstract case class Resource(name: String, attrs: List[Resource])
class AtLeast(name: String, attrs: List[Resource]) extends Resource(name, attrs)
class AtMost(name: String, attrs: List[Resource]) extends Resource(name, attrs)
class Exact(name: String, attrs: List[Resource]) extends Resource(name, attrs)

class GraphGen
