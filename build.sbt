name := "TypeInference"

version := "0.1"

scalaVersion := "2.12.1"

scalacOptions ++= Seq("-unchecked", "deprecation")

libraryDependencies += "com.chuusai" %% "shapeless" % "2.3.3"
libraryDependencies += "io.chymyst" %% "curryhoward" % "0.3.7"
libraryDependencies += "org.scala-lang" % "scala-compiler" % "2.12.1"
libraryDependencies += "com.google.guava" % "guava" % "12.0"

libraryDependencies += "org.scalatest" %% "scalatest" % "3.0.8" % Test

// https://mvnrepository.com/artifact/org.apache.flink/flink-java
libraryDependencies += "org.apache.flink" % "flink-java" % "1.11.2"
// https://mvnrepository.com/artifact/org.apache.flink/flink-streaming-java
libraryDependencies += "org.apache.flink" %% "flink-streaming-java" % "1.11.2" % "provided"


