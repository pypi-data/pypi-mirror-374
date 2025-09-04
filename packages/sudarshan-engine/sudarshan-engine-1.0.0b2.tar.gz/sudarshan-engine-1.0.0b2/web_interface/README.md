# Sudarshan Engine Web Interface

A browser-based interface for the Sudarshan Engine quantum-safe cybersecurity platform.

## Features

- **🔐 Quantum-Safe Operations**: Encrypt and decrypt files using post-quantum cryptography
- **🔑 Key Management**: Generate and manage Kyber KEM and Dilithium signature keypairs
- **👛 Wallet Support**: Create and manage quantum-safe digital wallets
- **📊 Real-time Feedback**: Progress indicators and status updates
- **🎨 Modern UI**: Responsive design with dark/light theme support
- **🌐 Local Server**: Runs locally for maximum security and privacy

## Quick Start

### Development

```bash
cd sudarshan_engine/web_interface
python server.py
```

Navigate to: http://localhost:8080

### Production Deployment

#### Option 1: Local Server
```bash
cd sudarshan_engine/web_interface
./deploy_local.sh
```

#### Option 2: Docker
```bash
cd sudarshan_engine/web_interface
docker-compose up -d
```

#### Option 3: Cloud (Heroku/AWS)
```bash
cd sudarshan_engine/web_interface
./deploy_cloud.sh heroku  # or aws, docker
```

### 3. Use the Interface

- **Encrypt Files**: Select a file, choose algorithm and compression, add metadata
- **Decrypt Files**: Select a .spq file to decrypt
- **Generate Keys**: Create quantum-safe keypairs for encryption/signing
- **Wallet**: Create and manage quantum-safe wallets

## Requirements

- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Sudarshan Engine backend (automatically detected)

## Architecture

```
Web Browser
    ↓
HTTP Server (Python)
    ↓
Sudarshan Engine Core
    ↓
Post-Quantum Cryptography (liboqs)
```

## Security Features

- **Local Operation**: All processing happens on your device
- **No Data Transmission**: Files never leave your computer
- **Secure Key Generation**: Uses cryptographically secure random number generation
- **Input Validation**: Comprehensive validation of all user inputs
- **Error Handling**: Fail-fast approach with clear error messages
- **Production Security**: HTTPS, authentication, rate limiting, security headers

## Production Deployment

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- SSL certificates (for HTTPS in production)

### Environment Configuration

1. Copy `.env` file and configure:
```bash
cp .env .env.production
# Edit .env.production with your settings
```

2. Key environment variables:
- `FLASK_ENV`: Set to `production`
- `SECRET_KEY`: Strong random key for Flask sessions
- `BASIC_AUTH_USERNAME/PASSWORD`: Credentials for API access
- `CORS_ORIGINS`: Allowed origins for CORS

### Deployment Options

#### 1. Local Production Server

```bash
# Automatic deployment
./deploy_local.sh

# Manual deployment
pip install -r requirements.txt
gunicorn --config gunicorn.conf.py wsgi:app
```

#### 2. Docker Deployment

```bash
# Build and run
docker-compose up -d

# With Nginx reverse proxy
docker-compose --profile nginx up -d
```

#### 3. Cloud Deployment

```bash
# Heroku
./deploy_cloud.sh heroku

# AWS EC2
AWS_INSTANCE_ID=i-1234567890 ./deploy_cloud.sh aws

# Docker Registry
DOCKER_REGISTRY=myregistry.com ./deploy_cloud.sh docker
```

#### 4. Domain Deployment (sudarshanengine.xyz)

**Easy Deployment:**
```bash
# One-command deployment to your domain
./deploy_domain.sh
```

**Manual Deployment:**
```bash
# 1. Install dependencies
pip install flask flask-cors werkzeug gunicorn

# 2. Run on your domain (port 80 for HTTP)
gunicorn --bind 0.0.0.0:80 --workers 4 server:app

# 3. For HTTPS (recommended for production)
# Get SSL certificate from your domain provider
# Then run with SSL:
gunicorn --bind 0.0.0.0:443 --workers 4 --certfile ssl/cert.pem --keyfile ssl/key.pem server:app
```

**Access your web interface at:**
- 🌐 **https://sudarshanengine.xyz**
- 🔒 **HTTPS recommended for production**

### SSL/TLS Configuration

For HTTPS in production:

1. **Generate certificates**:
```bash
python generate_ssl.py
```

2. **For Docker**: Mount SSL directory
```yaml
volumes:
  - ./ssl:/home/app/ssl:ro
```

3. **For cloud providers**: Use their SSL termination features

### Monitoring and Logging

- **Logs**: Check `logs/` directory
- **Health check**: `GET /api/health`
- **Metrics**: Gunicorn access logs
- **Monitoring**: Use tools like Prometheus/Grafana

### Backup and Recovery

- **Database**: No database used (stateless)
- **Keys**: Backup `.env` and `ssl/` directories
- **Logs**: Archive log files regularly

## API Endpoints

The web interface provides the following API endpoints:

- `GET /api/status` - Server status and capabilities
- `GET /api/info` - Application information
- `POST /api/encrypt` - Encrypt files
- `POST /api/decrypt` - Decrypt files
- `POST /api/generate-keys` - Generate keypairs

## File Formats

### Input Files
- Any file type supported
- Maximum size: Limited by browser and system memory

### Output Files
- **Encrypted**: `.spq` format (quantum-safe encrypted)
- **Decrypted**: Original file format restored
- **Keys**: JSON format with keypair information

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Troubleshooting

### Server Won't Start
- Ensure Python 3.8+ is installed
- Check that port 8080 is not in use
- Try a different port: `python server.py --port 8081`

### Interface Not Loading
- Clear browser cache
- Try a different browser
- Check browser console for JavaScript errors

### Operations Fail
- Ensure backend connection is active
- Check file permissions
- Verify sufficient disk space

## Development

### Project Structure
```
web_interface/
├── index.html          # Main HTML interface
├── styles.css          # CSS styling
├── app.js             # JavaScript functionality
├── server.py          # Python HTTP server
└── README.md          # This file
```

### Adding New Features
1. Update `index.html` for UI elements
2. Add styles in `styles.css`
3. Implement functionality in `app.js`
4. Add API endpoints in `server.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This web interface is part of the Sudarshan Engine project and follows the same AGPL-3.0 license.

## Support

- **Documentation**: [docs.sudarshanengine.xyz](https://docs.sudarshanengine.xyz)
- **Issues**: [GitHub Issues](https://github.com/sudarshan-engine/sudarshan-engine/issues)
- **Community**: [Discord](https://discord.gg/sudarshan-engine)

---

**Sudarshan Engine** - Protecting the future with quantum-safe cryptography.