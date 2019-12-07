# coding: utf-8
# author: Junwei Deng
# institute: UMSI
# SI507 Final Project

import json
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
from class_file import *
from data_process import *
from data_display import *

CACHE_FNAME = 'proj_final_cache.json'
DBNAME = 'proj_final.db'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

# Still set the unique combination as the url ifself
def params_unique_combination(url):
    return url

# Input: baseurl - a string which is the url of the crawling 
#        f       - a function pointer shows the type of the page
def make_request_using_cache(baseurl, f):
    unique_ident = params_unique_combination(baseurl)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        # print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        # print("Making a request for new data...")
        # Make the request and cache the new data
        resp = f(baseurl)
        CACHE_DICTION[unique_ident] = resp
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

# Input: page - a string which is the url of the crawling 
def get_school_list(page):
    # https://umich.edu/schools-colleges/
    user_agent = {'User-agent': 'Mozilla/5.0'}
    html = requests.get(page, headers=user_agent).text
    page_soup = BeautifulSoup(html, 'html.parser')
    content_li = page_soup.find_all(class_ = "nav-block")[0].find("ul").find_all("li")
    school_list = []
    website_list = []
    location = ['N', 'N', 'C', 'C', 'C', 'N', 'C', 'C', 'C', 'C', 'C', 'C', 'N', 'C', 'C', 'C', 'C', 'C', 'C'] # Not listed in the webpage so I add it manually, I can remove it if it does not meet the requirement
    for item in content_li:
        school_list.append(item.get_text())
        website_list.append(item.find(name = 'a').get('href'))
    school_list_dic = {}
    for i in range(len(school_list)):
        keyword_list = school_list[i].lower().split()
        school_list_dic[school_list[i]] = {"keywords": keyword_list, "website":website_list[i], 'location':location[i]}
    # print(school_list_dic)
    return school_list_dic

# Input: page - a string which is the url of the crawling 
def get_midas_data(page):
    user_agent = {'User-agent': 'Mozilla/5.0'}
    html = requests.get(page, headers=user_agent).text
    page_soup = BeautifulSoup(html, 'html.parser')
    content_h3 = page_soup.find_all("h3")
    content_div = page_soup.find_all(class_ = 'desc')
    content_h3 = content_h3[4:]
    weblist = []
    brief_desc = []
    for item in content_div:
        brief_desc.append(item.get_text().strip())
    for item in content_h3:
        try:
            content_a = item.find(name = 'a').get('href')
            weblist.append(content_a)
        except:
            pass
    result = {}
    for i in range(len(weblist)):
        page_text_tmp = requests.get(weblist[i], headers=user_agent).text
        page_soup_tmp = BeautifulSoup(page_text_tmp, 'html.parser')
        content_h1 = page_soup_tmp.find_all("h1")
        content_h3 = page_soup_tmp.find_all("h3")
        content_div = page_soup_tmp.find_all(class_ = 'faculty-content')
        content_button = page_soup_tmp.find_all(class_ = "staff-button")
        content_department = page_soup_tmp.find(class_ = "faculty-right").find("p").get_text().split("\n")
        aff_school = []
        for department in content_department:
            for key, value in school_list_dic.items():
                flag = False
                list_department = department.lower().split(" ")
                for word in list_department:
                    if word.strip(",") == "and":
                        continue
                    for word_fa in value["keywords"]:
                        if word.strip(",") == word_fa:
                            aff_school.append(key)
                            flag = True
                            break
                        if word.strip(",") == "lsa":
                            aff_school.append("Literature, Science,and the Arts")
                            flag = True
                            break
                    if flag:
                        break
                if flag:
                    break
        first_aff = ""
        second_aff = ""
        try:
            first_aff = aff_school[0]
        except:
            pass
        try:
            second_aff = aff_school[1]
        except:
            pass
        try:
            p_web = content_button[2].find(name = 'a').get('href')
        except:
            p_web = ""
        try:
            phone = content_button[1].get_text()
            if phone == "Website":
                p_web = content_button[1].find(name = 'a').get('href')
                phone = ""
        except:
            phone = ""
        try:
            email = content_button[0].get_text()
            if email == "Website":
                p_web = content_button[0].find(name = 'a').get('href')
                email = ""
        except:
            email = ""
        result[content_h1[0].get_text()] = {"page": weblist[i], "brief_desc": brief_desc[i], "title": content_h3[0].get_text(), "first_aff": first_aff, "second_aff": second_aff,"long_desc": content_div[0].get_text(), "email": email, "phone": phone, "per_web": p_web}
        time.sleep(0.5) # in case the website may list me to the black list
        # print(content_h1[0].get_text())
    return result

# Input: page - a string which is the url of the crawling 
def get_umsi_data(page):
    header = {'User-Agent': 'SI_CLASS'}
    html = requests.get(page, headers=header).text
    page_soup = BeautifulSoup(html, 'html.parser')
    content_cata = page_soup.find_all(class_ = "views-field views-field-catalog")
    content_title = page_soup.find_all(class_ = "views-field views-field-title")
    # content_website = content_title.find(name = 'a').get('href')
    cata_list = []
    title_list = []
    web_list = []
    content_cata = content_cata[1:]
    content_title = content_title[1:]
    result = {}
    for item in content_cata:
        cata_list.append(item.get_text().strip())
    for item in content_title:
        title_list.append(item.get_text().strip())
        web_list.append("https://www.si.umich.edu" + item.find(name = 'a').get('href'))
    for i in range(len(web_list)):
        html_class = requests.get(web_list[i], headers=header).text
        class_page_soup = BeautifulSoup(html_class, 'html.parser')
        desc = class_page_soup.find(class_ = "course2desc").get_text().strip("View syllabus")
        credit = class_page_soup.find(class_ = "course2credit").get_text().strip("View syllabus").strip("Credit Hours:").strip()
        forcepre = class_page_soup.find(class_ = "course2prer").get_text().strip("View syllabus").strip("Required prerequisites:").strip()
        result[cata_list[i]] = {"title": title_list[i], "page": web_list[i], "desc": desc, "credit": credit, "forced pre": forcepre}
        # print(title_list[i])
        time.sleep(0.5)
    return result

# Create the database
def create_database(school_list_dic, people_dic, course_dic):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    # Rebuild the whole databse
    cur.execute("DROP TABLE IF EXISTS 'Schools'")
    conn.commit()
    cur.execute("DROP TABLE IF EXISTS 'Faculties'")
    conn.commit()
    cur.execute("DROP TABLE IF EXISTS 'Courses'")
    conn.commit()
    print("Prepare table 1...")
    cur.execute(
        '''
        CREATE TABLE 'Schools' (
                'Id'        INTEGER PRIMARY KEY AUTOINCREMENT,
                'Name'  TEXT,
                'Website' TEXT,
                'Location' TEXT
        );
        '''
    )
    conn.commit()
    for key, value in school_list_dic.items():
        statement = "INSERT INTO Schools(Name, Website, Location) VALUES ("
        statement += "\"" + str(key) + "\"" + ","
        statement += "\"" + str(value["website"]) + "\"" + ","
        statement += "\"" + str(value["location"]) + "\"" + ");"
        cur.execute(statement)
        conn.commit()
    print("Prepare table 2...")
    cur.execute(
        '''
        CREATE TABLE 'Faculties' (
                'Id'        INTEGER PRIMARY KEY AUTOINCREMENT,
                'Name' TEXT,
                'Page'  TEXT,
                'Brief_desc' TEXT,
                'Title' TEXT,
                'First_Aff' TEXT,
                'Second_Aff' TEXT,
                'Long_desc' TEXT,
                'Email' TEXT,
                'Phone' TEXT,
                'Per_web' TEXT
        );
        '''
    )
    for key, value in people_dic.items():
        statement = "INSERT INTO Faculties(Name, Page, Brief_desc, Title, First_Aff, Second_Aff, Long_desc, Email, Phone, Per_web) VALUES ("
        statement += "\"" + str(key) + "\"" + ","
        statement += "\"" + str(value["page"]) + "\"" + ","
        statement += "\"" + str(value["brief_desc"]) + "\"" + ","
        statement += "\"" + str(value["title"]) + "\"" + ","
        statement += "\"" + str(value["first_aff"]) + "\"" + ","
        statement += "\"" + str(value["second_aff"]) + "\"" + ","
        statement += "\'" + str(value["long_desc"]).replace("\'", "\'\'").replace("\n", "").replace("\r", "") + "\'" + ","
        statement += "\"" + str(value["email"]) + "\"" + ","
        statement += "\"" + str(value["phone"]) + "\"" + ","
        statement += "\"" + str(value["per_web"]) + "\"" + ");"
        cur.execute(statement)
        conn.commit()
    
    print("Prepare table 3...")
    cur.execute(
        '''
        CREATE TABLE 'Courses' (
                'Id'        INTEGER PRIMARY KEY AUTOINCREMENT,
                'Number' TEXT,
                'Title' TEXT,
                'Page' TEXT,
                'Desc' TEXT,
                'Credit' REAL,
                'Forced_pre' TEXT
        );
        '''
    )
    for key, value in course_dic.items():
        statement = "INSERT INTO Courses(Number, Title, Page, Desc, Credit, Forced_pre) VALUES ("
        statement += "\"" + str(key) + "\"" + ","
        statement += "\"" + str(value["title"]) + "\"" + ","
        statement += "\"" + str(value["page"]) + "\"" + ","
        statement += "\"" + str(value["desc"]).replace("\"", "\'\'").replace("\'", "\'\'").replace("\n", "").replace("\r", "") + "\"" + ","
        statement += str(float(value["credit"])) + ","
        statement += "\'" + str(value["forced pre"]) + "\'" + ");"
        cur.execute(statement)
        conn.commit()

    conn.close()

def print_welcome_text():
    with open('M.txt') as f:
        print(f.read())

def print_help_text():
    with open('help.txt') as f:
        print(f.read())

if __name__=="__main__":
    print_welcome_text()
# Create three dictionary for three database table
    school_list_dic = make_request_using_cache("https://umich.edu/schools-colleges/", get_school_list)
    print("School list is crawled!")
    print("Begin crawling MIDAS faculty information...")
    people_dic = {}
    for i in range(1,18):
        page_dic = make_request_using_cache("https://midas.umich.edu/affiliated-faculty/?wpv_view_count=29518-TCPID28544&lname=&wpv_post_search=&wpv_paged={}".format(i), get_midas_data)
        people_dic.update(page_dic)
        print("{}/18 is completed".format(i))
    print("Begin crawling UMSI course information...")
    course_dic = make_request_using_cache("https://www.si.umich.edu/programs/courses/catalog", get_umsi_data)
    print("ALL DONE!\n")
# From each source, also need to capture at least 100 records
    print("We have " + str(len(school_list_dic)) + " schools!")
    print("We have " + str(len(people_dic)) + " professors!")
    print("We have " + str(len(course_dic)) + " courses!")
    print("\n------------------------------------------------------------\nEnter 'help' for command instructions.")

    command = input(">>> ").strip()
    faculty_filter = Faculty_Filter()
    while not command.lower() == "exit":
        if command.lower() == "help":
            print_help_text()
        if command.lower() == "school-distribution":
            datatmp = school_distribution_data(faculty_filter, DBNAME)
            school_distribution_plot(datatmp)
            print("A graph shows the distribution of schools under your filter is presented on your browser.")
            print("Here is your current filter (in SQL mode, blank means you are using the whole dataset):")
            print(faculty_filter)
        if command.lower() == "keyword":
            peoples_dic, words_num, words_key = keyword_data(faculty_filter, DBNAME)
            data = (peoples_dic, words_num, words_key)
            keyword_plot(data)
            print("A graph shows the distribution of keywords under your filter is presented on your browser.")
            print("Here is your current filter (in SQL mode, blank means you are using the whole dataset):")
            print(faculty_filter)
        if command.lower().split(" ")[0] == "filter":
            commandlist = command.split(" ")[1:]
            for i in range(len(commandlist)):
                if commandlist[i].split("=")[0].lower() == "campus":
                    faculty_filter.campus = commandlist[i].split("=")[1]
                    if faculty_filter.campus not in ['N', 'C']:
                        print('ERROR (campus): You can only enter \'N\' or \'C\' for North Campus and Central Campus.')
                    else:
                        faculty_filter.campus_flag = True
                        faculty_filter.campus = commandlist[i].split("=")[1]
                if commandlist[i].split("=")[0].lower() == "first-aff":
                    faculty_filter.first = commandlist[i].split("=")[1]
                    if faculty_filter.first not in school_list_dic.keys():
                        print("ERROR (first-aff): Please pay attention that you should enter the exact school name, if you don't know, please enter 'school-distribution' and see the legend.")
                    else:
                        faculty_filter.first_flag = True
                        faculty_filter.first = commandlist[i].split("=")[1]
                if commandlist[i].split("=")[0].lower() == "second-aff":
                    if faculty_filter.second not in school_list_dic.keys():
                        print("ERROR (second-aff): Please pay attention that you should enter the exact school name, if you don't know, please enter 'school-distribution' and see the legend.")
                    else:
                        faculty_filter.second_flag = True
                        faculty_filter.second = commandlist[i].split("=")[1]
        if command.lower() == "clear-filter":
            faculty_filter.clear()
        if command.lower() == "show-filter":
            print(faculty_filter)
        if command.lower().split(" ")[0] == "keyword-search":
            wordlist = command.lower().strip().lstrip("keyword-search").split(",")
            keylist = []
            for word in wordlist:
                keylist.append(word.strip())
            print("The key word you are searching on: " + str(keylist))
            print("This may take around 10 seconds...")
            try:
                data = keyword_search_data(faculty_filter, DBNAME, keylist)
                keyword_search_plot(data, keylist)
            except:
                print("ERROR (a list of words seperated by comma): There are no keywords in the descroption of our faculties in any of these words.")
        if command.lower().split(" ")[0] == "course-recommendation":
            faculty_name = command.strip().lstrip("course-recommendation").strip()
            try:
                data = course_recommendation_data(faculty_filter, DBNAME, faculty_name)
                course_recommendation_plot(data, faculty_name)
            except:
                print("ERROR (faculty name): Please copy the exact faculty name.")
        command = input(">>> ").strip()
    print("Bye, and GO BLUE!")
    # print_help_text()
# Got it!
    # create_database(school_list_dic, people_dic, course_dic)
    # faculty_filter = Faculty_Filter()
    # faculty_filter.campus_flag = True
    # faculty_filter.campus = "C"

    # datatmp = school_distribution_data(faculty_filter, DBNAME)
    # school_distribution_plot(datatmp)

    # peoples_dic, words_num, words_key = keyword_data(faculty_filter, DBNAME)
    # data = (peoples_dic, words_num, words_key)
    # keyword_plot(data)

    # data = keyword_search_data(faculty_filter, DBNAME, ['biology','image'])
    # keyword_search_plot(data, ['biology','image'])

    # data = course_recommendation_data(faculty_filter, DBNAME, "V. G. Vinod Vydiswaran")
    # course_recommendation_plot(data)





