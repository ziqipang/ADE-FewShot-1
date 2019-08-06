import torch
import torch.nn as nn
import torch.nn.functional as F
from roi_align.roi_align import RoIAlign
from torch.autograd import Variable
import numpy as np


def to_variable(arr, requires_grad=False, is_cuda=True):
    tensor = torch.from_numpy(arr)
    if is_cuda:
        tensor = tensor.cuda()
    var = Variable(tensor, requires_grad=requires_grad)
    return var


class FC_Classifier(nn.Module):
    def __init__(self, args, in_dim):
        super(FC_Classifier, self).__init__()
        self.crop_height = int(args.crop_height)
        self.crop_width = args.crop_width
        self.roi_align = RoIAlign(args.crop_height, args.crop_width, transform_fpcoor=True)
        self.num_class = args.num_class
        self.down_sampling_rate = args.down_sampling_rate
        self.in_dim = in_dim
        self.fc1 = nn.Linear(in_dim * self.crop_width * self.crop_height, self.num_class)
        self.type = 'fc_cls'
        self.output = 'dumb'

    def forward(self, x):
        feature_map, scale, anchors, anchor_num = x
        anchors = np.array(anchors.detach().cpu())
        scale = np.array(scale.detach().cpu())
        anchors = anchors / self.down_sampling_rate
        anchor_num = int(anchor_num)
        anchors[:, 2] = anchors[:, 2] * scale[0]
        anchors[:, 3] = anchors[:, 3] * scale[0]
        anchors[:, 0] = anchors[:, 0] * scale[1]
        anchors[:, 1] = anchors[:, 1] * scale[1]
        anchors[:, [1, 2]] = anchors[:, [2, 1]]
        anchor_index = np.zeros(anchor_num)
        anchor_index = to_variable(anchor_index).int()
        anchors = to_variable(anchors[:anchor_num, :]).float()
        pred = torch.zeros(anchor_num, self.num_class)
        feature_map = feature_map.unsqueeze(0)
        # print('feature map size {}'.format(feature_map.shape))
        feature = self.roi_align(feature_map, anchors, anchor_index)
        # print('Feature size is {}'.format(feature.shape))

        if self.output == 'feat':
            return feature

        feature = feature.view(-1, self.in_dim * self.crop_height * self.crop_width)
        # print('Feature shape after view is {}'.format(feature.shape))
        pred = self.fc1(feature)
        if self.output == 'pred':
            return pred
        # print('pred shape {}\n'.format(pred.shape))
        anchor_index.detach()
        anchors.detach()
        del anchor_index, anchors
        return pred, feature


class Novel_Classifier(nn.Module):
    def __init__(self, in_dim, num_class):
        super(Novel_Classifier, self).__init__()
        self.fc1 = nn.Linear(in_dim, num_class)
        self.type = 'fc_cls'

    def forward(self, x):
        x = self.fc1(x)
        return x

    def _acc(self, pred, label, output='dumb'):
        _, preds = torch.max(pred, dim=1)
        valid = (label >= 0).long()
        acc_sum = torch.sum(valid * (preds == label).long())
        instance_sum = torch.sum(valid)
        acc = acc_sum.float() / (instance_sum.float() + 1e-10)
        if output == 'dumb':
            return acc
        elif output == 'vis':
            return acc, pred, label
