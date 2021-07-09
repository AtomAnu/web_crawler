from utils import extract_data, create_country_dict, write_to_csv

tariff_code_list = [2701,
                    27011100,
                    27011210,
                    27011290,
                    27011900,
                    27012000,
                    2702,
                    27021000,
                    27022000,
                    2703,
                    27030010,
                    27030020,
                    2704,
                    27040010,
                    27040030,
                    2708,
                    27081000,
                    27082000,
                    2713,
                    27131100,
                    27131200,
                    27132000,
                    27139000]

month_list = list(range(1,13))
year_list = ['2018','2019','2020','2021']

max_month_year = (5, 2021)

driver_path = "/Users/frost/Documents/GitHub/web_crawler/chromedriver"

url = 'http://www.customs.go.th/statistic_report.php?ini_content=statistics_report&lang=en&left_menu=menu_report_and_news'

extract_data(tariff_code_list, month_list, year_list, max_month_year, driver_path, url)
write_to_csv(tariff_code_list, month_list, year_list, max_month_year, driver_path, url)
