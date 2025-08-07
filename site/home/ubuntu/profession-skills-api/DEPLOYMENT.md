# 🚀 Deployment Instructions

## Profession-Skills Website Deployment Guide

This guide provides multiple deployment options for your profession-skills website that can handle large data files (10GB+).

---

## 🐳 Option 1: Docker Deployment (Recommended)

### Prerequisites
- Docker installed on your server
- Docker Compose (usually included with Docker)

### Quick Start
```bash
# Clone or upload your project to the server
cd profession-skills-api

# Build and start the application
docker-compose up -d

# Check if it's running
docker-compose ps
```

### Access the Application
- **Main Website**: `http://your-server:5000`
- **Upload Interface**: `http://your-server:5000/admin/upload`
- **Large File Info**: `http://your-server:5000/admin/info`
- **API Stats**: `http://your-server:5000/api/stats`

### Managing the Application
```bash
# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart after changes
docker-compose down && docker-compose up -d

# Update the application
docker-compose build --no-cache
docker-compose up -d
```

---

## 🖥️ Option 2: Direct Server Deployment

### Prerequisites
- Python 3.11+
- pip
- Virtual environment support

### Installation Steps
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=src/main.py
export FLASK_ENV=production
export PYTHONPATH=$(pwd)

# Run the application
python -m flask run --host=0.0.0.0 --port=5000
```

### Production Server (with Gunicorn)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 300 src.main:app
```

---

## 📊 Large File Processing (10GB+)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Sufficient space for your data file + processed data
- **CPU**: Multi-core recommended for faster processing

### Processing Time Estimates
| File Size | Processing Time | RAM Usage |
|-----------|----------------|-----------|
| 1GB       | 2-5 minutes    | ~1GB      |
| 5GB       | 10-20 minutes  | ~2GB      |
| 10GB      | 20-40 minutes  | ~3-4GB    |

### Optimizations Included
- ✅ **Streaming Processing**: Files read in chunks, not loaded entirely in memory
- ✅ **Sparse Matrix Storage**: Efficient storage for profession-skills relationships
- ✅ **Memory Management**: Periodic garbage collection during processing
- ✅ **Progress Monitoring**: Real-time logging of processing status

---

## 🔄 Updating Data

### Method 1: Web Interface (Easiest)
1. Go to `http://your-server:5000/admin/upload`
2. Select your new data file (.txt format)
3. Click "Upload and Process"
4. Wait for processing to complete

### Method 2: Direct File Replacement
```bash
# Copy your new data file to the server
# Then run the processing script
python src/optimized_data_processor.py

# Restart the application
docker-compose restart  # For Docker
# OR
# Restart your Flask/Gunicorn process
```

### Data File Format
```
profession|hard_skills|soft_skills
Software Developer|Python;JavaScript;React|Communication;Problem Solving
Data Scientist|Python;R;Machine Learning|Analytical Thinking;Creativity
Project Manager|Agile;Scrum;Jira|Leadership;Planning
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Memory Issues During Processing
```bash
# Increase swap space (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 2. Port Already in Use
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>
```

#### 3. Permission Issues
```bash
# Fix file permissions
chmod +x src/main.py
chown -R $USER:$USER .
```

#### 4. Docker Issues
```bash
# Clean up Docker
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

---

## 📈 Monitoring

### Health Checks
- **Application Health**: `http://your-server:5000/api/stats`
- **Docker Health**: `docker-compose ps`

### Log Monitoring
```bash
# Docker logs
docker-compose logs -f

# Application logs (if running directly)
tail -f app.log
```

---

## 🔒 Security Considerations

### Production Deployment
1. **Use HTTPS**: Set up SSL/TLS certificates
2. **Firewall**: Only expose necessary ports
3. **Authentication**: Consider adding authentication for admin routes
4. **File Upload Limits**: Configure appropriate file size limits
5. **Rate Limiting**: Implement rate limiting for API endpoints

### Environment Variables
```bash
# Set in production
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

---

## 📞 Support

### File Format Issues
- Ensure your data file uses the exact format: `profession|hard_skills|soft_skills`
- Skills should be separated by semicolons (`;`)
- Use UTF-8 encoding for international characters

### Performance Issues
- Monitor RAM usage during large file processing
- Consider processing files during off-peak hours
- Use SSD storage for better I/O performance

### Need Help?
- Check the logs for detailed error messages
- Verify your data file format
- Ensure sufficient system resources

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start application | `docker-compose up -d` |
| Stop application | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Upload new data | Visit `/admin/upload` |
| Check status | Visit `/api/stats` |
| Restart | `docker-compose restart` |

---

**Your profession-skills website is now ready for production use with support for large data files!** 🎉

