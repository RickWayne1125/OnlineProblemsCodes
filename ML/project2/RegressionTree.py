import math

import numpy as np
import pandas as pd
import collections
import sklearn.datasets


class node:
    def __init__(self, v=None, l=None, r=None, d=0, label=None, max=None, leaf=0, nh=0, mse=0):
        self.value = v  # 分类参考值
        self.left = l  # 左子节点
        self.right = r  # 右子节点
        self.dimension = d  # 节点代表属性值在数据集中下标
        self.leaf = leaf  # 是否为叶子节点
        self.label = label  # 节点标签值
        self.mse = mse


class Model:
    def __init__(self, x, y):
        self.root = self.buildTree(x, y)

    def getAVG(self, y):
        total = 0
        mse = 0
        for i in range(len(y)):
            total += y[i]
        avg = total / len(y)
        return avg

    def getMSE(self, y):
        mse = 0
        if(len(y)==0):
            return mse
        avg = self.getAVG(y)
        for i in range(len(y)):
            mse += (y[i] - avg) * (y[i] - avg)
        return mse

    def getCutMSE(self, x, y, d):
        mse = -1
        value = 0
        attr = x[:, d]
        # attr = list(set(attr))
        attr = sorted(attr)
        anum = len(attr)
        dnum = len(x[:, d])
        for i in range(anum - 1):
            tmpv = (attr[i] + attr[i + 1]) / 2
            l = [j for j in range(dnum) if x[j, d] <= tmpv]
            r = [j for j in range(dnum) if x[j, d] > tmpv]
            yl = y[l]
            yr = y[r]
            tmpm = self.getMSE(yl) + self.getMSE(yr)
            if (tmpm < mse) or (mse == -1):
                mse = tmpm
                value = tmpv
        return mse, value

    def getAttr(self, x, y):
        mse = -1
        value = 0
        d = 0
        for i in range(len(x[0])):
            tmpm, tmpv = self.getCutMSE(x, y, i)
            if (tmpm < mse) or (mse == -1):
                mse = tmpm
                value = tmpv
                d = i
        return mse, value, d

    def divideTree(self, x, y, v, d):
        attr = x[:, d]
        num = len(x[:, d])
        l = [i for i in range(num) if x[i, d] <= v]
        r = [i for i in range(num) if x[i, d] > v]
        xl = x[l]
        xr = x[r]
        yl = y[l]
        yr = y[r]
        return xl, yl, xr, yr

    def buildTree(self, x, y):
        print('Building Tree...')
        if y.size > 1:
            mse, value, d = self.getAttr(x, y)
            # print('mse:', mse)
            # print('value:', value)
            # print('d', d)
            if mse >= 0:
                xl, yl, xr, yr = self.divideTree(x, y, value, d)
                ltree = self.buildTree(xl, yl)
                rtree = self.buildTree(xr, yr)
                return node(v=value, l=ltree, r=rtree, d=d, mse=mse)
            else:
                return node(label=y[0], leaf=1)
        else:
            label = self.getAVG(y)
            mse = self.getMSE(y)
            return node(label=label, leaf=1, mse=mse)

    def postPruning(self, root, alpha):
        if root.leaf == 0:
            if root.left.leaf == 0:
                self.postPruning(root.left, alpha)
            if root.right.leaf == 0:
                self.postPruning(root.right, alpha)
        if root.left.leaf == 1 and root.right.leaf == 1:
            bef = (root.left.mse + alpha) + (root.right.mse + alpha)
            aft = root.mse + alpha
            print('MSE Bef: ', bef)
            print('MSE Aft: ', aft)
            if bef >= aft:
                root.label = (root.left.label + root.right.label) / 2
                root.left = None
                root.right = None
                root.leaf = 1

    def regression(self, input, root):
        if root.label != None:
            return root.label
        else:
            tmp = input[root.dimension]
            if tmp <= root.value:
                next = root.left
            else:
                next = root.right
            return self.regression(input, next)

    def printTree(self):
        print('Root:')
        print('root: ', self.root.dimension, self.root.value)
        print('left: ', self.root.left.dimension, self.root.left.value)
        print('right: ', self.root.right.dimension, self.root.right.value)

    def getR2(self, pre, real):
        avg = self.getAVG(real)
        SSE = 0
        SST = 0
        SSR = 0
        for i in range(len(real)):
            SSE += (pre[i] - real[i]) ** 2
            SST += (real[i] - avg) ** 2
            SSR += (pre[i] - avg) ** 2
        R2 = 1 - SSE / SST
        return R2


class DataReader:
    def __init__(self):
        self.rawx = None
        self.rawy = None
        self.trainx = None
        self.testx = None
        self.trainy = None
        self.testy = None

    def load_boston(self):
        data = sklearn.datasets.load_boston()
        self.rawx = data.data
        self.rawy = data.target
        self.splitData()

    def load_slump(self):
        data = pd.read_csv('../data/slump_test.csv')
        data = np.array(data)
        self.rawx=data[:,1:10]
        self.rawy=data[:,10]
        self.splitData()

    def splitData(self):
        permutation = np.random.permutation(self.rawx.shape[0])
        shuffled_dataset = self.rawx[permutation, :]
        shuffled_labels = self.rawy[permutation]
        tlen = int(len(shuffled_labels) * 2 / 3)
        # print('Size of Test Datasets:', tlen)
        dlen = len(shuffled_labels)
        self.trainx = shuffled_dataset[:tlen, :]
        self.trainy = shuffled_labels[:tlen]
        self.testx = shuffled_dataset[tlen:dlen, :]
        self.testy = shuffled_labels[tlen:dlen]

    def getTrainData(self):
        return self.trainx, self.trainy

    def getTestData(self):
        return self.testx, self.testy


if __name__ == '__main__':
    dr = DataReader()
    dr.load_slump()
    dr.load_boston()
    train_data, train_label = dr.getTrainData()
    test_data, test_label = dr.getTestData()
    model = Model(train_data, train_label)

    true_count = 0
    pre = []
    for i in range(len(test_label)):
        predict = model.regression(test_data[i], model.root)
        pre.append(predict)
        print('Prediction: ', predict, 'Real: ', test_label[i])
    model.printTree()
    print('R2:', model.getR2(pre, test_label))

    root = model.root
    model.postPruning(root, 2)
    pre = []
    for i in range(len(test_label)):
        predict = model.regression(test_data[i], root)
        pre.append(predict)
        print('Prediction: ', predict, 'Real: ', test_label[i])
    print('R2:', model.getR2(pre, test_label))
