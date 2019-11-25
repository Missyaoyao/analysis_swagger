import json
import xlrd
import xlwt
from xlutils.copy import copy

import os

def write_data(data, file_name):
    """写入json文件"""
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


class Write_excel(object):
    def __init__(self, filename, title):
        self.filename = filename + title + '.xls'  # 路径+文件名
        print("excel文件名：", self.filename)

    def create_excelFile(self):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('接口测试用例')
        sheet_title = [['id','tags','name','method','url','params','headers','body','body_type','type'],]

        # 设置颜色
        # style = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue')
        # 字体加粗
        # style = xlwt.easyxf('font: bold on')
        # 样式合并
        style = xlwt.easyxf('pattern: pattern solid, fore_colour red; font: bold on')

        for j in range(len(sheet_title[0])):
                sheet.write(0,j,sheet_title[0][j], style)

        workbook.save(self.filename)
        print("创建excel 完成！")

    def write(self, hang, lie, data):
        # hang数 获取需要写入数据的行数
        workbook = xlrd.open_workbook(self.filename)  # 打开工作簿
        sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
        worksheet = workbook.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格
        rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
        new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
        new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格

        # for i in range(0, index):
        #     for j in range(0, len(value[i])):
        #         new_worksheet.write(i + rows_old, j, value[i][j])  # 追加写入数据，注意是从i+rows_old行开始写入

        new_worksheet.write(hang, lie-1, data)  # (这里进行了修改)追加写入数据，注意是从i+rows_old行开始写入
        new_workbook.save(self.filename)  # 保存工作簿
        print("xls格式表格【追加】写入数据成功！")


if __name__ == '__main__':
    excel_path = os.path.dirname(__file__) +'\\report\\'
    wt = Write_excel(excel_path, '生鲜柜业务')
    wt.create_excelFile()
