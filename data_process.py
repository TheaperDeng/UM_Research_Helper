# coding: utf-8
# author: Junwei Deng
# institute: UMSI
# SI507 Final Project

# SELECT COUNT(Faculties.First_Aff),Faculties.First_Aff
# FROM Faculties JOIN Schools 
# ON Faculties.First_Aff = Schools.Name
# WHERE Schools.Location = 'C' 
# GROUP BY Faculties.First_Aff

import sqlite3
from class_file import *
import nltk 
from nltk.corpus import stopwords
import re
from functools import reduce

def school_distribution_data(faculty_filter, DBNAME):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Faculties.First_Aff, COUNT(Faculties.First_Aff) FROM Faculties JOIN Schools ON Faculties.First_Aff = Schools.Name "
    statement += faculty_filter.__str__()
    statement += " GROUP BY Faculties.First_Aff ORDER BY COUNT(Faculties.First_Aff) DESC"
    cur.execute(statement)
    res = []
    for row in cur:
        # print(row)
        res.append(row)
    conn.close()
    return res

def keyword_data(faculty_filter, DBNAME):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Faculties.Long_desc, Faculties.Brief_desc FROM Faculties JOIN Schools ON Faculties.First_Aff = Schools.Name "
    statement += faculty_filter.__str__()
    cur.execute(statement)
    res = []
    for row in cur:
        # print(row)
        res.append(row)
    conn.close()
    words = {}
    peoples = {}
    for data in res:
        people = {}
        tokens = nltk.word_tokenize(data[0])
        pattern = re.compile(r'^[a-zA-Z-]')
        for word in tokens:
            if pattern.match(word) == None:
                continue
            if word.lower() in stopwords.words("english"):
                continue
            if word.lower() in ['data', 'research']:
                continue
            if not word.lower() in words:
                words[word.lower()] = 1
            else:
                words[word.lower()] += 1
            people[word.lower()] = 1
        tokens = nltk.word_tokenize(data[1])
        for word in tokens:
            if pattern.match(word) == None:
                continue
            if word.lower() in stopwords.words("english"):
                continue
            if word.lower() in ['data', 'research']:
                continue
            if not word.lower() in words:
                words[word.lower()] = 1
            else:
                words[word.lower()] += 1
            people[word.lower()] = 1
        for key in people.keys():
            if not key.lower() in peoples:
                peoples[key.lower()] = 1
            else:
                peoples[key.lower()] += 1
    words = sorted(words.items(), key = lambda x:(-int(x[1])))
    if len(words) > 100:
        words = words[0:100]
    peoples_dic = []
    words_num = []
    words_key = []
    # print(peoples)
    for data in words:
        peoples_dic.append(peoples[data[0]])
        words_num.append(data[1])
        words_key.append(data[0])
    # print(peoples_dic, words_num, words_key)
    return peoples_dic, words_num, words_key

def keyword_search_data(faculty_filter, DBNAME, custom_keyword):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    # SELECT Faculties.Long_desc, Faculties.Brief_desc, Faculties.Name FROM Faculties JOIN Schools ON Faculties.First_Aff = Schools.Name
    statement = "SELECT Faculties.Long_desc, Faculties.Brief_desc, Faculties.Name FROM Faculties JOIN Schools ON Faculties.First_Aff = Schools.Name "
    statement += faculty_filter.__str__()
    cur.execute(statement)
    res = []
    for row in cur:
        # print(row)
        res.append(row)
    conn.close()
    peoples = {}
    peoples_all = {}
    for data in res:
        people_count = [0]*len(custom_keyword)
        tokens = nltk.word_tokenize(data[0])
        pattern = re.compile(r'^[a-zA-Z-]')
        for word in tokens:
            if pattern.match(word) == None:
                continue
            if word.lower() in stopwords.words("english"):
                continue
            for i in range(len(custom_keyword)):
                if word == custom_keyword[i]:
                    people_count[i] += 1
        tokens = nltk.word_tokenize(data[1])
        for word in tokens:
            if pattern.match(word) == None:
                continue
            if word.lower() in stopwords.words("english"):
                continue
            for i in range(len(custom_keyword)):
                if word == custom_keyword[i]:
                    people_count[i] += 1
        for num in people_count:
            if not num == 0 and reduce(lambda x,y:x * y,people_count) == 0:
                peoples[data[2]] = people_count
                break
        if reduce(lambda x,y:x * y,people_count) >0:
            peoples_all[data[2]] = people_count
    peoples_all = sorted(peoples_all.items(), key = lambda x:(-int(sum(x[1]))))
    peoples = sorted(peoples.items(), key = lambda x:(-int(sum(x[1]))))
    res = peoples_all + peoples
    if len(res) > 10:
        res = res[0:10]
    # print(res)
    return res

def course_recommendation_data(faculty_filter, DBNAME, faculty_name):
    # SELECT Faculties.Long_desc, Faculties.Brief_desc, Faculties.Name 
    # FROM Faculties JOIN Schools 
    # ON Faculties.First_Aff = Schools.Name
    # WHERE Faculties.Name = "Eytan Adar"
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Faculties.Long_desc, Faculties.Brief_desc, Faculties.Name FROM Faculties JOIN Schools ON Faculties.First_Aff = Schools.Name "
    statement += "WHERE Faculties.Name = \'" + faculty_name + "\'"
    cur.execute(statement)
    res = []
    for row in cur:
        res.append(row)
    cur2 = conn.cursor()
    cur2.execute("SELECT * FROM Courses")
    res_course = []
    for row in cur2:
        res_course.append(row)
    keywords_faculty = {}
    tokens = nltk.word_tokenize(res[0][0])
    pattern = re.compile(r'^[a-zA-Z-]')
    for word in tokens:
        if pattern.match(word) == None:
            continue
        if word.lower() in stopwords.words("english"):
            continue
        if not word.lower() in keywords_faculty:
            keywords_faculty[word.lower()] = 1
        else:
            keywords_faculty[word.lower()] += 1
    tokens = nltk.word_tokenize(res[0][1])
    for word in tokens:
        if pattern.match(word) == None:
            continue
        if word.lower() in stopwords.words("english"):
            continue
        if not word.lower() in keywords_faculty:
            keywords_faculty[word.lower()] = 1
        else:
            keywords_faculty[word.lower()] += 1
    courses_dic = {}
    for course in res_course:
        course_dic = {}
        tokens = nltk.word_tokenize(course[4])
        for word in tokens:
            if pattern.match(word) == None:
                continue
            if word.lower() in stopwords.words("english"):
                continue
            # if word.lower() in ['data', 'research', 'information', 'include', 'etc', 'methods', 'current', 'academic']:
            #     continue
            if word.lower() in keywords_faculty:
                if not word.lower() in course_dic:
                    course_dic[word.lower()] = keywords_faculty[word.lower()] + 1
                else:
                    course_dic[word.lower()] += 1
        courses_dic[course[1]] = {'keyword':course_dic, 'title':course[2], 'credit':course[5], 'pre-request course':course[6], 'desc':course[4], 'page':course[3]}
    courses_dic = sorted(courses_dic.items(), key = lambda x:(-sum(x[1]['keyword'].values())))
    conn.close()
    return courses_dic[0:10]