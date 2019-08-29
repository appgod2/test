import random
import nltk
from nltk.sentiment import SentimentAnalyzer

def train_model(data_list):
        """
        训练模型
        :param industry_name: 行业名称
        """
        # stock_industry = stock_industry_load('./Data/stock_industry.csv')
        # electronic_stocks = data_list
        sentim_analyzer = SentimentAnalyzer()
        stock_days = []
        # for stock in electronic_stocks:
        #     file_name = './Data/%s-%s-%s.csv' % (industry_name, stock[0], stock[1])
        #     stock_data = stock_load(file_name)
        #     stock_days += stock_split(stock_data)
        stock_data = data_list
        stock_days += stock_split(stock_data)

        print(len(stock_days))
        random.shuffle(stock_days)
        train_set_size = int(len(stock_days) * 0.6)
        train_stock = stock_days[:train_set_size]
        test_stock = stock_days[train_set_size:]

        train_set = sentim_analyzer.apply_features(stock_feature(train_stock), True)
        test_set = sentim_analyzer.apply_features(stock_feature(test_stock), True)

        classifier = nltk.NaiveBayesClassifier.train(train_set)
        print(nltk.classify.accuracy(classifier, train_set))
        print(nltk.classify.accuracy(classifier, test_set))

        classifier.show_most_informative_features(20)

def stock_split(data_list, days=5):
        """
        股票数据分割，将某天涨跌情况和前几天数据关联在一起
        :param data_list: 股票数据列表
        :param days: 关联的天数
        :return: [([day1, day2, ...], label), ...]
        """
        stock_days = []
        for n in range(0, len(data_list['close'])-days):
            before_days = []
            for i in range(1, days+1):
                before_days.append(data_list['open'][n + i])
                before_days.append(data_list['high'][n + i])
                before_days.append(data_list['close'][n + i])
                before_days.append(data_list['low'][n + i])
                before_days.append(data_list['close'][n]-data_list['close'][n+i])
                before_days.append((data_list['close'][n]-data_list['close'][n+i])/data_list['close'][n]*100)
            # if data_list['?'][n] > 0.0:
            #     label = '+'
            # else:
            #     label = '-'
            # stock_days.append((before_days, label))
            stock_days.append((before_days, data_list['aaaa'][n]))

        return stock_days

def stock_feature(before_days):
        """
        股票特征提取
        :param before_days: 前几日股票数据
        :return: 股票特征
        """
        features = {}
        for n in range(0, len(before_days)):
            stock = before_days[n]
            open_price = stock[0]
            high_price = stock[1]
            close_price = stock[2]
            low_price = stock[3]
            price_change = stock[4]
            p_change = stock[5]
            features['Day(%d)PriceIncrease' % (n + 1)] = (price_change > 0.0)
            features['Day(%d)High==Open' % (n + 1)] = (high_price == open_price)
            features['Day(%d)High==Close' % (n + 1)] = (high_price == close_price)
            features['Day(%d)Low==Open' % (n + 1)] = (low_price == open_price)
            features['Day(%d)Low==Close' % (n + 1)] = (low_price == close_price)
            features['Day(%d)Close>Open' % (n + 1)] = (close_price > open_price)
            features['Day(%d)PChange' % (n + 1)] = p_change

        return features