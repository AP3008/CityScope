# CityScope 🏛️

**AI-powered civic transparency for London, Ontario**

CityScope automatically scrapes, processes, and summarizes City of London council meeting minutes, making local government more accessible to residents. Transform 50-page bureaucratic PDFs into concise, plain-English summaries in seconds.


## 🎯 What It Does

- **Automated Scraping**: Crawls the London eSCRIBE portal for new council meeting PDFs
- **Smart Extraction**: Uses AI to extract meeting titles and dates directly from document content
- **Intelligent Summarization**: Gemini 2.5 Pro generates concise summaries focused on resident-impacting decisions
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
- 🔄 Automatic duplicate detection

## 📁 Project Structure

```
CityScope/
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
- **Google Gemini 2.5 Pro** - AI summarization
- **Supabase** - PostgreSQL database

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Fetch API** - HTTP requests

## 📦 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Supabase account ([Sign up here](https://supabase.com))

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

-- Create indexes
CREATE INDEX idx_meeting_date ON public.meeting_summaries(meeting_date DESC);
CREATE INDEX idx_document_id ON public.meeting_summaries(document_id);

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

### 4. Frontend Setup

```bash
cd ../client

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will open at `http://localhost:3000`

### 5. Run the Backend

In a separate terminal:

```bash
cd flask-backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start Flask API
python server.py
```

The API will run at `http://127.0.0.1:5000`

## 🤖 Running the Scraper

Process council meeting PDFs and generate summaries:

```bash
cd flask-backend/scraper

# Test with 3 documents
python orchestrator.py --test

# Process specific number of documents
python orchestrator.py --max 10

# Process all available documents
python orchestrator.py
```

The scraper will:
1. Scrape document IDs from London eSCRIBE portal
2. Download and parse PDFs
3. Extract meeting titles and dates using AI
4. Generate concise summaries
5. Save everything to Supabase

## 🎨 Key Features Explained

### AI-Powered Metadata Extraction
Unlike traditional scrapers, CityScope uses Gemini to extract meeting titles and dates directly from PDF content, ensuring accuracy even when webpage structure changes.

### Smart Summarization
Summaries follow this format:
- **First sentence**: Topic overview
- **Bullet points**: Key decisions impacting residents (taxes, construction, bylaws, services)
- **Exclusions**: Procedural items, attendance, administrative matters

### Responsive Design
- Dark hero animation on load
- Smooth transitions between pages
- Mobile-friendly list and modal views
- Accessible color contrast

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/summaries` | GET | Get all summaries (with `?limit=N`) |
| `/summaries/<id>` | GET | Get specific summary |
| `/summaries/recent` | GET | Get recent summaries (with `?days=N`) |

## 🔧 Configuration

### Adjusting Summary Length
Edit `flask-backend/scraper/summarizer.py`:
- Modify the prompt to change summary style
- Adjust bullet point count
- Change focus areas

### Changing Models
In `summarizer.py`, update:
```python
model='gemini-2.5-pro'  # or 'gemini-2.0-flash-exp'
```

### Scraping Frequency
For automated updates, set up a cron job or GitHub Action to run `orchestrator.py` periodically.

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

Made with ❤️ for civic transparency