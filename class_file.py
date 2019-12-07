# coding: utf-8
# author: Junwei Deng
# institute: UMSI
# SI507 Final Project

class Faculty_Filter:
    def __init__(self):
        self.first_flag = False
        self.second_flag = False
        self.campus_flag = False
        self.first = ""
        self.second = ""
        self.campus = ""
    def clear(self):
        self.first_flag = False
        self.second_flag = False
        self.campus_flag = False
    def __str__(self):
        #WHERE Schools.Location = 'N'
        returnstr = ""
        if self.first_flag or self.second_flag or self.campus_flag:
            returnstr = "WHERE "
        if self.campus_flag:
            returnstr += "Schools.Location = \'" + self.campus + "\' "
            if self.first_flag or self.second_flag:
                returnstr += "AND "
        if self.first_flag:
            returnstr += "Faculties.First_Aff = \'" + self.first + "\' "
            if self.second_flag:
                returnstr += "AND "
        if self.second_flag:
            returnstr += "Faculties.Second_Aff = \'" + self.second + "\' "
        return returnstr

# faculty_filter = Faculty_Filter()
# faculty_filter.second_flag = True
# faculty_filter.second = "Engineering"
# faculty_filter.campus_flag = True
# faculty_filter.campus = "N"
# print(faculty_filter)