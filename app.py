from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to fetch and process a webpage
def fetch_page(url):
    try:
        # Send GET request to the external website
        response = requests.get(url)
        response.raise_for_status()

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove specific elements (e.g., popup ads, suspicious links)
        for ad in soup.find_all('div', class_='pl-6f4f5c3f5bfa5f5651799c658cb3556b__btn-bloc'):
            ad.decompose()  # Remove the element from the DOM

        # Keep iframe elements as they are (do not remove them)

        # Remove suspicious links, for example with specific IDs or suspicious href values
        for link in soup.find_all('a', href=True):
            # Remove links with specific id or suspicious href patterns
            if link.get('id') == 'lkld' or 'thugjudgementpreparations.com' in link['href']:
                link.decompose()  # Remove the suspicious link

        # Modify all 'a' tags with target="_blank" to remove this attribute
        for link in soup.find_all('a', target='_blank'):
            link['target'] = '_self'  # Open in the same window instead of a new one

        # Modify the URLs in the page to work within the Flask app
        for tag in soup.find_all('a', href=True):
            if tag['href'].startswith('http'):
                # For absolute URLs, keep them unchanged
                tag['href'] = f'/browse?url={tag["href"]}'
            else:
                # For relative URLs, make them relative to the base URL
                tag['href'] = f'/browse?url={url}/{tag["href"]}'
        
        return str(soup)
    except Exception as e:
        return f'<h1>Error</h1><p>{str(e)}</p>'

# Route to browse a website
@app.route('/browse')
def browse():
    # Get the URL from the query parameters
    url = request.args.get('url')
    
    # Default URL if none is provided
    if not url:
        url = 'https://arabseed.show/'  # Set your default website here
    
    # Fetch and display the content
    content = fetch_page(url)
    return render_template_string(content)

# Home route
@app.route('/')
def home():
    return '''
        <h1>Flask Browser</h1>
        <p>Enter a URL to start browsing.</p>
        <form action="/browse">
            <input type="text" name="url" placeholder="Enter URL">
            <button type="submit">Go</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
