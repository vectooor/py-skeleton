import os
import configparser

"""
这里通过一个例子来区分RawConfigParser/ConfigParser的区别

配置文件 test.ini
-----------------
[URL] 
url = http://%(host)s:%(port)s/test
host = localhost
port = 8080
-----------------

cf = ConfigParser.RawConfigParser() 
cf.read("test.ini")
cf.set("portal", "fullUrl", "%(host)s:%(port)s")
cf.get("portal", "fullUrl")
Result: %(host)s:%(port)s
-----------------

cf = ConfigParser.ConfigParser() 
cf.read("test.ini")
cf.set("portal", "fullUrl", "%(host)s:%(port)s")
cf.get("portal", "fullUrl")
Result: http://localhost:8080s/test 
-----------------
"""

class UmsConfig(object):
    def __init__(self, config_file='etc/config.ini'):
        self._path = os.path.join(os.getcwd(), config_file)
        if not os.path.exists(self._path):
            raise FileNotFoundError("No such file: config.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding='utf-8-sig')
        # RawConfigParser 就是对占位符不进行处理
        self._configRaw = configparser.RawConfigParser()
        self._configRaw.read(self._path, encoding='utf-8-sig')

    def get(self, section, name):
        return self._config.get(section, name)

    def getRaw(self, section, name):
        return self._configRaw.get(section, name)


globalConfig = UmsConfig()
