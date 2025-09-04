# Sudarshan Engine Web Interface - Deployment Guide

This guide covers deploying the Sudarshan Engine web interface to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Security Configuration](#security-configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Linux, macOS, or Windows (WSL)
- **Python**: 3.8 or higher
- **Memory**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application, plus space for logs and SSL certificates

### Optional Dependencies

- **Docker**: For containerized deployment
- **Nginx**: For reverse proxy and SSL termination
- **SSL Certificates**: For HTTPS (Let's Encrypt recommended)

## Quick Start

### 1. Local Development

```bash
cd sudarshan_engine/web_interface
python server.py
```

### 2. Production Deployment

```bash
# Automatic deployment
./deploy_local.sh

# Or manual setup
pip install -r requirements.txt
gunicorn --config gunicorn.conf.py wsgi:app
```

### 3. Docker Deployment

```bash
docker-compose up -d
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here

# Authentication
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=secure-password-here

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SSL (optional)
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem

# Logging
LOG_LEVEL=INFO
LOG_FILE=web_interface.log
```

### SSL Certificate Generation

For development/testing:

```bash
python generate_ssl.py
```

For production, obtain certificates from:
- **Let's Encrypt**: Free, automated
- **Commercial CA**: DigiCert, GlobalSign
- **Cloud provider**: AWS ACM, Google Cloud CA

## Deployment Options

### 1. Local Server

Best for: Development, small teams, internal use

```bash
./deploy_local.sh
```

Features:
- Automatic virtual environment setup
- SSL certificate generation
- Gunicorn WSGI server
- Process monitoring

### 2. Docker Container

Best for: Isolated deployment, cloud platforms

```bash
# Build and run
docker-compose up -d

# With Nginx reverse proxy
docker-compose --profile nginx up -d

# Scale the application
docker-compose up -d --scale sudarshan-web=3
```

### 3. Cloud Platforms

#### Heroku

```bash
./deploy_cloud.sh heroku
```

Required environment variables:
- `HEROKU_APP_NAME`: Your Heroku app name

#### AWS EC2

```bash
AWS_INSTANCE_ID=i-1234567890 ./deploy_cloud.sh aws
```

Prerequisites:
- EC2 instance with security group allowing ports 22, 80, 443
- SSH key pair configured

#### Google Cloud Run

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: sudarshan-web
spec:
  template:
    spec:
      containers:
      - image: gcr.io/PROJECT-ID/sudarshan-web
        ports:
        - containerPort: 8000
```

#### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sudarshan-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sudarshan-web
  template:
    metadata:
      labels:
        app: sudarshan-web
    spec:
      containers:
      - name: sudarshan-web
        image: sudarshan-web:latest
        ports:
        - containerPort: 8000
        env:
        - name: FLASK_ENV
          value: "production"
```

### 4. Traditional Web Server

#### Nginx + Gunicorn

```nginx
# /etc/nginx/sites-available/sudarshan
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Apache + mod_wsgi

```apache
# /etc/apache2/sites-available/sudarshan.conf
<VirtualHost *:80>
    ServerName yourdomain.com

    WSGIDaemonProcess sudarshan user=www-data group=www-data threads=5
    WSGIScriptAlias / /path/to/sudarshan-web/wsgi.py

    <Directory /path/to/sudarshan-web>
        WSGIProcessGroup sudarshan
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
</VirtualHost>
```

## Security Configuration

### HTTPS Setup

1. **Obtain SSL certificate**
2. **Configure server**

For Docker:
```yaml
environment:
  - SSL_CERT_PATH=/home/app/ssl/cert.pem
  - SSL_KEY_PATH=/home/app/ssl/key.pem
```

For direct deployment:
```bash
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

### Firewall Configuration

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### Security Headers

The application automatically includes:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security`
- `Content-Security-Policy`

### Rate Limiting

Default limits:
- 200 requests per day per IP
- 50 requests per hour per IP
- 10 encryption/decryption requests per minute
- 5 key generation requests per minute

## Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:8000/api/health

# Detailed status
curl http://localhost:8000/api/status
```

### Logs

```bash
# Application logs
tail -f logs/web_interface.log

# Gunicorn logs
tail -f logs/gunicorn.log

# Docker logs
docker-compose logs -f sudarshan-web
```

### Metrics

Monitor these key metrics:
- Response time
- Error rate
- CPU/Memory usage
- Request rate
- SSL certificate expiry

### Log Rotation

```bash
# Using logrotate
cat > /etc/logrotate.d/sudarshan-web << EOF
/home/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    create 644 app app
    postrotate
        docker-compose restart sudarshan-web
    endscript
}
EOF
```

## Troubleshooting

### Common Issues

#### Server won't start

```bash
# Check Python version
python3 --version

# Check dependencies
pip list | grep flask

# Check port availability
lsof -i :8000

# Check logs
tail -f logs/web_interface.log
```

#### SSL certificate errors

```bash
# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:443 -servername localhost
```

#### High memory usage

```bash
# Monitor processes
ps aux | grep gunicorn

# Check Gunicorn configuration
# Reduce workers in gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
```

#### Slow response times

```bash
# Check system resources
top
iostat -x 1

# Profile application
python -m cProfile server.py

# Optimize Gunicorn settings
worker_class = 'gevent'  # For I/O bound applications
```

### Performance Tuning

#### Gunicorn Configuration

```python
# gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
```

#### Nginx Optimization

```nginx
worker_processes auto;
worker_connections 1024;

# Enable gzip
gzip on;
gzip_types text/plain application/json application/javascript text/css;

# Cache static files
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/opt/backups/sudarshan-web"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env ssl/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## Support

For issues and questions:
- Check the logs in `logs/` directory
- Review the troubleshooting section above
- Open an issue on GitHub
- Check the documentation at docs.sudarshan-engine.org

---

**Sudarshan Engine** - Protecting the future with quantum-safe cryptography.