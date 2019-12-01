import com.google.common.collect.ImmutableMap;
import java.util.stream.Stream;

public class JavaStreamsDraft {
    public static void main(String[] args) {
        Stream.of(ImmutableMap.of(
                "x", 1,
                "y", 2))
                .filter(p -> p.get("x") > 0)
                .map(p -> ImmutableMap.<String, Integer>builder().putAll(p).put("x", p.get("x") * p.get("x")).build())
                .map(p -> ImmutableMap.of("x", p.get("x")))
                .forEach(System.out::println);
    }
}
