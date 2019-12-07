import unittest
from proj_final import *

class TestDatabase(unittest.TestCase):
    def test_access_5assert(self):
        school_list_dic = make_request_using_cache("https://umich.edu/schools-colleges/", get_school_list)
        self.assertTrue(len(school_list_dic) == 19)
        people_dic = {}
        for i in range(1,18):
            page_dic = make_request_using_cache("https://midas.umich.edu/affiliated-faculty/?wpv_view_count=29518-TCPID28544&lname=&wpv_post_search=&wpv_paged={}".format(i), get_midas_data)
            people_dic.update(page_dic)
        self.assertTrue(people_dic["Eytan Adar"]["title"] == "Associate Professor")
        self.assertTrue(people_dic["Eytan Adar"]["first_aff"] == "Information")
        self.assertTrue(people_dic["Eytan Adar"]["second_aff"] == "Engineering")
        course_dic = make_request_using_cache("https://www.si.umich.edu/programs/courses/catalog", get_umsi_data)
        self.assertTrue(course_dic['507']["title"] == "Intermediate Programming")
    def test_storage_5assert(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        results = cur.execute("SELECT Courses.Title from Courses WHERE Courses.Number = '649'")
        result_list = results.fetchall()
        self.assertIn(('Information Visualization',), result_list)
        results = cur.execute("SELECT Courses.Credit from Courses WHERE Courses.Number = '608'")
        result_list = results.fetchall()
        self.assertIn((3.0,), result_list)
        results = cur.execute("SELECT Faculties.Email from Faculties WHERE Faculties.Name = \"Karen Alofs\"")
        result_list = results.fetchall()
        self.assertIn(("kmalofs@umich.edu",), result_list)
        results = cur.execute("SELECT Faculties.Per_web from Faculties WHERE Faculties.Name = \"Karen Alofs\"")
        result_list = results.fetchall()
        self.assertIn(("https://sites.google.com/umich.edu/alofs",), result_list)
        results = cur.execute("SELECT Schools.Location from Schools where Schools.Name = \"Architecture & Urban Planning\"")
        result_list = results.fetchall()
        self.assertIn(("N",), result_list)
        conn.close()
    def test_process_5assert(self):
        faculty_filter = Faculty_Filter()
        datatmp = school_distribution_data(faculty_filter, DBNAME)
        self.assertTrue(datatmp[0][0] == "Engineering")
        self.assertTrue(datatmp[4][0] == "Information")
        _, _, words_key = keyword_data(faculty_filter, DBNAME)
        self.assertTrue(len(words_key) <= 100)
        faculty_filter.first_flag = True
        faculty_filter.first = "Engineering"
        self.assertTrue(faculty_filter.__str__() == "WHERE Faculties.First_Aff = 'Engineering' ")
        faculty_filter.clear()
        self.assertTrue(faculty_filter.__str__() == "")

unittest.main(verbosity=2)