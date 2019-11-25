import sys
import os


import requests
from SwaggerAnalysis.common import write_data, Write_excel


title_list = []


class AnalysisJson(object):
    """swagger自动生成测试用例"""

    def __init__(self, url_json):
        self.url_json = url_json
        print(self.url_json)
        r = requests.get(self.url_json + '/v2/api-docs').json()
        self.title = r['info']['title']
        print(r)
        print('标题', self.title)
        write_data(r, '{}.json'.format(self.title))  # swagger 接口完整大文件写入title.json 文件中保存
        self.interface_params = {}  # 初始化接口参数空字典

        self.row = 2  # 写入excel起始行数
        self.num = 1  # 初始化case id
        global title_list, json_path
        if self.check_data(r):
            self.json_path = os.path.abspath(
                os.path.dirname(
                    os.path.dirname(__file__))) + '\\SwaggerAnalysis' + '\\report' + '\\{}_data.json'.format(
                self.title)  # json file path，
            # 执行多个url的情况，区分生成的json文件
            self.data = r['paths']  # paths中的数据是有用的

            title_list.append(self.title)

            # 创建excel 文件
            self.excel_path = os.path.dirname(__file__) + '\\report\\'
            wt = Write_excel(self.excel_path, self.title)
            wt.create_excelFile()

        else:
            print("swagger 请求错误，请检查swagger 地址，联系管理员！")


    def check_data(self, r):
        """检查返回的数据是否是dict"""
        if not isinstance(r, dict):
            return False
        else:
            return True

    def retrieve_data(self):
        """主函数"""
        global body_name, method, headers
        for k, v in self.data.items():  # k: /接口地址
            method_list = []
            for _k, _v in v.items():  # _k: 请求方式
                interface = {}  # 初始化

                if _v['consumes']:  # 接口是否被弃用
                    method_list.append(_k)
                    api = k  # api地址
                    if len(method_list) > 1:  # api地址下的请求方式不止一个的情况
                        for i in range(len(method_list)):
                            body_name = api.replace('/', '_') + '_' * i  # json文件对应参数名称，excel中body名称
                            method = method_list[-1]  # 请求方式 同一个api地址，不同请求方式
                    else:  # 第一次内循环
                        body_name = api.replace('/', '_')
                        method = _k

                    self.interface_params = self.retrieve_excel(_v, interface, api)  # 写入excel，
                else:
                    print("接口已经被弃用，请联系开发！")
                    break
        if self.interface_params:

            write_data(self.interface_params, self.json_path)  # 参数写入json文件

    def retrieve_excel(self, _v, interface, api):
        """解析参数，拼接为dict--准备完成写入excel的数据"""
        parameters = _v.get('parameters')  # 未解析的参数字典
        if not parameters:  # 确保参数字典存在
            parameters = {}
        case_name = _v['summary']  # 接口名称
        tags = _v['tags'][0]  # 标签名称（属于当前fcb模块中的哪个功能小模块）
        comsumes = _v['consumes'][0]

        query_body_data = self.retrieve_params(parameters)
        params_dict = query_body_data['query']  # 处理接口参数，拼成dict形式query 参数
        body_dict = query_body_data['body']  # body 参数
        path_dict = query_body_data['path']  # 请求路径中{}中的参数
        formData_dict = query_body_data['formData']  # 请求路径中{}中的参数

        headers_name_list = self.retrieve_headers(parameters)  # 新增处理接口参数中的headers,拼成dict形式
        if len(headers_name_list) == 1:  # 只有Authorization这个请求头
            headers_name = headers_name_list[0]['headers']
        else:
            headers_name = ""
            for each in headers_name_list:
                headers_name += each['headers'] + ','

        # json 文件准备： self.interface_params
        self.interface_params[body_name] = {"query": params_dict,
                                            "body": body_dict,
                                            "path": path_dict,
                                            "formData": formData_dict
                                            }
        # 一个为空的情况（4）
        #  params_dict, body_dict, path_dict, formData_dict
        if params_dict == {} and body_dict != {} and path_dict != {} and formData_dict != {}:
            del self.interface_params[body_name]['query']
        elif body_dict == {} and params_dict != {} and path_dict != {} and formData_dict != {}:
            del self.interface_params[body_name]['body']
        elif path_dict == {} and body_dict != {} and params_dict != {} and formData_dict != {}:
            del self.interface_params[body_name]['formData']
        elif formData_dict == {} and body_dict != {} and params_dict != {} and path_dict != {}:
            del self.interface_params[body_name]['path']
        # 两个为空的情况 （6）
        # params_dict & body_dict,
        # body_dict & path_dict,
        # path_dict & formData_dict,
        # formData_dict & params_dict ，
        # body_dict & formData_dict，
        # path_dict & params_dict
        elif params_dict == {} and body_dict == {} and path_dict != {} and formData_dict != {}:
            del self.interface_params[body_name]['query']
            del self.interface_params[body_name]['body']
        elif body_dict == {} and path_dict == {} and params_dict != {} and formData_dict != {}:
            del self.interface_params[body_name]['body']
            del self.interface_params[body_name]['path']
        elif path_dict == {} and params_dict == {} and body_dict != {} and formData_dict != {}:
            del self.interface_params[body_name]['path']
            del self.interface_params[body_name]['query']
        elif path_dict == {} and formData_dict == {} and body_dict != {} and params_dict != {}:
            del self.interface_params[body_name]['path']
            del self.interface_params[body_name]['formData']
        elif formData_dict == {} and body_dict == {} and path_dict != {} and params_dict != {}:
            del self.interface_params[body_name]['formData']
            del self.interface_params[body_name]['body']
        elif params_dict == {} and formData_dict == {} and body_dict != {} and formData_dict != {}:
            del self.interface_params[body_name]['formData']
            del self.interface_params[body_name]['query']
        # 三个为空的情况 （3）
        # params_dict & body_dict & path_dict,
        # formData_dict & body_dict & path_dict
        # params_dict & formData_dict & path_dict
        elif params_dict == {} and path_dict == {} and body_dict == {} and formData_dict != {}:
            del self.interface_params[body_name]['body']
            del self.interface_params[body_name]['query']
            del self.interface_params[body_name]['path']
        elif formData_dict == {} and path_dict == {} and body_dict == {} and params_dict != {}:
            del self.interface_params[body_name]['formData']
            del self.interface_params[body_name]['path']
            del self.interface_params[body_name]['body']
        elif formData_dict == {} and path_dict == {} and params_dict == {} and body_dict != {}:
            del self.interface_params[body_name]['formData']
            del self.interface_params[body_name]['path']
            del self.interface_params[body_name]['query']
        elif formData_dict == {} and body_dict == {} and params_dict == {} and path_dict != {}:
            del self.interface_params[body_name]['formData']
            del self.interface_params[body_name]['body']
            del self.interface_params[body_name]['query']
        # 四个全部为空（1）
        elif path_dict == {} and params_dict == {} and body_dict == {} and formData_dict == {}:
            self.interface_params[body_name] = {"tips": "无任何参数"}

        if params_dict and parameters != {}:  # 单个或多个参数
            interface['row_num'] = self.row  # 写入excel时的所在行
            interface['id'] = 'test_' + str(self.num)  # case id
            interface['tags'] = tags  # 标签名称
            interface['name'] = case_name
            _type = 'json'  # 参数获取方式
            interface['method'] = method  # 请求方式
            interface['url'] = self.url_json + api  # 拼接完成接口url
            interface['headers'] = headers_name  # 是否传header
            interface['body'] = body_name
            interface['type'] = _type
            interface['body_type'] = comsumes
            self.num += 1
            self.row += 1
            # self.interface_params[body_name] = {"query": params_dict,
            #                                     "body": body_dict,
            #                                     "path": path_dict
            #                                     }
            print("传入excel的数据:", interface)
            self.write_excel(interface, self.excel_path)  # 参数写入excel
        else:  # 没有参数
            _type = 'data_old'
            interface['name'] = case_name
            interface['row_num'] = self.row
            interface['id'] = 'test_' + str(self.num)
            interface['tags'] = tags
            interface['method'] = method
            interface['url'] = self.url_json + api
            interface['headers'] = headers_name
            interface['body'] = body_name
            interface['body_type'] = comsumes
            interface['type'] = _type
            self.num += 1
            self.row += 1
            # self.interface_params[body_name] = {"query": params_dict,
            #                                     "body": body_dict,
            #                                     "path": path_dict
            #                                     }
            self.write_excel(interface, self.excel_path)  # 参数写入Excel表中
        return self.interface_params

    def retrieve_params(self, parameters):
        """处理参数，转为dict"""
        params_all = ''
        _in = ''

        for each in parameters:
            _in += each.get('in') + '\n'  # 参数传递位置
            params_all += each.get('name') + '\n'  # 参数

        _in = _in.strip('\n')
        _in_list = _in.split('\n')
        params_all = params_all.strip('\n')
        params_all_list = params_all.split('\n')
        query_list = []
        body_list = []
        path_list = []
        formData_list = []
        for i in range(len(_in_list)):
            if _in_list[i] == 'query':
                query_list.append(params_all_list[i])
            elif _in_list[i] == 'body':
                body_list.append(params_all_list[i])
            elif _in_list[i] == 'path':
                path_list.append(params_all_list[i])
            elif _in_list[i] == 'formData':
                formData_list.append(params_all_list[i])
        test_query_list = query_list.copy()
        query_dict = dict(zip(query_list, test_query_list))  # 把list转为dict
        test_body_list = body_list.copy()
        body_dict = dict(zip(body_list, test_body_list))  # 把list转为dict
        test_path_list = path_list.copy()
        path_dict = dict(zip(path_list, test_path_list))  # 把list转为dict
        test_formData_list = formData_list.copy()
        formData_dict = dict(zip(formData_list, test_formData_list))  # 把list转为dict
        params_dict = {
            "query": query_dict,
            "body": body_dict,
            "path": path_dict,
            "formData": formData_dict
        }
        print('========', params_dict)
        return params_dict

    def retrieve_headers(self, paramters):
        _in = ''
        _name = ''
        headers_name_list = []
        for each in paramters:
            _in += each.get('in') + '\n'  # 参数传递位置
            _name += each.get('name') + '\n'
        _in = _in.strip('\n')
        _in_list = _in.split('\n')
        _name = _name.strip('\n')
        _name_list = _name.split('\n')
        for i in range(len(_in_list)):
            if _in_list[i] == 'header':
                headers_name_list.append({'headers': _name_list[i]})
        return headers_name_list

    def write_excel(self, interface, filename):
        """把dict中的值写入对应的excel行中"""
        wt = Write_excel(filename, self.title)
        try:
            wt.write(interface['row_num'], 1, interface['id'])
            wt.write(interface['row_num'], 2, interface['tags'])
            wt.write(interface['row_num'], 3, interface['name'])
            wt.write(interface['row_num'], 4, interface['method'])
            wt.write(interface['row_num'], 5, interface['url'])
            wt.write(interface['row_num'], 7, interface['headers'])
            wt.write(interface['row_num'], 8, interface['body'])
            wt.write(interface['row_num'], 9, interface['body_type'])
            wt.write(interface['row_num'], 10, interface['type'])
            print("数据写入excle成功！")
        except Exception as e:
            print("出错了，请联系管理元")
            return


if __name__ == '__main__':
    AnalysisJson("http://XXX").retrieve_data()
