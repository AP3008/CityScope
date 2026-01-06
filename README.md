# CityScope 🏛️

**AI-powered civic transparency for London, Ontario**

CityScope automatically scrapes, processes, and summarizes City of London council meeting minutes, making local government more accessible to residents. Transform 50-page bureaucratic PDFs into concise, plain-English summaries in seconds.

[![Monthly Scraper](https://github.com/yourusername/cityscope/actions/workflows/monthly-scrape.yml/badge.svg)](https://github.com/yourusername/cityscope/actions/workflows/monthly-scrape.yml)

## 🎯 What It Does

- **Automated Scraping**: Crawls the London eSCRIBE portal for new council meeting PDFs
- **Smart Extraction**: Uses AI to extract meeting titles and dates directly from document content
- **Intelligent Summarization**: Gemini 2.5 Pro generates concise summaries focused on resident-impacting decisions
- **Duplicate Detection**: Automatically skips documents already in the database
- **Batch Processing**: Processes documents in configurable batches to avoid rate limits
- **Monthly Automation**: GitHub Actions runs monthly to keep database updated
- **Modern Web Interface**: Beautiful, responsive React frontend with smooth animations
- **Real-time Updates**: Flask REST API serves summaries to the frontend
- **Persistent Storage**: Supabase PostgreSQL database stores all processed summaries

## 🚀 Features

- ✨ Apple-inspired hero page with liquid gradient animations
- 📋 List view of all meeting summaries with dates
- 🔍 Detailed modal view with bullet-pointed key decisions
- 📱 Fully responsive design
- ⚡ Fast API with CORS support
- 🤖 AI-powered metadata extraction (no manual tagging needed)
- 🔄 Automatic duplicate detection and batch processing
- 📅 Monthly automated updates via GitHub Actions
- 💰 Optimized for Supabase free tier

## 📁 Project Structure

```
CityScope/
├── .github/
│   └── workflows/
│       └── monthly-scrape.yml       # GitHub Actions automation
│
├── client/                          # React Frontend
│   ├── src/
│   │   ├── App.js                  # Main React component
│   │   ├── App.css                 # Styles
│   │   └── index.js                # Entry point
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js          # Tailwind CSS config
│   └── postcss.config.js
│
└── flask-backend/                   # Python Backend
    ├── server.py                    # Flask REST API
    ├── database.py                  # Supabase database operations
    ├── .env                         # Environment variables (NOT in git)
    ├── requirements.txt             # Python dependencies
    │
    └── scraper/                     # PDF Processing Pipeline
        ├── orchestrator.py          # Main pipeline coordinator
        ├── summarizer.py            # AI summarization with Gemini
        ├── fetchers/
        │   └── fetch.py             # Web scraping with Selenium
        └── parsers/
            └── parser.py            # PDF text extraction
```

## 🛠️ Tech Stack

### Backend
- **Python 3.10+** - Core language
- **Flask** - REST API framework
- **Selenium + BeautifulSoup** - Web scraping
- **PyMuPDF (fitz)** - PDF parsing
- **Google Gemini 2.5 Flash** - AI summarization
- **Supabase** - PostgreSQL database

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### DevOps
- **GitHub Actions** - Automated monthly scraping
- **Ubuntu** - CI/CD runner environment

## 📦 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Supabase account ([Sign up here](https://supabase.com))
- GitHub account (for automation)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cityscope.git
cd cityscope
```

### 2. Backend Setup

```bash
cd flask-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
touch .env
```

Add the following to `flask-backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Database Setup

Go to your Supabase project SQL Editor and run:

```sql
-- Create the summaries table
CREATE TABLE public.meeting_summaries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id TEXT UNIQUE NOT NULL,
    meeting_date DATE NOT NULL,
    meeting_title TEXT NOT NULL,
    summary TEXT NOT NULL,
    original_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_meeting_date ON public.meeting_summaries(meeting_date DESC);
CREATE INDEX idx_document_id ON public.meeting_summaries(document_id);
CREATE INDEX idx_created_at ON public.meeting_summaries(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.meeting_summaries ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access for all users" 
ON public.meeting_summaries FOR SELECT USING (true);

CREATE POLICY "Enable insert for all users" 
ON public.meeting_summaries FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for all users"
ON public.meeting_summaries FOR UPDATE USING (true);
```

### 4. Initial Data Population

⚠️ **Important**: Start small to avoid rate limits!

```bash
cd flask-backend/scraper

# Process 5 documents (recommended for initial setup)
python orchestrator.py --max 5
```

**Expected output:**
- Scrapes document IDs
- Checks database for duplicates
- Processes 5 new PDFs
- Extracts metadata with AI
- Generates summaries
- Saves to Supabase

**Timing**: ~2-3 minutes per document (includes API rate limiting)

### 5. Frontend Setup

```bash
cd ../../client

# Install dependencies
npm install

# Start development server
npm start
```

Frontend opens at `http://localhost:3000`

### 6. Run the Backend API

In a separate terminal:

```bash
cd flask-backend
source venv/bin/activate  # Activate virtual environment
python server.py
```

API runs at `http://127.0.0.1:5000`

## 🤖 Running the Scraper

### Manual Runs

```bash
cd flask-backend/scraper

# Quick test with 3 documents
python orchestrator.py --test

# Process 5 new documents (skips duplicates automatically)
python orchestrator.py --max 5

# Process 10 new documents
python orchestrator.py --max 10

# Disable duplicate checking (not recommended)
python orchestrator.py --max 5 --no-check
```

### Process Flow

1. **Scrape**: Fetches document IDs from London eSCRIBE
2. **Check**: Queries Supabase for existing documents
3. **Filter**: Removes duplicates from batch
4. **Parse**: Downloads and extracts text from PDFs
5. **Analyze**: Uses Gemini to extract title, date, and summary
6. **Validate**: Skips documents without valid title/date
7. **Save**: Stores summaries in Supabase

### Rate Limiting

- **Gemini API**: 2 second delay between requests (built-in)
- **Recommended batch size**: 5-10 documents per run
- **Monthly automation**: Processes 10 documents/month

## 📅 Setting Up Monthly Automation

### 1. Create GitHub Secrets

Go to your repository: **Settings → Secrets and variables → Actions → New repository secret**

Add these three secrets:
- `GEMINI_API_KEY`: Your Gemini API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key

### 2. Enable GitHub Actions

The workflow file (`.github/workflows/monthly-scrape.yml`) is already included. It will:
- Run automatically on the 1st of each month at 2 AM UTC
- Process up to 10 new documents
- Skip duplicates automatically
- Log results in the Actions tab

### 3. Manual Trigger

You can also trigger manually:
1. Go to **Actions** tab in your repository
2. Click **Monthly Council Meeting Scraper**
3. Click **Run workflow**
4. Set max documents (default: 10)
5. Click **Run workflow**

### 4. Monitor Runs

- View logs in the **Actions** tab
- Check Supabase dashboard for new entries
- Summaries appear on your frontend automatically

## 💰 Staying Within Free Tiers

### Supabase Free Tier
- **Database**: 500 MB (plenty for thousands of summaries)
- **API requests**: Unlimited
- **Bandwidth**: 5 GB/month
- **Current usage**: Each summary ≈ 1-2 KB → 500 MB = ~250,000 summaries

### Gemini API Free Tier
- **Requests**: 15 requests/minute
- **Monthly**: No hard limit on free tier
- **Current usage**: 10 documents/month with 2-second delays = well within limits

### GitHub Actions Free Tier
- **Minutes**: 2,000 minutes/month
- **Current usage**: ~5-10 minutes/month
- **Storage**: 500 MB (not used)

**You're safe!** 🎉 Current usage is ~1% of all free tier limits.

## 🎨 Key Features Explained

### AI-Powered Metadata Extraction
Unlike traditional scrapers, CityScope uses Gemini to extract meeting titles and dates directly from PDF content, ensuring accuracy even when webpage structure changes.

### Smart Duplicate Detection
Before processing any document, the system checks if it already exists in the database by `document_id`. This prevents:
- Duplicate API calls
- Wasted processing time
- Database conflicts

### Batch Processing
Process documents in small batches (default: 5) to:
- Respect API rate limits
- Avoid timeouts
- Provide progress feedback
- Resume easily if interrupted

### Summary Format
```
[First sentence describing the meeting topic]

• [Key decision 1]
• [Key decision 2]
• [Key decision 3]
```

Focus: Taxes, construction, bylaws, services  
Excluded: Procedural items, attendance, administrative matters

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/summaries` | GET | Get all summaries (with `?limit=N`) |
| `/summaries/<id>` | GET | Get specific summary |
| `/summaries/recent` | GET | Get recent summaries (with `?days=N`) |

### Example Requests

```bash
# Get all summaries
curl http://127.0.0.1:5000/summaries

# Get 10 most recent
curl http://127.0.0.1:5000/summaries?limit=10

# Get summaries from last 60 days
curl http://127.0.0.1:5000/summaries/recent?days=60

# Get specific summary
curl http://127.0.0.1:5000/summaries/12345
```

## 🔧 Configuration

### Adjusting Batch Size

Edit `orchestrator.py`:
```python
# Default: process 5 new documents
python orchestrator.py --max 5

# Process more (careful with rate limits!)
python orchestrator.py --max 20
```

### Changing Summary Style

Edit `flask-backend/scraper/summarizer.py`:
- Modify the prompt to change summary format
- Adjust bullet point count
- Change focus areas

### Changing AI Model

In `summarizer.py`, update:
```python
model='gemini-2.5-flash'  # Faster, less accurate
```

### Adjusting Scraping Schedule

Edit `.github/workflows/monthly-scrape.yml`:
```yaml
schedule:
  - cron: '0 2 1 * *'  # Monthly on 1st at 2 AM
  # or
  - cron: '0 2 * * 1'  # Weekly on Mondays at 2 AM
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'selenium'"
```bash
cd flask-backend
source venv/bin/activate
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"
Check that `.env` file exists in `flask-backend/` with correct keys.

### "Database connection failed"
Verify Supabase credentials in `.env` and check that table exists.

### GitHub Actions failing
1. Check that all three secrets are set correctly
2. View logs in Actions tab for specific error
3. Ensure repository has Actions enabled

### Rate limit exceeded
- Reduce `--max` parameter
- Wait 1 hour before retrying
- Check Gemini API quota

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- City of London for providing public meeting minutes
- Google Gemini for AI capabilities
- Supabase for database infrastructure
- The open-source community

---

Made with ❤️ for civic transparency in London, Ontario