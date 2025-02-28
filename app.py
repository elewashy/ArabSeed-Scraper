import requests
from flask import Flask, Response, request, jsonify, redirect
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# الهوست الثابت
HOST = "https://bigwarp.io"

@app.route('/<path:subpath>')
def fetch_and_display(subpath):
    url = f"{HOST}/{subpath}"  # دمج الهوست مع المسار اللي هيدخله المستخدم

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # تعديل الروابط داخل <link> و <script>
        for tag in soup.find_all(["link", "script"], href=True):
            if tag["href"].startswith("/"):
                tag["href"] = HOST + tag["href"]
        for tag in soup.find_all("script", src=True):
            if tag["src"].startswith("/"):
                tag["src"] = HOST + tag["src"]

        # قائمة السكربتات غير المرغوبة
        unwanted_scripts = [
            "bigwarpjs.config",
            "$.cookie('file_id'",
            "afrdtech.com",
            "bit.ly",
            "naupsithizeekee.com",
            "ptichoolsougn.net",
            "bigwarp.io/js/big.js",
            "gangwafriend.com",
            "fontcpo.com",
            "data-cfasync",
            "document.createElement('script')",
            "Object.freeze"
        ]

        # السكربت المسموح به مع تعديل الوقت من 5000 إلى 1000
        allowed_script = """$(function() {
            var delay_done = 1;
            setTimeout(function(){
                $('#blk1').hide();
            }, 1000);
            if (!$.cookie('ads')) {
                $.cookie('ads', -1, { expires: 1 });
            }
            var count = parseInt($.cookie('ads'));
            var count2= 0;
        });"""

        # حذف جميع السكربتات غير المرغوبة
        for script in soup.find_all("script"):
            script_content = script.string
            script_src = script.get("src", "")

            if script_content:
                if any(unwanted in script_content for unwanted in unwanted_scripts):
                    script.decompose()
            elif script_src:
                if any(unwanted in script_src for unwanted in unwanted_scripts):
                    script.decompose()

        # إضافة السكربت بعد تنظيف الصفحة
        new_script = soup.new_tag("script")
        new_script.string = allowed_script
        soup.body.append(new_script)

        return Response(str(soup), content_type="text/html")

    return f"Error: {response.status_code}"

def get_hash(file_path):
    url = HOST + file_path
    file_id = file_path.split('/')[-1].rsplit('_', 1)[0]  # استخراج ID بدون الجزء المتغير
    response = requests.post(url, data={"op": "download_orig", "id": file_id, "mode": "o"})
    soup = BeautifulSoup(response.text, "html.parser")
    hash_input = soup.find("input", {"name": "hash"})
    return hash_input["value"] if hash_input else None

def get_download_link(file_path, hash_value):
    url = HOST + file_path
    file_id = file_path.split('/')[-1].rsplit('_', 1)[0]
    data = {
        "op": "download_orig",
        "id": file_id,
        "mode": "o",
        "hash": hash_value
    }
    response = requests.post(url, data=data)
    soup = BeautifulSoup(response.text, "html.parser")
    download_link = soup.find("span", style="background:#f9f9f9;border:1px dotted #bbb;padding:7px;")
    if download_link:
        download_a = download_link.find("a")
        return download_a["href"] if download_a and download_a.get("href") else None
    return None

@app.route('/d/<path:file_path>', methods=['GET'])
def download(file_path):
    hash_value = None
    
    while not hash_value:
        hash_value = get_hash("/d/" + file_path)
        if not hash_value:
            time.sleep(5)
    
    download_link = None
    while not download_link:
        download_link = get_download_link("/d/" + file_path, hash_value)
        if not download_link:
            hash_value = get_hash("/d/" + file_path)
            if not hash_value:
                return jsonify({"error": "Failed to retrieve hash"}), 500
            time.sleep(5)
    
    return redirect(download_link)


if __name__ == '__main__':
    app.run(debug=True)
