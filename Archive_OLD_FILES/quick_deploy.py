"""
IntelliPart Quick Deploy Script
One-command deployment to production
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class IntelliPartDeployment:
    """Quick deployment utility for IntelliPart."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self.load_deployment_config()
        
    def load_deployment_config(self):
        """Load deployment configuration."""
        config = {
            "app_name": "intellipart",
            "port": 5002,
            "workers": 4,
            "host": "0.0.0.0",
            "environment": "production",
            "requirements": [
                "flask>=2.0.0",
                "scikit-learn>=1.0.0",
                "numpy>=1.20.0"
            ],
            "optional_requirements": [
                "gunicorn>=20.0.0",
                "redis>=4.0.0",
                "psycopg2-binary>=2.9.0"
            ]
        }
        return config
    
    def check_dependencies(self):
        """Check if all dependencies are installed."""
        print("🔍 Checking dependencies...")
        
        missing_deps = []
        for req in self.config["requirements"]:
            package = req.split(">=")[0]
            try:
                __import__(package.replace("-", "_"))
                print(f"  ✅ {package}")
            except ImportError:
                missing_deps.append(req)
                print(f"  ❌ {package} (missing)")
        
        if missing_deps:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
            install = input("Install missing dependencies? (y/n): ")
            if install.lower() == 'y':
                self.install_dependencies(missing_deps)
        else:
            print("✅ All dependencies satisfied!")
    
    def install_dependencies(self, packages):
        """Install missing dependencies."""
        print("📦 Installing dependencies...")
        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"  ✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"  ❌ Failed to install {package}")
    
    def create_production_config(self):
        """Create production configuration files."""
        print("⚙️  Creating production configuration...")
        
        # Create gunicorn config
        gunicorn_config = f"""
bind = "{self.config['host']}:{self.config['port']}"
workers = {self.config['workers']}
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
"""
        
        with open("gunicorn.conf.py", "w") as f:
            f.write(gunicorn_config)
        
        # Create production environment variables
        env_config = f"""
FLASK_ENV={self.config['environment']}
FLASK_APP=enhanced_intellipart_app.py
PORT={self.config['port']}
WORKERS={self.config['workers']}
"""
        
        with open(".env.production", "w") as f:
            f.write(env_config)
        
        print("✅ Production configuration created!")
    
    def create_docker_files(self):
        """Create Docker deployment files."""
        print("🐳 Creating Docker configuration...")
        
        # Dockerfile
        dockerfile = """
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5002/health || exit 1

# Run application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "enhanced_intellipart_app:app"]
"""
        
        with open("Dockerfile", "w") as f:
            f.write(dockerfile)
        
        # Docker Compose
        docker_compose = f"""
version: '3.8'

services:
  intellipart:
    build: .
    ports:
      - "{self.config['port']}:{self.config['port']}"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///production.db
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{self.config['port']}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

volumes:
  redis_data:
"""
        
        with open("docker-compose.yml", "w") as f:
            f.write(docker_compose)
        
        print("✅ Docker configuration created!")
    
    def create_deployment_scripts(self):
        """Create deployment scripts."""
        print("📜 Creating deployment scripts...")
        
        # Linux/Mac deployment script
        deploy_script = f"""#!/bin/bash
set -e

echo "🚀 Deploying IntelliPart to Production"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Health check
echo "🏥 Checking application health..."
if curl -f http://localhost:{self.config['port']}/health; then
    echo "✅ Application is healthy!"
    echo "🌐 IntelliPart is now available at: http://localhost:{self.config['port']}"
else
    echo "❌ Application health check failed"
    docker-compose logs intellipart
    exit 1
fi

echo "🎉 Deployment completed successfully!"
"""
        
        with open("deploy.sh", "w") as f:
            f.write(deploy_script)
        
        # Make executable
        os.chmod("deploy.sh", 0o755)
        
        # Windows deployment script
        deploy_script_win = f"""@echo off
echo 🚀 Deploying IntelliPart to Production
echo ======================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Build and start services
echo 🏗️  Building Docker images...
docker-compose build

echo 🚀 Starting services...
docker-compose up -d

echo ⏳ Waiting for services to be ready...
timeout /t 30

REM Health check
echo 🏥 Checking application health...
curl -f http://localhost:{self.config['port']}/health
if %errorlevel% equ 0 (
    echo ✅ Application is healthy!
    echo 🌐 IntelliPart is now available at: http://localhost:{self.config['port']}
) else (
    echo ❌ Application health check failed
    docker-compose logs intellipart
    exit /b 1
)

echo 🎉 Deployment completed successfully!
"""
        
        with open("deploy.bat", "w") as f:
            f.write(deploy_script_win)
        
        print("✅ Deployment scripts created!")
    
    def create_health_endpoint(self):
        """Add health check endpoint to the app."""
        print("🏥 Adding health check endpoint...")
        
        health_check_code = """
# Add this to your enhanced_intellipart_app.py

@app.route('/health')
def health_check():
    \"\"\"Health check endpoint for load balancers.\"\"\"
    try:
        # Basic health checks
        checks = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'ok',
            'search_engine': 'ok'
        }
        
        # Test database connectivity
        try:
            search_engine = enhanced_search_engine
            if search_engine and len(search_engine.parts) > 0:
                checks['parts_loaded'] = len(search_engine.parts)
            else:
                checks['database'] = 'warning'
        except Exception as e:
            checks['database'] = f'error: {str(e)}'
            checks['status'] = 'unhealthy'
        
        # Return appropriate HTTP status
        status_code = 200 if checks['status'] == 'healthy' else 503
        return jsonify(checks), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503
"""
        
        with open("health_check_code.txt", "w") as f:
            f.write(health_check_code)
        
        print("✅ Health check code saved to health_check_code.txt")
    
    def create_requirements_file(self):
        """Create requirements.txt file."""
        print("📋 Creating requirements.txt...")
        
        requirements = """# Core dependencies
flask>=2.0.0
scikit-learn>=1.0.0
numpy>=1.20.0

# Production dependencies
gunicorn>=20.0.0

# Optional dependencies for enhanced features
redis>=4.0.0
psycopg2-binary>=2.9.0

# Development dependencies
pytest>=6.0.0
black>=21.0.0
flake8>=3.9.0
"""
        
        with open("requirements.txt", "w") as f:
            f.write(requirements)
        
        print("✅ requirements.txt created!")
    
    def run_quick_deploy(self):
        """Run quick deployment process."""
        print("🚀 IntelliPart Quick Deploy")
        print("=" * 40)
        
        # Check current setup
        self.check_dependencies()
        
        # Create all necessary files
        self.create_requirements_file()
        self.create_production_config()
        self.create_docker_files()
        self.create_deployment_scripts()
        self.create_health_endpoint()
        
        print("\n" + "=" * 40)
        print("🎉 Quick Deploy Setup Complete!")
        print("=" * 40)
        
        print("\n📋 Next Steps:")
        print("1. Review generated configuration files")
        print("2. Add health check endpoint to your app")
        print("3. Run deployment:")
        print("   - Linux/Mac: ./deploy.sh")
        print("   - Windows: deploy.bat")
        print("   - Manual: docker-compose up -d")
        
        print("\n🌐 After deployment, access your app at:")
        print(f"   http://localhost:{self.config['port']}")
        
        print("\n🔧 Configuration files created:")
        files_created = [
            "requirements.txt",
            "Dockerfile", 
            "docker-compose.yml",
            "gunicorn.conf.py",
            ".env.production",
            "deploy.sh",
            "deploy.bat",
            "health_check_code.txt"
        ]
        
        for file in files_created:
            if os.path.exists(file):
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file}")
        
        print("\n💡 Pro Tips:")
        print("   - Use environment variables for sensitive config")
        print("   - Set up monitoring and logging in production")
        print("   - Configure SSL/HTTPS for secure access")
        print("   - Set up automated backups")
        
        return True

def main():
    """Main deployment function."""
    try:
        deployer = IntelliPartDeployment()
        deployer.run_quick_deploy()
        return True
    except Exception as e:
        print(f"❌ Deployment setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
