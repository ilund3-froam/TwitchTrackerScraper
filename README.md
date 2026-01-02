# TwitchTracker Scraper

A web-based Python scraper with a user-friendly UI that extracts Twitch usernames from TwitchTracker.com's most-followers page and saves them to a CSV file.

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web UI (Recommended)

Run the Flask web application:
```bash
python app.py
```

Then open your browser and navigate to:
```
http://localhost:3000
```

In the web interface:
1. Enter the range of streamers you want (e.g., 1 to 150)
2. Click "Scrape Usernames" to fetch the data
3. Click "Download CSV" to save the results

**Note:** Each page contains 50 streamers. For example:
- Streamers 1-50 = Page 1
- Streamers 51-100 = Page 2
- Streamers 101-150 = Page 3

### Command Line (Legacy)

You can also use the original command-line scraper:
```bash
python scraper.py
```

This will create a `twitch_usernames.csv` file with all scraped usernames.

To specify a custom output file:
```bash
python scraper.py output.csv
```

## Output Format

The CSV file contains a single column:
- `twitch_username`: The Twitch username (e.g., "KaiCenat")
