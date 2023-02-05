import requests
from datetime import datetime
import traceback
from bs4 import BeautifulSoup
import os
import re
import json

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
    if not os.path.isdir(f"errors/"):
        os.makedirs(f"errors")
    with open(f"errors/error_{only_date.hour}_{only_date.minute}.txt", "w") as file:
        file.write(info)


def get_html(url: str, path: str, num: int or False, *args, **kwargs) -> list:
    """
    Функция записи HTML кода для страниц без динамической прогрузки контента

    :param url: Ссылка на страницу для получения кода
    :param path: Путь для сохранения страницы в .html
    :param num: Количество страниц если их несколько или False если страница одна
    :param args:
    :param kwargs:
    :return: Список из путей к файлам с html-кодом
    """
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


def get_pages_with_cards(url: str, *args, **kwargs):
    """
    Функция для создает папку data и задает путь для сохранения .html файлов

    :param url: Ссылка на страницу для получения кода
    :param args:
    :param kwargs:
    :return: Вызывает функцию для получения страниц отдельных объявлений
    """
    try:
        if not os.path.isdir(f"data/"):
            os.makedirs(f"data/data_pages")

        current_url = url + f"?currentpage="
        path = f"data/data_pages/mainpage_"
        pages_paths = get_html(current_url, path, 5)
        return get_page_of_car(pages_paths, url)

    except Exception as _ex:
        return errors_log(traceback.format_exc())

    finally:
        return "function get_pages_with_cards has done successfully"


def get_page_of_car(pages_paths: list, url: str, *args, **kwargs):
    """
    Функция для получения страниц объявлений в .html формате

    :param pages_paths: Список путей к файлам для скрапинга
    :param url: Ссылка на страницу для получения кода
    :param args:
    :param kwargs:
    :return: создает data.json
    """
    try:
        new_url = url.split("/transporter")[0]
        abs = []
        for path in enumerate(pages_paths):
            id = path[0] + 1
            with open(path[1], "r") as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")
            link = soup.find(class_="ls-titles").find("a").get("href")

            url = f"{new_url}{link}"
            path = f"data/data_pages/car_{id}.html"
            print(url)
            get_html(url, path, False)
            context = get_data(path, id, url)
            abs.append(context)
        list = {"abs": abs}
        with open("data.json", "w") as file:
            json.dump(list, file, indent=4, ensure_ascii=False)

    except Exception as _ex:
        errors_log(traceback.format_exc())

    finally:
        "function get_page_of_car has done successfully"


def get_data(page_path: str, id: int, url: str, *args, **kwargs) -> dict:
    """
    Функция для скрапинга требуемых данных

    :param page_path: Путь к .html файлу страницы
    :param id: Идентификатор нашего объявления
    :param url: Ссылка на страницу
    :param args:
    :param kwargs:
    :return: Готовый словарь для последующей записи в .json
    """
    with open(page_path, "r") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    try:
        title = soup.find(class_="sc-ellipsis sc-font-xl").text
    except AttributeError:
        title = " "

    try:
        price = soup.find(class_="sc-highlighter-4 sc-highlighter-xl sc-font-bold").text
    except AttributeError:
        price = 0

    try:
        mileage = soup.find(class_="data-basic1").find("div", text=re.compile("km")).text
    except AttributeError:
        mileage = 0

    try:
        color = soup.find(class_="columns").find("div", text=re.compile("Farbe")).next_sibling.next_sibling.text
    except AttributeError:
        color = " "

    try:
        power = soup.find(class_="columns").find("div", text=re.compile("Leistung")).next_sibling.next_sibling.text
    except AttributeError:
        power = 0

    try:
        description = soup.find(class_="short-description").text
    except AttributeError:
        description = " "

    if not os.path.isdir(f"data/{id}"):
        os.mkdir(f"data/{id}")

    images = soup.find_all(class_="gallery-picture")[:3]
    for image in enumerate(images):
        img = image[1].find("img").get("data-src")
        name = image[0] + 1
        download = requests.get(img)
        out = open(f"data/{id}/img{name}.jpg", "wb")
        out.write(download.content)
        out.close()

    context = {
        "id": id,
        "href": url,
        "title": title,
        "price": price,
        "mileage": mileage,
        "color": color,
        "power": power,
        "description": description.replace("\n", " ").replace('\xa0', ''),
    }

    return context


def main(*args, **kwargs):
    """
    Функция запуска парсера

    :param args:
    :param kwargs:
    :return:
    """
    url = "https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault"
    get_pages_with_cards(url)


if __name__ == "__main__":
    main()
