"""
Copyright 2011-13 Attila Zseder
Email: zseder@gmail.com

This file is part of hunmisc project
url: https://github.com/zseder/hunmisc

hunmisc is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""


from getpass import getpass

from selenium import webdriver

def get_firefox(profile_path):
    """open up an existing and working firefox"""
    profile = webdriver.FirefoxProfile(profile_path)
    driver = webdriver.Firefox(profile)
    return driver

def log_into_google(driver, username, password):
    """go to accounts google page, fill in sign up data, and click"""
    driver.get(u'http://accounts.google.com')
    driver.implicitly_wait(10)
    user_field = driver.find_element_by_id('Email')
    user_field.send_keys(username)
    pass_field = driver.find_element_by_id('Passwd')
    pass_field.send_keys(password)
    signinbutt = driver.find_element_by_id('signIn')
    signinbutt.click()
    driver.implicitly_wait(10)

def get_bib_for_article(driver, scholar_url):
    # navigate to the page of a result page of a search with only one article
    driver.get(scholar_url)
    driver.implicitly_wait(10)

    # find the import-bibtex link and click
    links = driver.find_elements_by_partial_link_text("BibTeX")
    link = links[0]
    link.click()
    driver.implicitly_wait(10)

    # return bibtex string after removing html tags
    return driver.page_source.split("<pre>")[1].split("</pre>")[0]

def l(url):
    # google account
    username = raw_input("Enter google username")
    password = getpass()

    firefox = get_firefox("/home/zseder/.mozilla/firefox/hto63qnp.default/")

    log_into_google(firefox, username, password)

    # if not using a firefox profile in which cookies are enabled,
    # and your in google user's settings the importing to Bib is turned on,
    # here you have to navigate to settings first and change that

    bib = get_bib_for_article(firefox, url)


    out = open("out.bib", "w")
    out.write(bib.encode("utf-8"))

if __name__ == "__main__":
    main()

