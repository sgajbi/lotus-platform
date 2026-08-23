FROM busybox:1.36.1-musl AS probe

FROM otel/opentelemetry-collector-contrib:0.111.0
COPY --from=probe /bin/busybox /bin/busybox
