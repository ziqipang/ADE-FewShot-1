import torch
import torch.nn as nn
import numpy as np


class NovelClassifier(nn.Module):
    def __init__(self, args):
        super(NovelClassifier, self).__init__()
        self.in_dim = args.crop_height * args.crop_width * args.feat_dim
        self.num_class = args.num_class
        self.fc = nn.Linear(self.in_dim, self.num_class)
        self.range_of_compute = args.range_of_compute
        self.loss = nn.CrossEntropyLoss(ignore_index=-1)
        self.mode = 'train'

    def predict(self, x):
        feature = x['feature']
        label = x['label'].long()
        pred = self.fc(feature)
        return self.acc(pred, label)

    def forward(self, x):
        if self.mode == 'val':
            return self.predict(x)

        feature = x['feature']
        label = x['label'].long()
        pred = self.fc(feature)
        loss = self.loss(pred, label)
        acc = self._acc(pred, label)
        return loss, acc

    def _acc(self, pred, label):
        _, preds = torch.max(pred, dim=1)
        valid = (label >= 0).long()
        acc_sum = torch.sum(valid * (preds == label).long())
        instance_sum = torch.sum(valid)
        acc = acc_sum.float() / (instance_sum.float() + 1e-10)
        return acc

    def acc(self, pred, label):
        acc_sum = 0
        num = pred.shape[0]
        preds = np.array(pred.detach().cpu())
        preds = np.argsort(preds)
        label = np.array(label.detach().cpu())
        for i in range(num):
            if label[i] in preds[i, -self.range_of_compute:]:
                acc_sum += 1
        acc = torch.tensor(acc_sum / (num + 1e-10)).cuda()
        return acc