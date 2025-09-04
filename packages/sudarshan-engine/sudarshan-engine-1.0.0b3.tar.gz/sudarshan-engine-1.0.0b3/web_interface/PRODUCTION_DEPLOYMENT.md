# 🚀 Sudarshan Engine Web Interface - Production Deployment Guide

This guide provides step-by-step instructions for deploying the Sudarshan Engine web interface to production with Cloudflare SSL certificates.

## 📋 Prerequisites

### System Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Root or sudo access
- Domain name (sudarshanengine.xyz) configured with Cloudflare
- Cloudflare account with SSL certificate access

### Cloudflare Setup
1. **Domain Configuration**: Ensure sudarshanengine.xyz points to your server
2. **SSL/TLS Settings**:
   - SSL/TLS encryption mode: Full (strict)
   - Always Use HTTPS: On
   - Automatic HTTPS Rewrites: On
3. **Origin Server Certificate**: Generate from Cloudflare dashboard

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Your Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Clone or upload your code to the server
cd /home/ubuntu
git clone https://github.com/Yash-Sharma1810/sudarshan_engine.git
cd sudarshan_engine/web_interface
```

### Step 2: Obtain Cloudflare SSL Certificates

1. **Login to Cloudflare Dashboard**
2. **Navigate to SSL/TLS > Origin Server**
3. **Click "Create Certificate"**
4. **Configure Certificate**:
   - Hostnames: sudarshanengine.xyz, *.sudarshanengine.xyz
   - Certificate Validity: 15 years (maximum)
   - Private key format: RSA (2048)
5. **Download Certificate Files**:
   - Certificate: `sudarshanengine.xyz.pem`
   - Private Key: `sudarshanengine.xyz.key`

### Step 3: Install SSL Certificates

```bash
# Create SSL directory
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

# Copy certificates (replace with your actual certificate paths)
sudo cp /path/to/sudarshanengine.xyz.pem /etc/ssl/certs/
sudo cp /path/to/sudarshanengine.xyz.key /etc/ssl/private/

# Set proper permissions
sudo chmod 644 /etc/ssl/certs/sudarshanengine.xyz.pem
sudo chmod 600 /etc/ssl/private/sudarshanengine.xyz.key
sudo chown root:root /etc/ssl/certs/sudarshanengine.xyz.pem
sudo chown root:root /etc/ssl/private/sudarshanengine.xyz.key
```

### Step 4: Run Production Deployment Script

```bash
cd /home/ubuntu/sudarshan_engine/web_interface

# Make script executable
chmod +x deploy_production.sh

# Run deployment
sudo ./deploy_production.sh
```

### Step 5: Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable sudarshan-web
sudo systemctl enable nginx
sudo systemctl start sudarshan-web
sudo systemctl start nginx

# Check status
sudo systemctl status sudarshan-web
sudo systemctl status nginx
```

### Step 6: Test Deployment

```bash
# Test SSL certificate
python3 test_ssl.py

# Test web interface
curl -I https://sudarshanengine.xyz

# Test API endpoints
curl https://sudarshanengine.xyz/api/health
```

## 🔒 Security Configuration

### SSL Certificate Validation

The deployment includes:
- **Certificate Path**: `/etc/ssl/certs/sudarshanengine.xyz.pem`
- **Private Key Path**: `/etc/ssl/private/sudarshanengine.xyz.key`
- **Certificate Authority**: Cloudflare Origin CA

### Security Headers

Nginx is configured with:
- `Strict-Transport-Security`: Forces HTTPS
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `X-XSS-Protection`: XSS protection
- `Content-Security-Policy`: Restricts resource loading

### Rate Limiting

- **General requests**: 100 per minute per IP
- **API requests**: 10 per second per IP
- **Health checks**: Unlimited (no rate limiting)

## 🌐 DNS Configuration

Ensure your DNS records are properly configured:

```
Type: A
Name: @
Value: YOUR_SERVER_IP

Type: A
Name: www
Value: YOUR_SERVER_IP

Type: CNAME
Name: sudarshanengine
Value: sudarshanengine.xyz
```

## 🔍 Monitoring & Maintenance

### Log Files

- **Application logs**: `/home/ubuntu/sudarshan_engine/web_interface/logs/`
- **Nginx access logs**: `/var/log/nginx/sudarshan_access.log`
- **Nginx error logs**: `/var/log/nginx/sudarshan_error.log`

### Health Checks

```bash
# Application health
curl https://sudarshanengine.xyz/api/health

# Detailed status
curl https://sudarshanengine.xyz/api/status
```

### SSL Certificate Renewal

Cloudflare Origin certificates are valid for 15 years, but monitor expiration:

```bash
# Check certificate expiry
openssl x509 -in /etc/ssl/certs/sudarshanengine.xyz.pem -text -noout | grep "Not After"
```

## 🚨 Troubleshooting

### Common Issues

#### SSL Certificate Errors
```bash
# Check certificate validity
openssl x509 -in /etc/ssl/certs/sudarshanengine.xyz.pem -text

# Test SSL connection
openssl s_client -connect sudarshanengine.xyz:443 -servername sudarshanengine.xyz
```

#### Nginx Configuration Issues
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo nginx -s reload

# Check error logs
sudo tail -f /var/log/nginx/sudarshan_error.log
```

#### Application Issues
```bash
# Check application logs
tail -f /home/ubuntu/sudarshan_engine/web_interface/logs/web_interface.log

# Restart application
sudo systemctl restart sudarshan-web

# Check application status
sudo systemctl status sudarshan-web
```

### Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Check firewall status
sudo ufw status
```

## 🔄 Updates & Maintenance

### Application Updates

```bash
cd /home/ubuntu/sudarshan_engine
git pull origin main
cd web_interface

# Restart services
sudo systemctl restart sudarshan-web
sudo nginx -s reload
```

### SSL Certificate Updates

When renewing Cloudflare certificates:

```bash
# Backup old certificates
sudo cp /etc/ssl/certs/sudarshanengine.xyz.pem /etc/ssl/certs/sudarshanengine.xyz.pem.backup
sudo cp /etc/ssl/private/sudarshanengine.xyz.key /etc/ssl/private/sudarshanengine.xyz.key.backup

# Install new certificates
sudo cp new_certificate.pem /etc/ssl/certs/sudarshanengine.xyz.pem
sudo cp new_private_key.key /etc/ssl/private/sudarshanengine.xyz.key

# Reload Nginx
sudo nginx -s reload
```

## 📞 Support

For deployment issues:
1. Check the logs in `/home/ubuntu/sudarshan_engine/web_interface/logs/`
2. Run the SSL test: `python3 test_ssl.py`
3. Verify Cloudflare SSL settings
4. Check DNS propagation

## ✅ Deployment Checklist

- [ ] Server prepared with required packages
- [ ] Domain configured in Cloudflare
- [ ] SSL certificates obtained and installed
- [ ] Production deployment script executed
- [ ] Services started and enabled
- [ ] SSL certificate validated
- [ ] HTTPS access confirmed
- [ ] API endpoints tested
- [ ] Firewall configured
- [ ] Monitoring set up

---

**🎉 Your Sudarshan Engine web interface is now live at https://sudarshanengine.xyz!**

Remember to:
- Regularly backup your SSL certificates
- Monitor certificate expiration dates
- Keep the application and system updated
- Review logs for security issues