from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import requests
import gspread

sa = gspread.service_account(filename='tt-parser-a52f25070a31.json')
sh = sa.open('TTpars')
wks = sh.worksheet('list1')


# ranimexchannel

username = input('username: ')
# username = 'ranimexchannel'
print('[INFO] username input')


def get_HTML():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=chrome_options)


    driver.get(f'https://www.tiktok.com/@{username}')
    print('[INFO] browser start')
    print('[INFO] sleep')
    sleep(5)
    print('[INFO] sleep stop')
    input('Press enter')

    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print('[INFO] scroll')

        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)
        print('[INFO] scroll sleep')

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        print('[INFO] calc scroll')
        if new_height == last_height:
            print('[INFO] break')
            sleep(3)
            break
        last_height = new_height

    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))



def get_data():
    Links = []
    Views = []

    with open('index.html', encoding='utf-8') as f:
        src = f.read()

    soup = BeautifulSoup(src, 'lxml')
    videos = soup.find_all('div', class_='tiktok-x6y88p-DivItemContainerV2 e19c29qe8')

    for v in videos:
        link = v.find('a', class_='tiktok-1wrhn5c-AMetaCaptionLine eih2qak0').get("href")
        Links.append(link)
        print('Links')

        view = v.find('strong', class_='video-count tiktok-dirst9-StrongVideoCount e148ts222').text
        Views.append(view)
        print('Views')

    Dates = []
    for link in Links:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')

        date = soup.find('span', class_="tiktok-1kcycbd-SpanOtherInfos evv7pft3").find_all('span')[2].text
        print(date)
        if date:
            Dates.append(date)
        else:
            Dates.append("Не удалось получить")

    print('[INFO] Доступные видео: ')
    print('link -- views -- dates')
    for i in range(len(Links)):
        print(f'{Links[i]} -- {Views[i]} -- {Dates[i]}')

    return Links, Views, Dates

def upload_to_sheets(Links, Views, Dates):
    try:
        data = prepare_data(Links, Views, Dates)
        start_row = 2
        for i, row in enumerate(data):
            wks.update(f'A{start_row + i}:C{start_row + i}', [row])
    except Exception as err:
        print(f"Неизвестная ошибка: {err}")


def prepare_data(Links, Views, Dates):
    data = []
    for i in range(len(Links)):
        row = [Links[i], Views[i], Dates[i]]
        data.append(row)

    return data


def main():
    get_HTML()
    Links, Views, Dates = get_data()
    upload_to_sheets(Links, Views, Dates)


if __name__ == '__main__':
    main()
