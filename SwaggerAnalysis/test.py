

class Analysis(object):
    def __init__(self):
        self.interface_params = {}

    def demo01(self):
        print(self.interface_params)
        self.interface_params = self.demo02()
        print('1111111111111111',self.interface_params)

    def demo02(self):
        print('current:', self.interface_params)
        self.interface_params['aaa'] = 'bbb'
        print('22222222222222', self.interface_params)
        return self.interface_params


if __name__ == '__main__':
    analysis = Analysis()
    analysis.demo01()
    print(analysis.interface_params)
