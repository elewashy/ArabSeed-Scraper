from flask import Flask, redirect, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/<path:url>/<filename>')
def download(url, filename):
    # بناء الرابط الكامل
    page_url = f"https://{url}"

    # إرسال طلب GET لجلب محتوى الصفحة
    response = requests.get(page_url)
    response.raise_for_status()  # التأكد من نجاح الطلب

    # تحليل محتوى الصفحة باستخدام BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # البحث عن رابط التحميل المباشر في العناصر <a> التي تحتوي على خاصية download
    download_link = soup.find('a', class_='link btn btn-light', download=True)
    if download_link:
        download_link = download_link['href']
    else:
        # البحث عن رابط التحميل في العناصر <a> أخرى
        download_link = soup.find('a', class_='FlatButton FlatButton--primary FlatButton--size-l')
        if download_link:
            download_link = download_link['href']
        else:
            # البحث عن رابط الفيديو في العناصر <source>
            download_link = soup.find('source', type='video/mp4')
            if download_link:
                download_link = download_link['src']
            else:
                # إذا لم يتم العثور على أي رابط تحميل أو فيديو، ارجع برسالة خطأ
                return "No download link or video source found", 404

    if "video.mp4" in download_link:
        download_link = download_link.replace("video.mp4", filename)
    #elif "Cima-Now_CoM" in download_link:
        #download_link = download_link.replace("Cima-Now_CoM", filename)


    # إعادة توجيه المستخدم إلى رابط التحميل المباشر مع الاسم الجديد
    return redirect(download_link)

if __name__ == '__main__':
    app.run(debug=True)
