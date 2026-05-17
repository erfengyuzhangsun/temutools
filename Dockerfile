# ===== Stage 1: Build Go Backend =====
FROM golang:latest AS go-builder
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server ./cmd/server

# ===== Stage 2: Build Frontend =====
FROM node:latest AS frontend-builder
WORKDIR /app
COPY web/package.json web/package-lock.json* ./
RUN npm ci
COPY web/ ./
RUN npm run build

# ===== Stage 3: Minimal Runtime =====
FROM alpine:3.20
RUN apk add --no-cache ca-certificates tzdata wget
WORKDIR /app
COPY --from=go-builder /app/server ./server
COPY --from=frontend-builder /app/dist ./web/dist
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=3s --retries=3 \
  CMD wget -qO- http://localhost:8080/health || exit 1
CMD ["/app/server"]
