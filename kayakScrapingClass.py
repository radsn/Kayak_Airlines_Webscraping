from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
import time
import csv
import re



class KayakScraper(object):
    def __init__(self):
        self.driver = webdriver.Chrome("./chromedriver/chromedriver")
        self.file = open("./data/kayak.csv",'w+')
        self.fieldnames = ['price','src_stops','dest_stops',
                    'src_airport_stops', 'dest_airport_stops',
                    'src_duration', 'dest_duration',
                    'src_airport', 'dest_airport',
                    'src_time', 'dest_time',
                    'src_carrier', 'dest_carrier',
                    'sort'
                ]

        ## Dictionary to CSV writer class
        self.writer = csv.DictWriter(self.file,
                fieldnames = self.fieldnames)
        ## Write column names to CSV header
        self.writer.writeheader()

        self.driver.get("https://www.kayak.com/")
        time.sleep(5)

    def __del__(self):
        self.driver.quit()
        del self.writer
        self.file.close()
        

    def show_more_results(self):
        try:        
            showMoreResults_button = self.driver.find_element_by_xpath('//a[@class="moreButton"]')
            showMoreResults_button
            time.sleep(1)
        except:
            pass


    def scrape_data(self, _sort = "best"):
        # if _sort == "cheapest":
        #     self.clickCheapest()
        # elif _sort == "quickest":
        #     self.clickQuickest()
        
       #find prices
        prices = self.waitobject('//span[@class="price option-text"]')
        prices_list = [tag.text.replace('$','') for tag in prices if tag.text != '']
        prices_list = list(map(int, prices_list))

        #find number of stops
        stops  = self.waitobject('//div[@class="section stops"]/div[1]')
        stops_list = [tag.text[0] for tag in stops if stops != '']
        stops_list = [tag.replace('n','0') for tag in stops_list]
        stops_list = list(map(int, stops_list))
        source_stops_list = stops_list[0::2]
        destination_stops_list = stops_list[1::2]

        #find airport cities for stops
        airport_stops = self.waitobject('//div[@class="section stops"]/div[2]')
        airport_stops_list = [tag.text for tag in airport_stops if airport_stops != '']
        source_airport_stops_list = airport_stops_list[0::2]
        destination_airport_stops_list = airport_stops_list[1::2]
        
        #find durations
        durations = self.waitobject('//div[@class="section duration"]/div[1]')
        durations_list = [tag.text for tag in durations]
        source_durations_list = durations_list[0::2]
        destination_durations_list = durations_list[1::2]
        
        #find airports cities for source and destination
        airports = self.waitobject('//div[@class="section duration"]/div[2]')
        airports_list = [tag.text for tag in airports]
        source_airports_list = airports_list[0::2]
        destination_airports_list = airports_list[1::2]

        #find the time
        times = self.waitobject('//div[@class="section times"]/div[1]')
        times_list = [tag.text for tag in times]
        source_times_list = times_list[0::2]
        destination_times_list = times_list[1::2]
        
        #find carriers
        carriers = self.waitobject('//div[@class="section times"]/div[2]')
        carriers_list = [tag.text for tag in carriers]
        source_carriers_list = carriers_list[0::2]
        destination_carriers_list = carriers_list[1::2]
    

        ## Store to dictionary
        kayak_dict = {}
        kayak_dict[self.fieldnames[0]]  = prices_list
        kayak_dict[self.fieldnames[1]]  = source_stops_list
        kayak_dict[self.fieldnames[2]]  = destination_stops_list
        kayak_dict[self.fieldnames[3]]  = source_airport_stops_list
        kayak_dict[self.fieldnames[4]]  = destination_airport_stops_list
        kayak_dict[self.fieldnames[5]]  = source_durations_list
        kayak_dict[self.fieldnames[6]]  = destination_durations_list
        kayak_dict[self.fieldnames[7]]  = source_airports_list
        kayak_dict[self.fieldnames[8]]  = destination_airports_list
        kayak_dict[self.fieldnames[9]]  = source_times_list
        kayak_dict[self.fieldnames[10]] = destination_times_list
        kayak_dict[self.fieldnames[11]] = source_carriers_list
        kayak_dict[self.fieldnames[12]] = destination_carriers_list
        print("*"*50)
        print(kayak_dict)

        return (_sort, kayak_dict)



    def waitobject(self, xpath):
        return WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))

    def scrape_flight(self, url):
        self.driver.get(url)
        self.closePopup()
        for ordering, data in self.scrape_sortings():
            for row in pd.DataFrame(data).iterrows():
                print(row)
                temp_dict = row[1].to_dict()
                temp_dict[self.fieldnames[13]] = ordering
                self.writer.writerow(temp_dict)

    def scrape_sortings(self):
        """ returns scraped data in 3-tuple of differents sorting methods on flight page
            in order (best, cheapest, quickest)"""
        return [self.scrape_data()]

       # self.scrape_data("cheapest"),
       # self.scrape_data("quickest"))


    def closePopup(self):
        """ Close popups that appear on flight pages"""
        try:
            popUp_button = self.driver.find_elements_by_xpath('//button[contains(@id, "dialog-close") and contains(@class, "Button-No-Standard-Style close ")]')
            popUp_button[5].click()
            time.sleep(15)
        except:
            pass


    # def clickQuickest(self):
    #     """ Helper function to change sort on page"""
    #     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@data-code = "duration"]'))).click()

    # def clickCheapest(self):
    #     """ Helper function to change sort on page"""
    #     cheap = waitobject(driver, '//a[@data-code = "price"]')
    #     cheap.click()

    def makeFlightURL(self,source,dest,start_date,end_date):
        return f"https://www.kayak.com/flights/{source}-{dest}/{start_date}/{end_date}?sort=bestflight_a"



if __name__ == "__main__":
    scraper = KayakScraper()
    scraper.scrape_flight(scraper.makeFlightURL("NYC","LAX","2019-08-30","2019-09-02"))
