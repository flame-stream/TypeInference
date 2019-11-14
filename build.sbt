name := "TypeInference"

version := "0.1"

scalaVersion := "2.13.1"

scalacOptions ++= Seq("-unchecked", "deprecation")

libraryDependencies += "com.chuusai" %% "shapeless" % "2.3.3"
libraryDependencies += "org.scala-lang" % "scala-reflect" % "2.13.1"
libraryDependencies += "org.scalatest" %% "scalatest" % "3.0.8" % Test