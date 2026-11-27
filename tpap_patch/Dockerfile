FROM python:3.13-slim-bookworm AS builder
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*
COPY build_patch.py /build_patch.py
RUN python /build_patch.py /payload

FROM python:3.13-slim-bookworm
COPY --from=builder /payload /payload
COPY manage_patch.py /manage_patch.py
COPY test_manage_patch.py /test_manage_patch.py
RUN cd / && python -m unittest -v test_manage_patch
CMD ["python", "-u", "/manage_patch.py", "app"]
