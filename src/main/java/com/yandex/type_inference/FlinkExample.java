package com.yandex.type_inference;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.util.Collector;

import java.util.ArrayList;
import java.util.Optional;

interface Log {
    String payload();

    long ts();

    String userId();
}

class FrontLog implements Log {
    @Override
    public String payload() {
        return null;
    }

    @Override
    public long ts() {
        return 0;
    }

    @Override
    public String userId() {
        return null;
    }

    String frontId() {
        return "front";
    }
}

class AccessLog implements Log {

    @Override
    public String payload() {
        return null;
    }

    @Override
    public long ts() {
        return 0;
    }

    @Override
    public String userId() {
        return null;
    }
}

class ZipLog implements Log {
    @Override
    public String payload() {
        return null;
    }

    @Override
    public long ts() {
        return 0;
    }

    @Override
    public String userId() {
        return null;
    }

    Optional<Object> frontFeatures() {
        return Optional.empty();
    }

    Optional<Object> userFeatures() {
        return Optional.empty();
    }
}

interface ModelResult {
    boolean sessionEnd();
}

interface PainMetric {
    long value();
}


public class FlinkExample {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        final DataStreamSource<Log> accessLogSource = env.fromCollection(new ArrayList<>());
        final DataStreamSource<Log> frontLogsSource = env.fromCollection(new ArrayList<>());

        final SingleOutputStreamOperator<Object> joinedStream = accessLogSource
                .union(frontLogsSource)
                .flatMap((value, out) -> {
                    //(4): join events
                    out.collect(value);
                });

        joinedStream.union(joinedStream
                .map(value -> {
                    //(5): add front features
                    return value;
                })
                .map(value -> {
                    //(6): add user features
                    return value;
                })
                .flatMap((value, out) -> {
                    //(7): model inference
                    out.collect((ModelResult) null);
                })
        ).flatMap((value, out) -> {
            //(9): window aggregation
            out.collect((PainMetric) null);
        }).map(value -> {
            //(10): front features
            return null;
        });
        
        env.execute("Window WordCount");
    }
}
