#!/usr/bin/env python3
"""
Flask web application for scraping TwitchTracker.com usernames with a web UI.
"""

from flask import Flask, render_template, request, send_file, jsonify
from bs4 import BeautifulSoup
import requests
import csv
import io
import time
from math import ceil

app = Flask(__name__)


def calculate_pages_needed(start, end):
    """
    Calculate which pages are needed to get streamers from start to end range.
    Each page has 50 streamers.
    
    Args:
        start: Starting position (1-indexed)
        end: Ending position (1-indexed)
    
    Returns:
        List of page numbers needed
    """
    start_page = ceil(start / 50)
    end_page = ceil(end / 50)
    return list(range(start_page, end_page + 1))


def scrape_usernames_range(start, end, language=None):
    """
    Scrape Twitch usernames from TwitchTracker.com for a specific range.
    
    Args:
        start: Starting position (1-indexed, e.g., 1)
        end: Ending position (1-indexed, e.g., 150)
        language: Optional language filter (e.g., 'english', 'spanish', etc.)
    
    Returns:
        List of usernames in the specified range
    """
    base_url = 'https://twitchtracker.com/channels/most-followers'
    if language:
        base_url = f'{base_url}/{language}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    pages_needed = calculate_pages_needed(start, end)
    all_usernames = []
    
    print(f"Scraping pages {pages_needed} for range {start}-{end} (language: {language or 'all'})...")
    
    for page_num in pages_needed:
        # Construct URL
        if page_num == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page_num}"
        
        print(f"Scraping page {page_num}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table with id="channels"
        table = soup.find('table', {'id': 'channels'})
        
        if not table:
            print(f"No table found on page {page_num}.")
            continue
        
        # Find all rows in the tbody
        tbody = table.find('tbody')
        if not tbody:
            print(f"No tbody found on page {page_num}.")
            continue
        
        rows = tbody.find_all('tr')
        
        # Extract usernames from each row
        for row in rows:
            # Find all links in the row - there are usually 2 (one with image, one with text)
            # We want the one with non-empty text (the username)
            links = row.find_all('a', href=True)
            for link in links:
                username = link.get_text(strip=True)
                href = link.get('href', '')
                # Use the first link that has text and is a channel link
                if username and href.startswith('/') and username not in all_usernames:
                    all_usernames.append(username)
                    break  # Found the username link, move to next row
        
        time.sleep(1)  # Be respectful, wait 1 second between requests
    
    # Calculate which usernames fall within the requested range
    start_idx = start - 1  # Convert to 0-indexed
    end_idx = end  # End is exclusive in slicing
    
    if start_idx < len(all_usernames):
        usernames_in_range = all_usernames[start_idx:end_idx]
    else:
        usernames_in_range = []
    
    return usernames_in_range


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    """Handle the scrape request and return usernames."""
    try:
        start = int(request.json.get('start', 1))
        end = int(request.json.get('end', 50))
        language = request.json.get('language', '').strip() or None
        
        if start < 1 or end < start:
            return jsonify({'error': 'Invalid range. Start must be >= 1 and end must be >= start.'}), 400
        
        usernames = scrape_usernames_range(start, end, language)
        
        return jsonify({
            'success': True,
            'count': len(usernames),
            'usernames': usernames
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['POST'])
def download():
    """Generate and return CSV file for download."""
    try:
        start = int(request.json.get('start', 1))
        end = int(request.json.get('end', 50))
        language = request.json.get('language', '').strip() or None
        
        if start < 1 or end < start:
            return jsonify({'error': 'Invalid range. Start must be >= 1 and end must be >= start.'}), 400
        
        usernames = scrape_usernames_range(start, end, language)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['twitch_username'])
        for username in usernames:
            writer.writerow([username])
        
        # Create BytesIO object for Flask send_file
        csv_bytes = io.BytesIO()
        csv_bytes.write(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        lang_suffix = f'_{language}' if language else ''
        filename = f'twitch_usernames_{start}_{end}{lang_suffix}.csv'
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting TwitchTracker Scraper on http://localhost:3000")
    app.run(host='0.0.0.0', port=3000, debug=True)

