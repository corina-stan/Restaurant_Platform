# Stage 1: Build Python dependencies
FROM python:3.12-alpine AS builder

WORKDIR /app

# Install build dependencies for compiling cryptography, Pillow, psycopg2, etc.
RUN apk add --no-cache gcc musl-dev postgresql-dev libffi-dev jpeg-dev zlib-dev make

COPY requirements.txt .

# Install dependencies in user space to easily copy them to the next stage
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production runtime image
FROM python:3.12-alpine

WORKDIR /app

# Install runtime libraries (PostgreSQL client libraries, Pillow image libraries, libffi, and shell)
RUN apk add --no-cache postgresql-libs jpeg zlib libffi

# Copy the compiled user packages from builder
COPY --from=builder /root/.local /root/.local

# Add the user binary path so scripts like daphne are executable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copy the django codebase
COPY . .

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Explicitly launch with shell interpreter to prevent line-ending compatibility issues
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
