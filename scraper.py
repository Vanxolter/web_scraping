import requests
from datetime import datetime
import traceback
from bs4 import BeautifulSoup
import os
import re


headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}


def errors_log(info, *args, **kwargs):
    """
    Кэширование ошибок в файлы
    :param info: Информация по ошибке
    :return: none
    """

    date_time = datetime.today()
    only_date = datetime.time(date_time)
    with open(f"errors/error_{only_date.hour}_{only_date.minute}.txt", "w") as file:
        file.write(info)


def get_html(url, path, num):
    pages_paths = []
    if num:
        for numer in range(1, num):
            current_url = f"{url}{numer}"
            path_to_file = f"{path}{numer}.html"
            req = requests.get(current_url, headers=headers)
            src = req.text
            pages_paths.append(path_to_file)

            with open(path_to_file, "w") as file:
                file.write(src)
        return pages_paths
    else:
        req = requests.get(url, headers=headers)
        src = req.text
        with open(path, "w") as file:
            file.write(src)


def get_pages_with_cards(url, *args, **kwargs):
    try:
        current_url = url + f"?currentpage="
        path = f"data/data_pages/mainpage_"
        pages_paths = get_html(current_url, path, 5)
        return get_page_of_car(pages_paths, url)

    except Exception as _ex:
        return errors_log(traceback.format_exc())

    finally:
        return "function get_pages_with_cards has done successfully"


def get_page_of_car(pages_paths, url):
    try:
        new_url = url.split("/transporter")[0]
        for path in enumerate(pages_paths):
            id = path[0] + 1
            print(path[1])
            with open(path[1], "r") as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")
            link = soup.find(class_="ls-titles").find("a").get("href")

            url = f"{new_url}{link}"
            path = f"data/data_pages/car_{id}.html"
            print(url)
            get_html(url, path, False)
            get_data(path, id)

    except Exception as _ex:
        errors_log(traceback.format_exc())

    finally:
        "function get_page_of_car has done successfully"


def get_data(page_path, id):
    with open(page_path, "r") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    title = soup.find(class_="sc-ellipsis sc-font-xl").text
    print(title)
    price = soup.find(class_="sc-highlighter-4 sc-highlighter-xl sc-font-bold").text
    print(price)
    mileage = soup.find(class_="data-basic1").find("div", text=re.compile("km")).text
    print(mileage)
    try:
        color = soup.find(class_="columns").find("div", text=re.compile("Farbe")).next_sibling.next_sibling.text
        print(color)
    except AttributeError:
        color = " "
        print(color)
    power = soup.find(class_="columns").find("div", text=re.compile("Leistung")).next_sibling.next_sibling.text
    print(power)
    description = soup.find(class_="short-description").text
    print(description)

    if not os.path.isdir(f"data/{id}"):
        os.mkdir(f"data/{id}")

    image = soup.find(class_="gallery-picture").find("img").get("data-src")
    print(image)

    """r = requests.get(image)
    soup = BeautifulSoup(r.content)
    for link in soup.select("img[src^=http]"):
        lnk = link["src"]
        with (f"data/{id}/{id}.img", " wb") as file:
            file.write(requests.get(lnk).content)"""

def main():
    url = "https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault"
    get_pages_with_cards(url)


if __name__ == "__main__":
    main()
