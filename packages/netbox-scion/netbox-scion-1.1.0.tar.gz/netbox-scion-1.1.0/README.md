# NetBox SCION Plugin

A comprehensive NetBox plugin for managing SCION (Scalability, Control, and Isolation On Next-generation networks) infrastructure.

[![PyPI](https://img.shields.io/pypi/v/netbox-scion)](https://pypi.org/project/netbox-scion/)
[![Python Version](https://img.shields.io/pypi/pyversions/netbox-scion)](https://pypi.org/project/netbox-scion/)
[![License](https://img.shields.io/github/license/aciupac/netbox-scion)](https://github.com/aciupac/netbox-scion/blob/main/LICENSE)

## ✨ Features

- **Organizations:** Manage SCION operators with metadata and descriptions
- **ISD-ASes:** Track Isolation Domain and Autonomous System identifiers with core nodes
- **Link Assignments:** Interface management with customer information and Zendesk integration
- **REST API:** Full CRUD operations with filtering and pagination
- **Export:** CSV and Excel export capabilities
- **Web Interface:** Advanced filtering and search capabilities

## 📦 Installation

```bash
pip install netbox-scion
```

## 🚀 Quick Start

### Prerequisites
- NetBox v4.0+ (either Docker or system installation)
- Python 3.8+ with pip

### Installation

Choose the method that matches your NetBox deployment:

#### Option 1: NetBox Docker Deployment

If you're using [netbox-docker](https://github.com/netbox-community/netbox-docker):

**1. Add plugin to requirements:**
```bash
# Edit your env/netbox.env file
PLUGINS_REQUIREMENTS=netbox-scion==1.0.0
```

**2. Configure the plugin:**
```python
# Edit configuration/plugins.py
PLUGINS = [
    'netbox_scion',
    # Your other plugins...
]
```

**3. Restart NetBox:**
```bash
cd /path/to/your/netbox-docker
docker-compose restart netbox netbox-worker
```

#### Option 2: System NetBox Installation

If NetBox is installed directly on your system:

**1. Install the plugin:**
```bash
# Install in your NetBox virtual environment
source /opt/netbox/venv/bin/activate
pip install netbox-scion==1.0.0
```

**2. Configure the plugin:**
```python
# Edit /opt/netbox/netbox/netbox/configuration.py
PLUGINS = [
    'netbox_scion',
    # Your other plugins...
]
```

**3. Run migrations and restart:**
```bash
# Run database migrations
cd /opt/netbox/netbox
python manage.py migrate

# Restart NetBox services (systemd example)
sudo systemctl restart netbox netbox-rq
```

### Verification

After installation, verify the plugin is working:

1. **Check installation:**
   ```bash
   # For Docker:
   docker exec netbox pip show netbox-scion
   
   # For system install:
   /opt/netbox/venv/bin/pip show netbox-scion
   ```

2. **Access the interface:**
   - Log into NetBox web interface
   - Look for "SCION" section in the sidebar
   - You should see: Organizations, ISD-ASes, SCION Link Assignments

### Advanced Installation

For custom Docker images, local wheel files, or complex deployments, see our [**Advanced Deployment Guide**](deployment/README.md) which covers:
- Custom Docker images with local wheel files
- Manual container installation
- Troubleshooting and development setup

## 🔧 API Endpoints

All endpoints support full CRUD operations with filtering, pagination, and export:

- **Organizations:** `/api/plugins/scion/organizations/`
- **ISD-ASes:** `/api/plugins/scion/isd-ases/`
- **Link Assignments:** `/api/plugins/scion/link-assignments/`

## 🎯 Navigation

The plugin adds a "SCION" section to the NetBox sidebar with:
- Organizations
- ISD-ASes  
- SCION Link Assignments

## 📁 Development

### For Plugin Users
**You don't need to clone this repository!** Simply install via pip using the instructions above.

### For Contributors & Developers

Only clone this repository if you want to:
- Contribute code changes
- Customize the plugin
- Use local development builds
- Test unreleased features

```bash
# Clone and setup for development
git clone https://github.com/aciupac/netbox-scion.git
cd netbox-scion

# Install in development mode
pip install -e .

# For advanced deployment scenarios
cp -r deployment/* /path/to/your/netbox-docker/
```

See [**deployment/README.md**](deployment/README.md) for advanced installation methods including custom Docker images and local wheel files.

### Project Structure
```
netbox_scion/
├── __init__.py              # Plugin configuration
├── models.py                # Data models
├── forms.py                 # Web forms
├── views.py                 # Web views
├── urls.py                  # URL routing
├── api/                     # REST API
├── templates/               # HTML templates
├── migrations/              # Database migrations
└── static/                  # CSS/JS assets
```

### Local Development
```bash
# Install in development mode
pip install -e .

# Run migrations
python manage.py migrate

# Create wheel package
python setup.py bdist_wheel
```

## 🐛 Troubleshooting

### Quick Fixes

**Plugin not appearing?**
- Check installation: `pip show netbox-scion` (or `docker exec netbox pip show netbox-scion`)
- Ensure `'netbox_scion'` is in your `PLUGINS` list
- Restart NetBox services

**For detailed troubleshooting, deployment issues, and advanced configuration, see our [**Advanced Deployment Guide**](deployment/README.md).**

### Getting Help
- 🐛 **Bug reports:** [GitHub Issues](https://github.com/aciupac/netbox-scion/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/aciupac/netbox-scion/discussions)
- 📚 **Detailed docs:** [deployment/README.md](deployment/README.md)

## 📝 License

Apache License 2.0
