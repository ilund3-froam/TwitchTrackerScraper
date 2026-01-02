#!/usr/bin/env python3
"""
Scraper for TwitchTracker.com to extract Twitch usernames from the most-followers page.
Outputs usernames to a CSV file.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import sys


def scrape_usernames(base_url, output_file='twitch_usernames.csv'):
    """
    Scrape Twitch usernames from TwitchTracker.com and save to CSV.
    
    Args:
        base_url: The URL to scrape
        output_file: Name of the output CSV file
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    usernames = []
    page = 1
    max_pages = 100  # Safety limit
    
    print(f"Starting scrape of {base_url}...")
    
    while page <= max_pages:
        # Construct URL with page parameter
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page}"
        
        print(f"Scraping page {page}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table with id="channels"
        table = soup.find('table', {'id': 'channels'})
        
        if not table:
            print(f"No table found on page {page}. Stopping.")
            break
        
        # Find all rows in the tbody
        tbody = table.find('tbody')
        if not tbody:
            print(f"No tbody found on page {page}. Stopping.")
            break
        
        rows = tbody.find_all('tr')
        
        if not rows:
            print(f"No rows found on page {page}. Stopping.")
            break
        
        page_usernames = []
        
        # Extract usernames from each row
        for row in rows:
            # Find the <a> tag in the row (the username link)
            link = row.find('a', href=True)
            if link:
                # Get the username from the link text (e.g., "KaiCenat")
                username = link.get_text(strip=True)
                # Only add if it's a valid username (not empty, and href looks like a channel)
                href = link.get('href', '')
                if username and href.startswith('/') and username not in usernames:
                    page_usernames.append(username)
                    usernames.append(username)
        
        if not page_usernames:
            print(f"No new usernames found on page {page}. Stopping.")
            break
        
        print(f"Found {len(page_usernames)} usernames on page {page} (total: {len(usernames)})")
        
        # Check if there's a next page button
        pagination = soup.find('ul', class_='pagination')
        if pagination:
            next_button = pagination.find('a', string='Next') or pagination.find('li', class_='next')
            if not next_button or 'disabled' in next_button.get('class', []):
                break
        else:
            # If no pagination found and we got a small number of results, assume we're done
            if len(page_usernames) < 25:
                break
        
        page += 1
        time.sleep(1)  # Be respectful, wait 1 second between requests
    
    # Write to CSV
    print(f"\nTotal usernames found: {len(usernames)}")
    print(f"Writing to {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['twitch_username'])  # Header
        for username in usernames:
            writer.writerow([username])
    
    print(f"Successfully saved {len(usernames)} usernames to {output_file}")
    return usernames


if __name__ == '__main__':
    url = 'https://twitchtracker.com/channels/most-followers'
    output = 'twitch_usernames.csv'
    
    if len(sys.argv) > 1:
        output = sys.argv[1]
    
    scrape_usernames(url, output)

