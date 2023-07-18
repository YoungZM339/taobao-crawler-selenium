:start
call .\venv\Scripts\activate
pyinstaller.exe -F -w .\jdCrawler.py
pyinstaller.exe -F -w .\taobaoCrawler.py
pyinstaller.exe -F -w .\taobaoCrawlerBySaleDesc.py
pause