import datetime
import requests
import json
import pandas as pd
from retry import retry
# import openpyxl
# import xlsxwriter

"""
Возможные фильтры: 
    -скидка (%)
    -категория
Данные которые собирает парсер:
            'id': артикул,
            'name': название,
            'price': цена,
            'salePriceU': цена со скидкой,
            'sale': % скидки,
            'brand': бренд,
            'rating': рейтинг товара,
            'supplier': продавец,
            'supplierRating': рейтинг продавца,
            'feedbacks': отзывы,
            'reviewRating': рейтинг по отзывам,
            'promoTextCard': промо текст карточки,
            'promoTextCat': промо текст категории
            'pics': кол-во картинок
            'img': ссылки на картинки
            'link': ссылка
"""


def get_catalogs_wb() -> dict:  # полный каталог Wildberries
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json'
    headers = {'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    return requests.get(url, headers=headers).json()


def get_data_category(catalogs_wb: dict) -> list:  # сбор данных категорий из каталога Wildberries
    catalog_data = []
    if isinstance(catalogs_wb, dict) and 'childs' not in catalogs_wb:
        catalog_data.append({
            'name': f"{catalogs_wb['name']}",
            'shard': catalogs_wb.get('shard', None),
            'url': catalogs_wb['url'],
            'query': catalogs_wb.get('query', None),
            'seo': catalogs_wb.get('seo', catalogs_wb['name'])
        })
    elif isinstance(catalogs_wb, dict):
        catalog_data.extend(get_data_category(catalogs_wb['childs']))
    else:
        for child in catalogs_wb:
            catalog_data.extend(get_data_category(child))
    return catalog_data


def search_category_in_catalog(seo, catalog_list: list) -> dict:  # ????
    for catalog in catalog_list:
        if catalog.get('seo') == seo or catalog['name'] == seo:
            return catalog


def get_data_from_json(json_file: dict) -> list:
    data_list = []
    for data in json_file['data']['products']:
        sku = data.get('id')
        name = data.get('name')
        price = int(data.get("priceU") / 100)
        salePriceU = int(data.get('salePriceU') / 100)
        sale = data.get('sale')
        brand = data.get('brand')
        rating = data.get('rating')
        supplier = data.get('supplier')
        supplierRating = data.get('supplierRating')
        feedbacks = data.get('feedbacks')
        reviewRating = data.get('reviewRating')
        promoTextCard = data.get('promoTextCard')
        promoTextCat = data.get('promoTextCat')
        pics = data.get('pics')
        img = get_images(int(sku), pics)
        data_list.append({
            'id': sku,
            'name': name,
            'price': price,
            'salePriceU': salePriceU,
            'sale': sale,
            'brand': brand,
            'rating': rating,
            'supplier': supplier,
            'supplierRating': supplierRating,
            'feedbacks': feedbacks,
            'reviewRating': reviewRating,
            'promoTextCard': promoTextCard,
            'promoTextCat': promoTextCat,
            'pics': pics,
            'img': img,
            'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/detail.aspx?targetUrl=BP'
        })
        # print(f"SKU:{data['id']} Цена: {int(data['salePriceU'] / 100)} Название: {data['name']} Рейтинг: {data['rating']}")
    return data_list


def get_images(sku: int, pics: str):
    _short_id = sku // 100000
    """Используем match/case для определения basket на основе _short_id"""
    if 0 <= _short_id <= 143:
        basket = '01'
    elif 144 <= _short_id <= 287:
        basket = '02'
    elif 288 <= _short_id <= 431:
        basket = '03'
    elif 432 <= _short_id <= 719:
        basket = '04'
    elif 720 <= _short_id <= 1007:
        basket = '05'
    elif 1008 <= _short_id <= 1061:
        basket = '06'
    elif 1062 <= _short_id <= 1115:
        basket = '07'
    elif 1116 <= _short_id <= 1169:
        basket = '08'
    elif 1170 <= _short_id <= 1313:
        basket = '09'
    elif 1314 <= _short_id <= 1601:
        basket = '10'
    elif 1602 <= _short_id <= 1655:
        basket = '11'
    elif 1656 <= _short_id <= 1919:
        basket = '12'
    elif 1920 <= _short_id <= 2045:
        basket = '13'
    elif 2046 <= _short_id <= 2189:
        basket = '14'
    elif 2190 <= _short_id <= 2405:
        basket = '15'
    else:
        basket = '16'

    """Делаем список всех ссылок на изображения и переводим в строку"""
    link_str = "".join([
        f"https://basket-{basket}.wb.ru/vol{_short_id}/part{sku // 1000}/{sku}/images/big/{i}.jpg;"
        for i in range(1, pics + 1)])
    return link_str


@retry(Exception, tries=-1, delay=0)
def scrap_page(page: int, shard: str, query: str, discount: int = None) -> dict:
    """Сбор данных со страниц"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.wildberries.ru",
        'Content-Type': 'application/json; charset=utf-8',
        'Transfer-Encoding': 'chunked',
        "Connection": "keep-alive",
        'Vary': 'Accept-Encoding',
        'Content-Encoding': 'gzip',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }
    url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub' \
          f'&dest=-1257786' \
          f'&locale=ru' \
          f'&page={page}' \
          f'&sort=popular&spp=0' \
          f'&{query}' \
          f'&discount={discount}'
    r = requests.get(url, headers=headers)
    return r.json()


# def save_excel(data: list, filename: str):
#     df = pd.DataFrame(data)
#     writer = pd.ExcelWriter(f'{filename}.xlsx')
#     df.to_excel(writer, sheet_name='data', index=False)
#     writer.sheets['data'].set_column(0, 1, width=10)
#     writer.sheets['data'].set_column(1, 2, width=34)
#     writer.sheets['data'].set_column(2, 3, width=8)
#     writer.sheets['data'].set_column(3, 4, width=9)
#     writer.sheets['data'].set_column(4, 5, width=4)
#     writer.sheets['data'].set_column(5, 6, width=10)
#     writer.sheets['data'].set_column(6, 7, width=5)
#     writer.sheets['data'].set_column(7, 8, width=25)
#     writer.sheets['data'].set_column(8, 9, width=10)
#     writer.sheets['data'].set_column(9, 10, width=11)
#     writer.sheets['data'].set_column(10, 11, width=13)
#     writer.sheets['data'].set_column(11, 12, width=19)
#     writer.sheets['data'].set_column(12, 13, width=19)
#     writer.sheets['data'].set_column(13, 14, width=67)
#     writer.close()
#     print(f'Все сохранено в {filename}.xlsx\n')


def parser(seo: str, discount: int = 0):
    # получаем данные по заданному каталогу
    catalog_data = get_data_category(get_catalogs_wb())
    try:
        # поиск введенной категории в общем каталоге
        category = search_category_in_catalog(seo=seo, catalog_list=catalog_data)
        data_list = []
        for page in range(1, 50):  # вб отдает 50 страниц товара
            data = scrap_page(
                page=page,
                shard=category['shard'],
                query=category['query'],
                discount=discount)
            data_page = get_data_from_json(data)
            if len(data_page) > 0:
                data_list.extend(data_page)
            else:
                break
        return data_list
    except TypeError:
        print('Ошибка! Возможно не верно указан раздел. Удалите все доп фильтры с ссылки')
    except PermissionError:
        print('Ошибка! Вы забыли закрыть созданный ранее excel файл. Закройте и повторите попытку')