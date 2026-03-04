# Ozone Analysis Dashboard

A modern Flask-based web application for analyzing ozone data with interactive visualizations and ML insights.

## Features
- 📊 Seasonal, Year-wise, and Month-wise analysis
- 🤖 ML-powered insights (trend analysis, correlation, statistics)
- 📈 Interactive Plotly charts with dark theme
- 🎨 Modern glassmorphism UI design

## Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd "Data analysis"
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Add data files**
Place your Excel files in the project root:
- `Year_vs_Month_Monthly_Average_Ozone_Pivot_Rounded.xlsx`
- `Delhi_TOC.xlsx`

5. **Run locally**
```bash
python app.py
```
Visit `http://localhost:5001`

## Deployment Options

### Option 1: Heroku (Recommended)

1. **Install Heroku CLI** from https://devcenter.heroku.com/articles/heroku-cli

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku app**
```bash
heroku create your-app-name
```

4. **Add data files to Heroku**
```bash
git add .
git commit -m "Add data files"
git push heroku main
```

5. **View logs**
```bash
heroku logs --tail
```

### Option 2: AWS (EC2)

1. **Launch EC2 instance** (Ubuntu 22.04)

2. **SSH into instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Install dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

4. **Clone and setup**
```bash
git clone <your-repo-url>
cd "Data analysis"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

5. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

6. **Setup Nginx reverse proxy** (optional for production)

### Option 3: Railway.app

1. **Connect GitHub repo** to Railway
2. **Set environment variables** if needed
3. **Deploy** - automatic on push

### Option 4: PythonAnywhere

1. Go to https://www.pythonanywhere.com
2. Upload files via web interface
3. Configure WSGI file
4. Enable web app

## Environment Variables

Create `.env` file for sensitive data:
```
FLASK_ENV=production
DEBUG=False
```

## GitHub Push

```bash
git init
git add .
git commit -m "Initial commit: Ozone analysis dashboard"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

## Project Structure
```
Data analysis/
├── app.py                    # Main Flask app
├── requirements.txt          # Dependencies
├── Procfile                  # Heroku config
├── templates/
│   └── index.html           # HTML template
├── static/                  # CSS/JS (if any)
└── *.xlsx                   # Data files
```

## Notes
- Data files are large; consider using cloud storage (S3) for production
- Update `app.py` to load data from cloud if deploying to serverless
- Ensure Excel files are in the same directory as `app.py`

## License
MIT
