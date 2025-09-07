# 特殊配置代码列表，每个字典中包含检测字段 check_code 和 新增代码 add_code
SPECIAL_MAP_ARR = [
    {
        'check_code': 'pgzrun',
        'add_code': '''from pgzero.actor import Actor
from pgzero.rect import Rect
from pgzero.loaders import sounds, images
from pgzero import music, tone
from pgzero.clock import clock
from pgzero.builtins import keymods  # 似乎没有作用
from pgzero.constants import mouse
from pgzero.animation import animate
from pgzero.keyboard import keys, Keyboard, keyboard
from pgzero.screen import Screen, screen
keyboard: Keyboard  # 类型标注
screen: Screen  # 类型标注
'''},
    {
        'check_code': 'df.',
        'add_code': '''import pandas
df:pandas.DataFrame
'''}]

preload_arr = [
    {
        "source": '''import pandas
pandas.''',
        "row": 2,
        "column": 7
    },
    {
        "source": '''import sklearn
sklearn.''',
        "row": 2,
        "column": 8
    },
    {
        "source": '''import numpy
numpy.''',
        "row": 2,
        "column": 6
    }
]

# 补全请求超时限制
OUT_TIME_SECONDS = 10
# 补全黑名单，相应字符后不补全,中文字符
BLACK_LIST = ["！", "$", "￥", "（", "）",")", "-", "【", "】", "、", ":",";","；", "’", ",", "《", "，","。", "》", "？"]
EMPTY_SOURCE = ("a=1", 1, 3) #这种情况下获得的补全为空
from xesrepair.complete_template import TEMPLATE_LIST


class completeFilter:
    def __init__(self):
        pass

    def set_jedi_config(self):
        import jedi
        # jedi.settings.auto_import_modules = ['gi']
        jedi.inference.recursion.recursion_limit = 4
        jedi.inference.recursion.total_function_execution_limit = 6
        jedi.inference.recursion.per_function_execution_limit = 3
        jedi.inference.recursion.per_function_recursion_limit = 2
        # 设置加括号未生效
        # jedi.settings.add_bracket_after_function = True

    def before(self, source, row, column):
        '''
        :功能：对补全代码做前置处理
        :param special_map_arr: 特殊代码匹配的数组
        :param source: 要检测的代码
        :param row: 待补全位置所在行数
        :param column: 当前行待补全位置前的字符个数
        :return 检测特殊代码后重新返回新参数
        '''
        # 1、检测补全位置前是否是黑名单字符
        source, row, column = self.filter_black_char(source, row,column)

        # 2.添加导库语句
        for smap in SPECIAL_MAP_ARR:
            if smap['check_code'] in source:
                source = smap['add_code'] + source
                add_rows = smap['add_code'].count('\n')
                return (source, row+add_rows, column)
        
        return (source, row, column)
    
    def filter_black_char(self,source, row, column):
        '''
        过滤黑名单字符
        '''
        lines = source.split("\n")
        prev_char = lines[row-1][column-1]
        if prev_char in BLACK_LIST:
            return EMPTY_SOURCE
        return source, row, column
    def handle_template(self, source):
        '''
        处理模板
        :return 是否存在模板代码
        '''
        last_line = source.split("\n")[-1]
        for template in TEMPLATE_LIST:
            if last_line == template["keyword"]:
                return [
                    {
                        "meta": "code_block",
                        "caption": template["keyword"],
                        "score": 0,
                        "lang": "python",
                        "value":template["code_block"]
                    }
                ] 
        return None

    def after(self, origin_data, source, row, column):
        '''
        :功能：对补全代码提示做后置处理
        :param origin_data: 初步获得的代码提示数组
        :return 处理过的前端提示
        '''
        template_intelligence = self.handle_template(source)
        if template_intelligence != None:
            return template_intelligence
        target_data = []
        max_index = len(origin_data) - 1
        has_brackets_flag = self.has_brackets(source, row, column)
        for n in origin_data:
            # 如果值的首尾有引号，但是首尾不匹配，那么去掉首尾的引号
            name = n["name"]
            max_index = len(name)-1
            quotation_arr = ['"',  "'"]
            if (name[0] in quotation_arr or name[len(name)-1] in quotation_arr) and name[max_index] != name[0]:
                name = name.strip('"').strip("'")
            if n["type"] == "function" and has_brackets_flag:
                name = name+"()"
            i = {
                "meta": n["type"],
                "caption": name,
                "value": name,
                "score": 0,
                "lang": "python"
            }
            target_data.append(i)
        # 对默认情况不处理
        return target_data
    def has_brackets(self, source, row, column):
        '''判断函数是否加括号
        :retutn bool 是否加括号
        '''
        lines = source.split("\n")
        line = lines[row-1]
        right = line[column:]
        right = right.strip()
        return not right.startswith('(') 


# 用作单例
completeFilterObj = completeFilter()
