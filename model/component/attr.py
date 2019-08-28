import torch.nn as nn
import torch
import numpy as np
import torch.nn.functional as F


class AttrSoftLoss(nn.Module):
    """
    soft margin loss for this
    """
    def __init__(self):
        super(AttrSoftLoss, self).__init__()

    def forward(self, x):
        """
        consider attributes as multiple labels
        carry out multi-label classification loss
        :param x: score and attributes
        :return: loss
        """
        scores, attributes = x
        attr_loss = 0.0
        attributes = attributes.float().cuda()
        for i in range(attributes.shape[0]):
            loss_mask = torch.ones(attributes.shape[1]).cuda()
            zeros = (attributes[i, :] == 0).nonzero().cpu().numpy()
            indices = np.random.choice(zeros.squeeze(), int(round(len(zeros) * 0.95)), False)
            loss_mask[indices] = 0
            # print(scores[i].shape)
            attr_loss += F.multilabel_soft_margin_loss(scores[i].unsqueeze(0),
                                                       attributes[i].unsqueeze(0), weight=loss_mask)
        attr_loss /= attributes.shape[0]
        return attr_loss


class AttrClassifier(nn.Module):
    """
    Linear Classifier
    """
    def __init__(self, args):
        super(AttrClassifier, self).__init__()
        self.in_dim = args.feat_dim * args.crop_height * args.crop_width
        for supervision in args.supervision:
            if supervision['name'] == 'attr':
                self.num_class = supervision['other']['num_attr']
                self.orth = supervision['other']['orth']
                self.weight = supervision['weight']
        # self.mid_layer = nn.Linear(self.in_dim, self.in_dim)
        self.classifier = nn.Linear(self.in_dim, self.num_class)
        self.sigmoid = nn.Sigmoid()
        self.loss = AttrSoftLoss()
        self.mode = 'train'

    def diagnosis(self, agg_data):
        x = agg_data['features']
        x = self.classifier(x)
        return x

    def forward(self, agg_data):
        """
        forward pipeline, compute loss function
        :param agg_data: refer to ../base_model.py
        :return: loss, acc
        """
        if self.mode == 'diagnosis':
            return self.diagnosis(agg_data)

        loss_sum = 0
        x = agg_data['features']
        attributes = agg_data['attr']
        feature_num = len(x)
        attributes = attributes[:x.shape[1]].long()
        for j in range(feature_num):
            pred = self.classifier(x[j])
            loss_sum += self.loss([pred, attributes])

        orth_loss = torch.zeros(1).cuda()
        if self.orth > 0:
            for name, param in self.classifier.named_parameters():
                if 'bias' not in name:
                    param_flat = param.view(param.shape[0], -1)
                    sym = torch.mm(param_flat, torch.t(param_flat))
                    sym -= torch.eye(param_flat.shape[0]).cuda()
                    orth_loss += sym.sum()
            orth_loss = orth_loss[0].abs() * self.orth / self.weight

            loss_sum += orth_loss
        return loss_sum
