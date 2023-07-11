import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from loguru import logger

from kwork_parser_bot.services.kwork.api.types import Project


def get_projects():
    url = "https://kwork.ru/projects"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) \
                                                Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)'}
    projects = []
    response = requests.get(url, headers=headers)
    logger.info("Status code: %d. Length: %d " % (response.status_code, len(response.text)))
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("div[class*=js-card]")
    for item in items[:]:
        title = item.select_one("div[class*=header-title]")
        title = title.text if title else "Error title"
        price = item.select_one("div.wants-card__right")
        price = re.findall(r"\d{3}|\d{1,2}\s\d{3}", str(price))
        price = " - ".join(price)
        description = item.select_one("div.breakwords.hidden")
        description = description.text.replace("Скрыть", "").strip() if description else "Description error"
        if description == "Description error":
            description = item.select_one("div.breakwords.first-letter ~ div")
            description = description.text if description else "Description error2"
        proposal_count = item.find(lambda tag: tag.name == "span" and "Предложений:" in tag.text)
        proposal_count = re.findall(r"\d+", proposal_count.text)[0] if proposal_count else "Prop error"
        author = item.select_one("a.v-align-t")
        author = author.text if author else "Author error"
        link = item.select_one("div.wants-card__header-title a")
        link = link['href'] if link else "Link error"
        time_left = item.find(lambda tag: tag.name == "span" and "Осталось" in tag.text)
        time_left = time_left.text if time_left else "timer error"
        project = Project(
            title=title,
            description=description,
            author=author,
            offers=proposal_count,
            price=price,
            time_left=time_left

        )
        projects.append(project)
    return projects


def main():
    projects = get_projects()
    pprint(projects)


if __name__ == '__main__':
    main()
