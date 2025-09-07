def get_config_by_key(config_path, section_name, key):
    '''
        @param {string} config_path 配置文件路径
        @param {string} section_name 配置文件section
        @param {string} key 配置文件key
    '''
    try:
        import configparser
        config = configparser.ConfigParser()
        ENCODING = "utf-8"
        config.read(config_path, encoding=ENCODING)
        config_value = config.get(section_name, key)
        return config_value
    except Exception as e:
        print('get_config_by_key Exception', e)
        return None

def test_get():
    # # 示例用法
    config_path = 'config.ini'
    # key = 'local_update'
    key='local_update'
    section_name = "info"
    config_value = get_config_by_key(config_path, section_name, key)
    print(config_value)


def set_config_by_key(config_path, section_name, key, value):
    '''
        功能：修改配置文件，如果不存在配置文件则新增配置文件
        @param {string} config_path 配置文件路径
        @param {string} section_name 配置文件section
        @param {string} key 配置文件key
        @param {string} value 配置文件value
    '''
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8")
        if section_name not in config.sections():
            config.add_section(section_name)
        config.set(section_name, key, value)
        with open(config_path, 'w') as config_file:
            config.write(config_file)
    except Exception as e:
        print("set_config_by_key Exception", e)

def test_set():
    import configparser
    config_path = 'config.ini'
    section_name = 'info'
    key = 'local_update'
    value = '2023-08-15'
    set_config_by_key(config_path, section_name, key, value)


# 示例用法
# config_path = 'config.ini'
# section_name = 'DATABASE'
# key = 'db_username'
# value = 'john'
# set_config_by_key(config_path, section_name, key, value)


def compare_time(time_str1, time_str2):
    '''
    比较两个时间的大小
    :param time_str1: 时间字符串1
    :param time_str2: 时间字符串2
    :return: 
        1: time_str1 > time_str2; 
        0: time_str1 = time_str2; 
        -1: time_str1 < time_str2
    '''
    from datetime import datetime
    time1 = datetime.strptime(time_str1, '%Y-%m-%d %H:%M:%S')
    time2 = datetime.strptime(time_str2, '%Y-%m-%d %H:%M:%S')
    
    if time1 < time2:
        return -1
    elif time1 > time2:
        return 1
    else:
        return 0

def test_time():
    # 示例用法
    time1 = '2023-08-15 16:30:29'
    time2 = '2023-08-15 16:45:40'

    result = compare_time(time1, time2)
    print(result) # -1


def get_cert_path_old():
    import os.path
    module_path = os.path.split(os.path.realpath(__file__))[0]
    cert1_path = os.path.join(module_path, 'cert/localhost+2.pem')
    cert2_path = os.path.join(module_path, 'cert/private.pem')
    return os.path.join(module_path, [cert1_path, cert2_path])

def get_cert_path():
    import site,os
    files = site.getsitepackages()
    sfile = None
    for file in files:
        if file.endswith("site-packages"):
            sfile = file
            break
    thonnypath = os.path.join(sfile,'thonny')
    cert_path = os.path.join(thonnypath,'cert')
    cert1_path = os.path.join(cert_path, 'localhost+2.pem')
    cert2_path = os.path.join(cert_path, 'private.pem')
    return [cert1_path, cert2_path]

def update_cert(res_obj):

    '''
    '''
    ssl_cert_config = res_obj['data']['ssl_cert']
    remote_update = ssl_cert_config['remote_update']
    config_path = "config.ini" #助手内部的配置文件
    section_name = "cert"
    key = "local_update"
    local_update = get_config_by_key(config_path, section_name, key) or "2023-01-01 00:00:00"
    if compare_time(local_update, remote_update) == -1:
        [localhost, private] = get_cert_path()
        # 更新证书
        ENCODING = "utf-8"
        with open(localhost, "w", encoding=ENCODING) as f:
            f.write(ssl_cert_config['localhost+2'])
        with open(private, "w", encoding=ENCODING) as f:
            f.write(ssl_cert_config['private'])
        # 更新本地更新时间
        set_config_by_key(config_path, section_name, key, remote_update)
    
    pass

def handle_update_cert():
    import requests
    url = 'https://code.xueersi.com/api/python/libs'
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
        try:
            update_cert(res.json())
        except Exception as e:
            print("exception", e)
    else:
        print('请求api失败')


