from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import requests
import csv
import json

def extract_data(tariff_code_list, month_list, year_list, max_month_year, driver_path, url):
    """

    :param tariff_code_list:
    :param month_list:
    :param year_list:
    :param max_month_year:
    :param driver_path:
    :param url:
    :return:
    """
    driver = webdriver.Chrome(driver_path)
    driver.get(url)

    type_box = Select(driver.find_element_by_name('imex_type'))
    type_box.select_by_value('import')

    data = {}
    for tariff_code in tariff_code_list:
        data[tariff_code] = {}

        for year in year_list:
            for month in month_list:

                if month > max_month_year[0] and year == max_month_year[1]:
                    with open('customs/' + str(tariff_code) + '.txt', 'w') as code_file:
                        code_file.write(json.dumps(data[tariff_code]))
                    break

                hscode_box = driver.find_element_by_name('tariff_code')
                hscode_box.send_keys(tariff_code)

                country_box = Select(driver.find_element_by_name('country_code'))
                country_box.select_by_visible_text('All Country')

                month_box = Select(driver.find_element_by_name('month'))
                month_box.select_by_value(str(month))

                year_box = Select(driver.find_element_by_name('year'))
                year_box.select_by_value(year)

                search_button = driver.find_element_by_css_selector('.btn.btn-success').click()

                country_tab_xpath = '//*[@id="form1"]/div[3]/div/div[2]/div/div[1]/ul/li[1]/a'

                driver.find_element_by_xpath(country_tab_xpath).click()

                table_xpath = '//*[@id="form1"]/div[3]/div/div[2]/div/div[2]/div/table'

                WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, table_xpath)))

                all_country_table = driver.find_elements_by_xpath(table_xpath)[0]
                tds = all_country_table.find_elements_by_tag_name('td')

                if len(tds) == 0:
                    data[tariff_code][str(month) + '-' + year] = 'N/A'
                    continue
                else:
                    data[tariff_code][str(month) + '-' + year] = {}

                count = 0
                country_list = []
                for td in tds:
                    if count % 4 == 0:
                        country_list.append(td.text)
                    count += 1

                for country in country_list:
                    data[tariff_code][str(month) + '-' + year][country] = {}

                    country_box = Select(driver.find_element_by_name('country_code'))
                    country_box.select_by_value(country)

                    search_button = driver.find_element_by_css_selector('.btn.btn-success').click()

                    stats_code_tab_xpath = '//*[@id="form1"]/div[3]/div/div[2]/div/div[1]/ul/li[3]/a'
                    driver.find_element_by_xpath(stats_code_tab_xpath).click()

                    stats_table_xpath = '//*[@id="form1"]/div[3]/div/div[2]/div/div[2]/div/table'

                    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, stats_table_xpath)))

                    country_table = driver.find_elements_by_xpath(stats_table_xpath)[0]
                    country_tbody = country_table.find_elements_by_tag_name('tbody')[0]
                    country_tr_list = country_tbody.find_elements_by_tag_name('tr')

                    th_list = country_tr_list[-1].find_elements_by_tag_name('th')

                    quantity = th_list[1].text
                    cif = th_list[2].text

                    top_table = driver.find_elements_by_xpath('//*[@id="form1"]/div[3]/div/div[2]/div/div[2]/table')[0]
                    top_table_tbody = top_table.find_elements_by_tag_name('tbody')[0]
                    top_table_tr_list = top_table_tbody.find_elements_by_tag_name('tr')
                    description = top_table_tr_list[-1].find_elements_by_tag_name('td')[0].text

                    data[tariff_code]['Description'] = description
                    data[tariff_code][str(month) + '-' + year][country]['Quantity'] = quantity
                    data[tariff_code][str(month) + '-' + year][country]['CIF'] = cif

    driver.quit()

def create_country_dict(driver_path, url):

    driver = webdriver.Chrome(driver_path)
    driver.get(url)

    country_option_xpath = '//*[@id="country_code"]'

    country_option = driver.find_element_by_xpath(country_option_xpath)
    countries = country_option.find_elements_by_tag_name('option')

    cc2c = {}
    c2cc = {}
    for country in countries:
        if country.text != 'All Country':
            country_name = country.text.split(' ')
            if len(country_name) == 3:
                cc2c[country_name[0]] = country_name[2]
                c2cc[country_name[2]] = country_name[0]
            elif len(country_name) > 3:
                cc2c[country_name[0]] = " ".join(country_name[2:])
                c2cc[" ".join(country_name[2:])] = country_name[0]
            else:
                print('Error!!')

    driver.quit()

    return cc2c, c2cc

def write_to_csv(tariff_code_list, month_list, year_list, max_month_year, driver_path, url):

    dt_list = []
    dt_line = ','
    for year in year_list:
        for month in month_list:
            if month > max_month_year[0] and year == max_month_year[1]:
                break
            else:
                dt = str(month) + '-' + year
                dt_line += dt + ',,'
                dt_list.append(dt)

    data = {}
    for code in tariff_code_list:
        code = str(code)
        with open('customs/' + code + '.txt', 'r') as file:
            code_dict = json.load(file)
            data[code] = code_dict

    cc2c, c2cc = create_country_dict(driver_path, url)

    with open('data.csv', 'w') as f:
        for code in tariff_code_list:

            code = str(code)

            if 'Description' in list(data[code].keys()):
                f.write('CODE,' + code + ',"' + str(data[code]['Description']) + '"\n')
            else:
                f.write('CODE,' + code + '\n')

            f.write(dt_line + '\n')
            f.write('Country' + ',Quantity,CIF' * len(dt_list) + '\n')

            country_set = set()

            for dt in dt_list:
                if data[code][dt] != 'N/A':
                    for country_code in list(data[code][dt].keys()):
                        if country_code != 'Description':
                            country_set.add(cc2c[country_code])

            country_list = list(country_set)
            country_list.sort()

            for country in country_list:
                line = '"' + country + '"'

                country_code = c2cc[country]

                for dt in dt_list:
                    if data[code][dt] == 'N/A' or country_code not in list(data[code][dt].keys()):
                        line += ',,'
                    else:
                        line += ',"' + data[code][dt][country_code]['Quantity'] + '"'
                        line += ',"' + data[code][dt][country_code]['CIF'] + '"'
                f.write(line + '\n')

            f.write(',\n')
