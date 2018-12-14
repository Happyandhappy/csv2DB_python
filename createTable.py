from Model import *
import os, sys, shutil, time
import zipfile
import requests, io, datetime
from config import *
import warnings
warnings.filterwarnings("ignore")
if (sys.argv.__len__() == 1):
        sys.argv.append('-W ignore')

project_path = os.path.dirname(os.path.abspath(__file__))

start = time.time()
def elapsed():
    return time.time() - start

# crete database
def createDB():
    Dbcon = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS)
    query = """CREATE DATABASE IF NOT EXISTS `%s`;""" %(MYSQL_DBNAME)
    dbcur = Dbcon.cursor()
    try:
        dbcur.execute(query)
        Dbcon.commit()
        print("Database %s was created." %(MYSQL_DBNAME))
    except:
        Dbcon.rollback()
        print(query)
        print("SQL statement Error")
    dbcur.close()


# pull zip file from online
def Pull(url):
    r = requests.get(url)
    with open('ipgold-offline.zip', 'wb') as fh:
        fh.write(r.content)

# Extract file from zip to path(directory)
def Unzip(zip, path):
    with zipfile.ZipFile(zip,'r') as zip_ref:
        zip_ref.extractall(path)

# get all file name list in directory
def getCSVfilelist(dir):
    return os.listdir(dir)


"""
    def : SplitCSV
    split big csv to small csv files each has 100000 rows
"""
def splitCSV(filepath):
    ### delete temp files and create new temp files
    dirName = 'temp'
    if os.path.isdir(dirName):
        shutil.rmtree(dirName)
    os.mkdir(dirName)

    names = []
    name = 0
    with open(filepath, "r", encoding='utf-8',) as f:
        file = open(dirName + "/" + str(name), 'a')
        names.append(dirName + "/" + str(name))
        cnt = 0
        for line in f:
            cnt += 1
            file.write(str(line))
            if cnt > 100000:
                cnt = 0
                name += 1
                file.close()
                file = open(dirName + "/" + str(name), 'a')
                names.append(dirName + "/" + str(name))
        file.close()
    return names


# Unit to store splitted file data to mysql
def CSVtoDB_Unit(file, model):
    model.creatTable()
    model.setfilepath(project_path + "/" + file)
    model.importCSV()

# store csv data to mysql
def CSVtoDB(dir,file, model):
    # filepath = project_path + "\{0}\{1}".format(dir, file)
    names = splitCSV("./{0}/{1}".format(dir, file))
    for name in names:
        print(name)
        print('\n%.3fs:' % (elapsed()))
        CSVtoDB_Unit(name, model)
        model.isHeader = False

if __name__ == "__main__":
    print('\n%.3fs:' % (elapsed()))

    # crate db if not exist
    createDB()
    #create directory
    dirName = 'ipgold-offline'
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    print("Start pulling file from website")
    ## pull zip file from url
    # Pull(ZIP_URL)
    print("Finish pulling file from website")
    ## unzip zip file
    zipfileName = "ipgold-offline.zip"
    # print("Extracting %s..." % (zipfileName))
    # Unzip(zipfileName, dirName)
    print("Finish Extracting!")

    print("Start processing!")
    csvlist = getCSVfilelist(dirName) #
    for csvf in csvlist:
        print("Storing {0} to mysql...".format(csvf))
        modelName = csvf.split('.')[0]
        modelName = modelName.lower().replace('ipgold','')
        model = None
        if  '201' in modelName:
            model = IPGOLD201()
        elif '202' in modelName:
            model = IPGOLD202()
        elif '203' in modelName:
            model = IPGOLD203()
        elif '204' in modelName:
            model = IPGOLD204()
        elif '206' in modelName:
            model = IPGOLD206()
        elif '207' in modelName:
            model = IPGOLD207()
        elif '208' in modelName:
            model = IPGOLD208()
        elif '220' in modelName:
            model = IPGOLD220()
        elif '221' in modelName:
            model = IPGOLD221()
        elif '222' in modelName:
            model = IPGOLD222()
        if model != None:
            CSVtoDB(dirName, csvf, model)
    print("End processing!")
    print('\n%.3fs : Total spent time' % (elapsed()))
    if os.path.isdir('temp'):
        shutil.rmtree('temp')
