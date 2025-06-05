###########################################################################################
# This Dockerfile runs an LMC-compatible websocket server at / on port 8000.              #
# To learn more about LMC, visit https://docs.openinterpreter.com/protocols/lmc-messages. #
# This container is optimized for Cursor's background agents with WebSocket support.      #
###########################################################################################

FROM python:3.11.8

# Set environment variables for WebSocket compatibility
# ENV OPENAI_API_KEY ...

ENV HOST 0.0.0.0
ENV PORT 8000
# ^ Sets the server host to 0.0.0.0, Required for the server to be accessible outside the container
# ^ Explicitly set PORT environment variable for WebSocket connections

# Install system dependencies for WebSocket support
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy required files into container
RUN mkdir -p interpreter scripts
COPY interpreter/ interpreter/
COPY scripts/ scripts/
COPY poetry.lock pyproject.toml README.md ./

# Create nginx configuration for WebSocket proxy
RUN mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
COPY <<EOF /etc/nginx/sites-available/websocket
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
EOF

# Enable the nginx site
RUN ln -s /etc/nginx/sites-available/websocket /etc/nginx/sites-enabled/
RUN rm -f /etc/nginx/sites-enabled/default

# Create supervisor configuration
COPY <<EOF /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stderr_logfile=/var/log/nginx.err.log
stdout_logfile=/var/log/nginx.out.log

[program:interpreter]
command=interpreter --server --host 127.0.0.1 --port 8000
autostart=true
autorestart=true
stderr_logfile=/var/log/interpreter.err.log
stdout_logfile=/var/log/interpreter.out.log
environment=HOST="127.0.0.1",PORT="8000"
EOF

# Expose ports for HTTP and WebSocket connections
EXPOSE 80 8000

# Install server dependencies with WebSocket support
RUN pip install ".[server]" websockets

# Create healthcheck for WebSocket connectivity
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Start supervisor to manage nginx and interpreter services
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]