import requests
from lxml import html


def get_links():
    url = "https://kb.nstu.ru/it:services"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return []

    tree = html.fromstring(response.content)
    target_div = tree.xpath('//*[@id="dokuwiki__aside"]/div/div/div')

    if not target_div:
        print("Target div not found.")
        return []

    base_url = "https://kb.nstu.ru"
    links = [
        (link.text_content().strip(), f"{base_url}{link.get('href')}")
        for link in target_div[0].xpath('.//a')[1:]
        if link.get('href') and link.get('href').startswith('/')
    ]

    return links


if __name__ == "__main__":
    services = get_links()
    for name, url in services:
        print(f"Название: {name}, Ссылка: {url}")

