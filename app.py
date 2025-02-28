from flask import Flask, render_template, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

app = Flask(__name__)

# Function to fetch and process a webpage
def fetch_page(url):
    try:
        # Send GET request to the external website
        headers = {
            'Referer': 'https://asd.rest/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove specific scripts
        script_urls_to_block = [
            "https://www.googletagmanager.com/gtag/js?id=G-D8NNSFR7SN",
            "//affordedseasick.com/6f/4f/5c/6f4f5c3f5bfa5f5651799c658cb3556b.js",
            "//affordedseasick.com/67/10/54/6710543788e9f02584f3584d5416d1e3.js"
        ]
        for script_url in script_urls_to_block:
            for script in soup.find_all('script', src=script_url):
                script.decompose()

        # Modify all 'a' tags with target="_blank" to remove this attribute
        for link in soup.find_all('a', target='_blank'):
            link['target'] = '_self'

        # Replace the specific link for anchors and forms
        for tag in soup.find_all('a', href=True):
            original_href = tag['href']
            if original_href == 'https://asd.rest/find':
                tag['href'] = '/search'
            elif original_href.startswith('http'):
                tag['href'] = f'/browse?url={original_href}'
            else:
                if original_href.startswith('/find/?find='):
                    search_query = original_href.split('find=')[-1]
                    tag['href'] = f'/search?find={search_query}'
                elif original_href.startswith('/find/'):
                    tag['href'] = original_href.replace('/find/', '/search?find=')
                else:
                    tag['href'] = f'/browse?url={url}/{original_href}'

        for form in soup.find_all('form', action=True):
            if form['action'] == 'https://asd.rest/find':
                form['action'] = '/search'

        for div in soup.find_all('div', class_='SearchBtn'):
            icon = div.find('i', class_='fal fa-search')
            if icon:
                new_link = soup.new_tag('a', href='/find', style='display: block;')
                new_link.append(icon.extract())
                div.clear()
                div.append(new_link)

        page_url = unquote(url)
        path = page_url.split('://')[-1]
        path = path.split('/', 1)[-1]

        for watch_btn in soup.find_all('a', class_='watchBTn'):
            new_link = f'/server/asd.rest/{path}'
            watch_btn['href'] = new_link

        for btn in soup.find_all('a', class_='downloadBTn'):
            new_link = f'/server/asd.rest/{path}'
            btn['href'] = new_link

        for tag in soup.find_all('a', href=True):
            if tag['href'].startswith('http://127.0.0.1:5000/browse?url=https://'):
                tag['href'] = tag['href'].replace('http://127.0.0.1:5000/browse?url=https://', '/server/')

        return str(soup)
    except Exception as e:
        return f'<h1>Error</h1><p>{str(e)}</p>'

# Route to search using the search form
@app.route('/search')
def search():
    search_query = request.args.get('find')
    offset = request.args.get('offset')

    if search_query:
        search_url = f'https://asd.rest/find/?find={search_query}'
        if offset:
            search_url += f'&offset={offset}'
        content = fetch_page(search_url)
        return render_template_string(content)

    return '<h1>No search query provided</h1>'

# Route to browse a website
@app.route('/browse')
def browse():
    url = request.args.get('url')
    
    if not url:
        url = 'https://arabseed.show/'
    else:
        url = unquote(url)

    content = fetch_page(url)
    return render_template_string(content)

# Route to render the index.html file
@app.route('/find')
def html_page():
    return render_template('search.html')

# Home route
@app.route('/')
def home():
    return '''

        <form action="/browse">
            <input type="text" name="url" placeholder="Enter URL">
            <button type="submit">Go</button>
        </form>
    '''

# New route to scrape a specific page and fetch quality-based video links
@app.route('/server/<path:target_url>', methods=['GET'])
def scrape(target_url):
    headers = {
        'Referer': 'https://asd.rest/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    quality_map = {
        720: None,
        480: None,
        1080: None
    }

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    try:
        response = requests.get(target_url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            watch_button = soup.find('a', class_='watchBTn')

            if watch_button and 'href' in watch_button.attrs:
                watch_link = watch_button['href']
                if not watch_link.startswith(('http://', 'https://')):
                    watch_link = 'https://' + watch_link

                watch_response = requests.get(watch_link, headers=headers)

                if watch_response.status_code == 200:
                    watch_soup = BeautifulSoup(watch_response.text, 'html.parser')
                    links = watch_soup.find_all('li', attrs={'data-link': True})

                    domain = "https://w.gamehub.cam"

                    for link in links:
                        video_link = link['data-link']

                        if video_link.startswith(domain):
                            video_link = video_link.replace('https://', '')

                            if quality_map[720] is None:
                                quality_map[720] = video_link
                            elif quality_map[480] is None:
                                quality_map[480] = video_link
                            elif quality_map[1080] is None:
                                quality_map[1080] = video_link
                            else:
                                break

                    return render_template('template.html', links=quality_map)
                else:
                    return "Failed to retrieve the watch page.", 500
            else:
                return "Watch button not found.", 404
        else:
            return "Failed to retrieve the target page.", 500
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
