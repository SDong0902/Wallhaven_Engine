import os
import os.path
import time
from pprint import pprint as pp

import bs4
import pandas as pd
import requests
from bs4 import BeautifulSoup


class WallHeavenDownloader:

    def __init__(self, url: str, directory: str, start_page: int = 1, end_page: int = -1):
        """

        :param url: the main page URL to download the images from: str
        :param directory: the filepath directory to save the images: str
        :param start_page: start page to download, inclusive
        :param end_page: end page to download, inclusive

        """
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)

        self.directory = directory

        self.start_page = start_page
        self.end_page = end_page
        #self.url = self.create_valid_url(url)
        self.url = url

        self.ua = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/98.0.4758.80 Safari/537.36"}

        self.previous_page_len = 0
        self.success = 0
        self.fail = 0
        self.total_items = 0
        self.page_number_list = []

    def home_page_download(self, url):
        home_page = self.get_main_page(url)
        feat_row = home_page.find("div", class_="feat-row").find_all("a")
        more_feat = home_page.find("div", class_="more-feat").find_all("a")
        feat = feat_row + more_feat
        img_list = []
        for i in feat:
            img_list.append(i.get('href'))

        return img_list

    def tag_page_download(self, url):
        tag_page = self.get_main_page(url)
        tag_images = tag_page.find("section", class_="thumb-listing thumbs-container").find_all("figure")
        tag_list = []
        for i in tag_images:
            a = i.find("a", class_="preview")
            tag_list.append(a.get("href"))

        return tag_list

    # Takes the main page with all the preview images html page and
    # returns a html text file
    def get_main_page(self, main_url: str, encoding: str = "utf-8") -> bs4.BeautifulSoup:

        resp = requests.get(main_url, headers=self.ua)
        resp.encoding = encoding
        pp(f"Main page response: {resp}")
        main_page = BeautifulSoup(resp.text, "html.parser")
        return main_page

    # This is for standard pages (e.g. Search or from tags on the wallhaven.cc page), not for tag pages from
    # the 'related tags' section or the home page of wallhaven.cc
    def get_all_pages(self, main_page: bs4.BeautifulSoup) -> list:
        """

        :param main_page  html file of the main page where all the images are displayed, divided in pages
        :type main_page bs4.BeautifulSoup

        :return: returns a list of URLs that will be processed in the start method to download the images
        :rtype: list

        """
        # Internal function, used for taking the page number of the href string, in int
        def take_href_page(href_: str) -> int:
            """
            :param href_: a href string such as 'https://wallhaven.cc/search?q=something&page=2': str
            :return: returns the href page number in int, 2 for the above example: int
            """
            return int(href_.split("=")[-1])

        # Locate the 'place' in the main_page html document where the next pages are, and put into a list
        pages = main_page.find("ul", class_="pagination").find_all("a")
        page_list = []  # Empty list to store the page URLs to be downloaded
        # Take the initial part of the URL, without the page number: 'https://wallhaven.cc/search?q=something&page='
        href_start_part = "=".join(pages[0].get("href").split("=")[:-1])+"="

        # if the pages in the main_page are more than 1, fill the return list with the start page URL (to be inclusive)
        # else, just return the main_page url which will be the only one to be downloaded
        if len(pages) > 1:
            page_list.append(f'{href_start_part}{self.start_page}')
            self.page_number_list.append(str(self.start_page))
        else:
            page_list.append(main_page)
            self.page_number_list.append(1)
            return page_list

        # Set an index count to check if there are pages skipped in the main_page document, which will be recovered
        index = 1
        for page in pages:  # loop into the pages list
            url = page.get("class")     # the URL we want does not have the class attribute, so filter only them
            if url is None:
                href = page.get("href")     # the URL is stored in the 'href' attribute, so get the URL from it
                current_page = take_href_page(href)    # record the current page we are looping (only the number in int)

                # filter the range to be between start and end inclusive
                if current_page > self.start_page and (current_page <= self.end_page or self.end_page == -1):

                    previous_page = take_href_page(page_list[index-1])  # take the previous value from the list

                    # check if between the current and the previous page number, there are any missing pages
                    if previous_page != current_page-1:
                        # fill te missing pages
                        while previous_page != current_page-1:
                            # beginning from the previous page number, start adding the missing pages one by one
                            additional_page = previous_page + 1
                            additional_href = href_start_part + str(additional_page)
                            page_list.append(str(additional_href))   # append the missing page
                            self.page_number_list.append(additional_page)
                            previous_page = additional_page  # update the previous page
                            index += 1  # Increase the index to keep on track of the current location in the list
                        continue
                    page_list.append(href)
                    self.page_number_list.append(str(current_page))
                    index += 1  # Increase the index to keep on track of the current location in the list

        return page_list    # Return the list with all the URLs

    # Takes all the single images URLs out from one single page html text file and
    # appends it to a list. Returns the list with all the image URLs of a single page
    def get_child_url(self, page: str) -> list:

        child_url = self.get_main_page(page).find("div", class_="thumbs-container thumb-listing infinite-scroll").find_all("a")
        child_page_url = []
        for i in child_url:
            url = i.get("data-href")
            if url is not None:
                if "tags" in url:
                    child_page_url.append(url)
        return child_page_url

    # Downloads the whole page images from the child url. Each download iteration, there is
    # a sleep time to prevent overloading the web server
    def download_one_page_img(self, child_url: list, page: str) -> None:

        count = 1
        pp(f"Start Downloading Page {page}, total items: {len(child_url)}")
        self.total_items += len(child_url)

        for i in child_url:
            pp(f"Downloading {i}...")
            try:
                img_name = self.download_img(i)

                pp(f"Downloaded image {img_name}, Page #{page} Image #{count}, {len(child_url) - count} Images left in "
                   f"the page")
                self.success += 1
                # break  # Just for testing download one single image

            except AttributeError:
                time.sleep(3)
                res = self.try_download_4_times(i, 0)
                if res[0]:
                    pp(f"Downloaded image {res[1]}, Page #{page} Image #{count}, {len(child_url) - count} Images left in "
                       f"the page")
                else:
                    message = f"Image {i} Download Failed, Page #{page} Image #{count}, {len(child_url) - count} " \
                              f"Images left in the page "
                    pp(message)

                    # If the download fails, record the failed image into the log text file
                    self.fail += 1
                    with open("log.txt", mode="a") as f:
                        f.write(message + "\n")

            count += 1
            time.sleep(3)

    # Download a single image from the URL provided and saves it into the directory
    def download_img(self, url: str) -> str:

        child_resp = requests.get(url)
        child_page = BeautifulSoup(child_resp.text, "html.parser")
        img_area = child_page.find("div", class_="scrollbox")
        img = img_area.find("img").get("src")
        img_name = img.split("/")[-1]

        with open(self.directory + "/" + img_name, mode="wb") as f:
            f.write(requests.get(img).content)

        return img_name

    # Sometimes the download of the image might fail, so we recursively try to download the
    # image 4 times more to prevent losing images due to fail. If it still fails downloading,
    # it moves to the next one writing the fail into the log
    def try_download_4_times(self, url: str, count: int) -> list:
        img_name = ""
        try:
            img_name = self.download_img(url)

        except AttributeError:
            if count < 4:
                time.sleep(3)
                count += 1
                self.try_download_4_times(url, count)
            else:
                return [0]

        return [1, img_name]

    # Count the items in the directory to check if there are any images missing. For test purposes only
    def count_items(self) -> None:

        pp(f"Items in the {self.directory.split('/')[-1]} folder: " + str(len([name for name in os.listdir
        (self.directory) if os.path.isfile(os.path.join(self.directory, name))])))

    # Main function of the class
    def start(self) -> None:

        print("-" * 100 + "\n")
        print("Start Download Operation...\n")
        if self.url == "https://wallhaven.cc/":
            child_page = self.home_page_download(self.url)
            self.download_one_page_img(child_page, 'Home')

        elif "/tag/" in self.url:
            child_page = self.tag_page_download(self.url)
            self.download_one_page_img(child_page, 'Tag')
        else:
            main_page = self.get_main_page(self.url)
            pages = self.get_all_pages(main_page)
            i = 0
            for page in pages:

                child_page = self.get_child_url(page)

                if len(child_page) != 0:
                    self.download_one_page_img(child_page, self.page_number_list[i])
                    i += 1

        self.count_items()
        print("\n" + "-" * 100)
        print("Download Over!\n")

        print("{:21} {:10}".format("Total Items:", str(self.total_items)),
              "{:22} {:10}".format("\nSuccessful Download:", str(self.success)),
              "{:22} {:10}".format("\nFail Download:", str(self.fail)))


if __name__ == '__main__':
    home_url = "https://wallhaven.cc/"
    url1 = "https://wallhaven.cc/search?q=tokyo%20ghoul&categories=110&purity=100&sorting=random&order=desc&seed=L7RGJd"
    tag_page1 = "https://wallhaven.cc/tag/1777"

    folder_name = "/Users/sandro/Documents/Programming_Repository/Python/Wallhaven_Download_Engine/Download_Engine/download_dir"

    downloader = WallHeavenDownloader(url=tag_page1, directory=folder_name, end_page=1)
    downloader.start()
