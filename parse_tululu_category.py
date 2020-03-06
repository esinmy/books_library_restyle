import argparse, json, os, requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def create_parser():
    parser = argparse.ArgumentParser(description="""This app allows you to bulk download 
                                                    science fiction books from tululu.org""")
    parser.add_argument("-s", "--start_page", type=int, default=1,
                        help="provide a start page for downloading (default: 1)")
    parser.add_argument("-e", "--end_page", type=int,
                        help="provide an end page for downloading (default: category's last page)")
    return parser


def get_category_last_page(lib_domain, category_path):
    """If end page is not set by user, the function determines the category's last page id.

    Args:
        category_url (str): url to desired category.

    Returns:
        int: category's last page id.

    """
    category_url = urljoin(lib_domain, category_path)
    response = requests.get(category_url, allow_redirects=False)
    response.raise_for_status()
    category_soup = BeautifulSoup(response.text, 'lxml')
    pages = category_soup.select("#content p.center a")
    last_page = pages[-1].text
    return int(last_page)


def get_books_url(lib_domain, category_path, start_page, end_page):
    category_url = urljoin(lib_domain, category_path)
    books_url = []
    for page in range(start_page, end_page + 1):
        response = requests.get(urljoin(category_url, "{}/".format(page)), allow_redirects=False)
        response.raise_for_status()
        category_soup = BeautifulSoup(response.text, 'lxml')
        books = category_soup.select("table.d_book")
        books_url += [urljoin(lib_domain, book.select_one('a')['href']) for book in books]
    return books_url


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранён текст (None: Если скачивание не удалось).

    """
    out_path = os.path.join(folder, sanitize_filename(filename))
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    if not response.status_code == 200:
        return None

    with open(out_path, 'w', encoding='UTF-8') as file:
        file.write(response.text)
    return out_path


def download_img(url, filename, folder='images/'):
    """Функция для скачивания изображений.

    Args:
        url (str): Cсылка на изображение, которое хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранёно изображение.

    """
    out_path = os.path.join(folder, sanitize_filename(filename))
    # do not download nopic.gif every time
    if os.path.exists(out_path):
        return out_path
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    with open(out_path, 'wb') as file:
        file.write(response.content)
    return out_path


if __name__ == '__main__':
    lib_domain = "http://tululu.org"
    category_path = "l55/"
    book_txt_url = urljoin(lib_domain, "txt.php?id={}")

    books_dir = "books"
    images_dir = "images"
    [Path(folder).mkdir(parents=True, exist_ok=True) for folder in [books_dir, images_dir]]

    downloaded_books_info_path = "books.json"
    downloaded_books_info = []

    parser = create_parser()
    namespace = parser.parse_args()
    start_page, end_page = namespace.start_page, namespace.end_page
    if end_page is None:
        end_page = get_category_last_page(lib_domain, category_path)

    books_url = get_books_url(lib_domain, category_path, start_page, end_page)
    for book_url in books_url:
        response = requests.get(book_url, allow_redirects=False)
        response.raise_for_status()

        book_soup = BeautifulSoup(response.text, 'lxml')
        book_head = book_soup.select_one("#content h1").text
        book_title, book_author = [part.strip() for part in book_head.split("::")]

        book_id = urlparse(book_url).path.strip("/b")
        book_path = download_txt(book_txt_url.format(book_id), book_title + '.txt')
        if book_path is None:
            continue
        # Повысьте надёжность вычисления URL? Что понадобится: urllib.parse.urljoin
        book_image_url = urljoin(lib_domain, book_soup.select_one(".bookimage img")['src'])
        book_image_name = book_image_url.split('/')[-1]
        book_reviews_raw = book_soup.select(".texts .black")
        book_reviews = [review.text for review in book_reviews_raw]
        book_genres_raw = book_soup.select("span.d_book a")
        book_genres = [book_genre.text for book_genre in book_genres_raw]
        img_path = download_img(book_image_url, book_image_name)
        book_info = {"title": book_title,
                     "author": book_author,
                     "img_src": img_path,
                     "book_path": book_path,
                     "book_reviews": book_reviews,
                     "book_genres": book_genres
                     }
        downloaded_books_info.append(book_info)
    with open(downloaded_books_info_path, "w", encoding='utf8') as file:
        json.dump(downloaded_books_info, file, ensure_ascii=False)