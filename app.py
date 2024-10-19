from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

app = Flask(__name__)

# Function to fetch and process a webpage
def fetch_page(url):
    try:
        # Send GET request to the external website
        response = requests.get(url)
        response.raise_for_status()

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove ad-related elements based on classes and ids
        ad_classes = [
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__wrap', 
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__content',
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__closelink',
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__bubble',
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__title',
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__descr',
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__message',
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__message-after',
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__girl-icon',
            'pl-6f4f5c3f5bfa5f5651799c658cb3556b__pic'
        ]

        # Remove elements with specific classes
        for class_name in ad_classes:
            for element in soup.find_all(class_=class_name):
                element.decompose()

        # Remove the specific iframe element by id
        iframe_element = soup.find('iframe', id='container-6f4f5c3f5bfa5f5651799c658cb3556b46751')
        if iframe_element:
            iframe_element.decompose()

        # Remove the specific body element with class 'vsc-initialized'
        body_class_element = soup.find('body', class_='vsc-initialized')
        if body_class_element:
            body_class_element.decompose()

        # Remove specific scripts
        script_urls_to_block = [
            "https://www.googletagmanager.com/gtag/js?id=G-D8NNSFR7SN",
            "//affordedseasick.com/6f/4f/5c/6f4f5c3f5bfa5f5651799c658cb3556b.js",
            "//affordedseasick.com/67/10/54/6710543788e9f02584f3584d5416d1e3.js"
        ]
        
        # Remove scripts with specified URLs
        for script_url in script_urls_to_block:
            for script in soup.find_all('script', src=script_url):
                script.decompose()

        # Modify all 'a' tags with target="_blank" to remove this attribute
        for link in soup.find_all('a', target='_blank'):
            link['target'] = '_self'  # Open in the same window instead of a new one

        # Modify the URLs in the page to work within the Flask app
        for tag in soup.find_all('a', href=True):
            if tag['href'].startswith('http'):
                tag['href'] = f'/browse?url={tag["href"]}'  # Use the raw href
            else:
                tag['href'] = f'/browse?url={url}/{tag["href"]}'  # Use the raw href

        # Get the part of the URL after the domain
        page_url = unquote(url)  # This is the full URL
        path = page_url.split('://')[-1]  # Remove the protocol
        path = path.split('/', 1)[-1]  # Get everything after the domain

        # Replace the link inside watchBTn with the complete URL after the domain
        for watch_btn in soup.find_all('a', class_='watchBTn'):
            new_link = f'https://arabseed-server.vercel.app/asd.quest/{path}'  # Format of the new link
            watch_btn['href'] = new_link  # Replace the old link with the new one
        for btn in soup.find_all('a', class_='downloadBTn'):
            new_link = f'https://arabseed-server.vercel.app/asd.quest/{path}'  # Format of the new link
            btn['href'] = new_link  # Replace the old link with the new one

        # Replace all links that point to the local server with the new base URL
        for tag in soup.find_all('a', href=True):
            if tag['href'].startswith('http://127.0.0.1:5000/browse?url=https://'):
                tag['href'] = tag['href'].replace('http://127.0.0.1:5000/browse?url=https://', 'https://arabseed-server.vercel.app/')

        return str(soup)
    except Exception as e:
        return f'<h1>Error</h1><p>{str(e)}</p>'

# Route to browse a website
@app.route('/browse')
def browse():
    # Get the URL from the query parameters and decode it
    url = request.args.get('url')
    
    # Default URL if none is provided
    if not url:
        url = 'https://arabseed.show/'  # Set your default website here
    else:
        # Decode the URL to handle encoded characters
        url = unquote(url)  # Decode only once
    
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
