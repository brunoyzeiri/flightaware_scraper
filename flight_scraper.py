#!python3
"""
Created in Nov 2019
@author: Bruno Yzeiri

"""

import platform, os, pickle, numpy, webbrowser, platform, time
import pandas as pd
from openpyxl import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException


# cwd = os.path.dirname(os.path.abspath(__file__))

# Defining the location of the Chromedriver, this should be the path where
# your downloaded chromedriver is located, look at selenium documentation
# for more details at: https://www.seleniumhq.org/docs/

if platform.system()=='Windows':
    chromedriver = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
    sl = '\\'
else:
    sl = '/'
    chromedriver = '/home/bruno/pyscripts/chromedriver'

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('--no-sandbox')
chromeOptions.add_experimental_option('excludeSwitches', ['disable-component-update'])
# chromeOptions.add_argument("load-extension=/home/bruno/.config/google-chrome/Default/Extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm")

# Here I'm adding an AdBlocker cause ads sometimes interfere with the scraper
# Note that it maps to a file that I have locally on my machine, if you need to run this
# you need to specify your own directory where the file is contained, otherwise
# simply COMMENT THIS OPTION and the scraper should be able to run anwyay provided
# the chromedriver directory is inputted correctly and chromedriver is up to date
# (older versions have problems with some of the commands I'm using in this script)
chromeOptions.add_extension('/home/bruno/Downloads/cjpalhdlnbpafiamejdnhcphjbkeiagm-1.17.0-www.Crx4Chrome.com.crx')

# TODO: Uncomment this when we get in production, at the moment is not really
# necessary to have it headless cause I want to see how the code behaves

# chromeOptions.add_argument('headless')

# ==============================================================
# Here we define some parameters that might be changed at any point

# browser = webdriver.Chrome(executable_path = chromedriver, chrome_options = chromeOptions)
# wait = WebDriverWait(browser, 20)
# actions = ActionChains(browser)

# This is the function that handles the actual complexity of the HTML structure
# of the page, it scrolls to get the object in view because otherwise it doesn't
# actually load the reviews and keeps doing it until we have the full page loaded
# with the actual reviews we want to extract with another functiion, it has some
# try/except statements that while not really beautiful and efficent handle all
# the cases where we might run into a problem safely. This should not be modified
# and the commented commands can be well deleted, thing I'm not doing simply
# cause I might be interested in rearranging the function to be more efficent
# in the future.
#
#def scroller(browser):
#    # browser = webdriver.Chrome(executable_path = chromedriver, chrome_options = chromeOptions)
#    # browser.get(link)
#    actions = ActionChains(browser)
#    for i in range(rpwine//3):
#        # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="all_reviews"]/div/div/div/a')))
#        time.sleep(3)
#        try:
#            if i > 3:
#                try:
#                    # print("Closing Ad")
#                    close_ad(browser, actions)
#                except:
#                    pass
#            showmore = browser.find_element_by_xpath(
#                '//*[@id="all_reviews"]/div/div/div/a')
#            # print("Clicking")
#            browser.execute_script("arguments[0].scrollIntoView();", showmore)
#            actions.move_to_element(showmore)
#            actions.click(showmore)
#            actions.perform()
#        except StaleElementReferenceException: 
#            try:
#                # print("Closing Ad in Exception")
#                close_ad(browser, actions)
#                showmore = browser.find_element_by_xpath(
#                    '//*[@id="all_reviews"]/div/div/div/a') 
#                browser.execute_script("arguments[0].scrollIntoView();", showmore)
#                actions.move_to_element(showmore)
#                actions.click(showmore)
#                actions.perform()
#            except:
#                continue
#            #showmore = browser.find_element_by_xpath(
#            #        '//*[@id="all_reviews"]/div/div/div/a') 
#            #browser.execute_script("arguments[0].scrollIntoView();", showmore)
#            #actions.move_to_element(showmore)
#            #actions.click(showmore)
#            #actions.perform()
#    return

def close_cookie(browser, actions):
    elemclose = browser.find_elem_by_xpath('/html/body/div[15]/div[1]/div[2]/div/div[3]/button[2]')
    actions.move_to_element(elemclose)
    actions.click(elemclose)
    actions.perform()
    return

def route_finder(browser, dep, arr):
    actions = ActionChains(browser)
    dep_input_element = browser.find_element_by_xpath('//*[@id="findRouteMain"]/div/div[1]/form/div[1]/div/input')
    arr_input_element = browser.find_element_by_xpath('//*[@id="findRouteMain"]/div/div[1]/form/div[3]/div/input')
    dep_input_element.send_keys(dep)
    arr_input_element.send_keys(arr)
    search_elem = browser.find_element_by_xpath('//*[@id="findRouteMain"]/div/div[2]/button')
    actions.move_to_element(search_elem)
    actions.click(search_elem)
    actions.perform()
    return

def plane_scraper(browser):
    l = []
    n_of_flights = browser.find_element_by_xpath('//*[@id="ffinder-refine"]/form/div[1]/div/nobr[3]/span').text[8:10]
    for i in range(0, 2*int(n_of_flights), 2):
        plane = browser.find_element_by_xpath('//*[@id="Results"]/tbody/tr[' + str(i+1) + ']/td[3]').text
        l.append(plane)
    return "_".join(l)

if __name__ == "__main__":
    browser = webdriver.Chrome(executable_path = chromedriver, chrome_options = chromeOptions)
    routes_df = pd.read_csv('df_sets2.csv')
    output_df = pd.DataFrame({}, columns=['route', 'planes'])
    for i in range(len(routes_df)):
        browser.get('https://uk.flightaware.com/')
        try:
            dep = routes_df.route[i][2:5]
            arr = routes_df.route[i][9:12]
            route_finder(browser, dep, arr)
            planes = plane_scraper(browser)
            print("Found planes")
            s = pd.Series([routes_df.route[i], planes], index=['route', 'planes'])
            output_df = output_df.append(s, ignore_index=True)
            print(output_df.head())
        except:
            print("Error incurred")
            continue
    output_df.to_csv('scraped_flight_data.csv', index=True)