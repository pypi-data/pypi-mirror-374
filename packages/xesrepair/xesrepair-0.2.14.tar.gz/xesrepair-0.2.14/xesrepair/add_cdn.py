def concatCdns(cdn_lst, seperator):
    '''
        :功能：根据字符串列表，返回拼接后的字符串
        :param cdn_lst: 字符串列表
        :return ret_str: 返回的字符串去除首位空白字符
    '''
    all_cdn_str = ""

    for cdn in cdn_lst:
        all_cdn_str = all_cdn_str + cdn + seperator
    ret_str = all_cdn_str.strip()  # 去除最后的换行
    return ret_str


def addCdns(config_path="config.ini"):
    '''
        :功能：添加cdn到助手的配置文件中
        :param cdn_lst: 字符串列表
        :return ret_str: 返回的字符串去除首位空白字符
    '''
    import configparser
    cf = configparser.ConfigParser()
    ENCODING = "utf-8"
    cf.read(config_path, encoding=ENCODING)
    # 先读取现在的cdn
    cur_cdns = cf["cdns"]["online"]
    needWrite = False
    if cur_cdns == None or cur_cdns.strip() == "":
        # 添加线上环境的cdn
        online_cdn_arr = []
        for i in range(0, 11):
            cdn = 'https://static{}.xesimg.com'.format(i)
            online_cdn_arr.append(cdn)
        online_cdn_str = concatCdns(online_cdn_arr, ",\n")
        cf['cdns']['online'] = online_cdn_str + cf['cdns']['online']
        cf.set('cdns', 'online', cf['cdns']['online'])
        needWrite = True
    
    test_cdns = cf["cdns"]["test"]
    if test_cdns == None or test_cdns.strip() == "":
        # 添加测试环境的cdn
        test_cdn_arr = ['https://static0-test.xesimg.com']
        test_cdn_str = concatCdns(test_cdn_arr, ",\n")
        cf['cdns']['test'] = test_cdn_str + cf['cdns']['test']
        needWrite = True
    
    if needWrite:
        cf.write(open(config_path, "w"))

def addCdnsFn():
    try:
        import platform
        import os.path
        import sys
        filename = "config.ini"
        if platform.system() == "Windows":
            config_path = filename
        else:
            config_path = os.path.join(sys.exec_prefix, "bin", filename)
        addCdns(config_path)
    except Exception as e:
        print(e)
