from flask import Flask, request, render_template_string, render_template
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

        # Replace the specific link for anchors and forms
        for tag in soup.find_all('a', href=True):
            original_href = tag['href']

            # Replace https://asd.quest/find with /search
            if original_href == 'https://asd.quest/find':
                tag['href'] = '/search'  # Replace with the search route

            # If the href is a full URL
            elif original_href.startswith('http'):
                tag['href'] = f'/browse?url={original_href}'  # Use the raw href
            else:
                # If the href contains 'find', replace it with 'search'
                if original_href.startswith('/find/?find='):
                    # Replace with /search
                    search_query = original_href.split('find=')[-1]  # Get the query after 'find='
                    tag['href'] = f'/search?find={search_query}'  # Modify to /search?find=
                elif original_href.startswith('/find/'):
                    # If the link contains 'find' but is not in the format '/find/?find=', handle it
                    tag['href'] = original_href.replace('/find/', '/search?find=')

                # For other links, append to the current URL
                else:
                    tag['href'] = f'/browse?url={url}/{original_href}'  # Use the raw href

        # Replace form actions
        for form in soup.find_all('form', action=True):
            if form['action'] == 'https://asd.quest/find':
                form['action'] = '/search'  # Replace the action with /search
        # تحويل <i> داخل <div class="SearchBtn"> إلى <a>
        for div in soup.find_all('div', class_='SearchBtn'):
            icon = div.find('i', class_='fal fa-search')  # ابحث عن الأيقونة داخل div
            if icon:
                # إنشاء عنصر <a>
                new_link = soup.new_tag('a', href='/find', style='display: block;')  # إضافة style للحفاظ على الشكل
                # إضافة الأيقونة إلى الرابط
                new_link.append(icon.extract())  # استخدام extract لإزالة الأيقونة من مكانها

                # إضافة الرابط الجديد إلى الـ <div>
                div.clear()  # مسح المحتويات الحالية
                div.append(new_link)  # إضافة الرابط الجديد إلى الـ <div>

        # Return the modified HTML
        return str(soup)
    except Exception as e:
        return f'<h1>Error</h1><p>{str(e)}</p>'

# Route to search using the search form
@app.route('/search')
def search():
    # Get the 'find' query parameter from the request
    search_query = request.args.get('find')
    offset = request.args.get('offset')  # Get the offset parameter if it exists

    # Construct the search URL
    if search_query:
        search_url = f'https://asd.quest/find/?find={search_query}'
        if offset:
            search_url += f'&offset={offset}'  # Append offset if it exists
        content = fetch_page(search_url)
        return render_template_string(content)
    
    return '<h1>No search query provided</h1>'

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

    # Fetch and display the content for other URLs
    content = fetch_page(url)
    return render_template_string(content)

# Route to render the index.html file
@app.route('/find')
def html_page():
    return render_template('search.html')  # Open index.html from the templates folder

# Home route
@app.route('/')
def home():
    return '''
        <h1>Flask Browser</h1>
        <p>Enter a URL to start browsing.</p>
        <form action="/search" id="main-p-search" method="get">
            <input name="find" placeholder="البحث السريع ..." type="text"/>
            <button type="submit"><i class="fal fa-search"></i> Search</button>
        </form>
        <form action="/browse">
            <input type="text" name="url" placeholder="Enter URL">
            <button type="submit">Go</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
