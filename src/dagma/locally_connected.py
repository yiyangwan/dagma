import torch
import torch.nn as nn
import math


class LocallyConnected(nn.Module):

    def __init__(self, num_linear: int, input_features: int, output_features: int, bias: bool = True):
        r"""
        Local linear layer, i.e. Conv1dLocal() with filter size 1.

        Parameters
        ----------
        num_linear : int
            num of local linear layers, i.e.
        input_features : int
            m1
        output_features : int
            m2
        bias : bool, optional
            Whether to include bias or not. Default: ``True``.
        
        Shape
        -----
        input : [n, d, m1]
        output : [n, d, m2]

        Attributes
        ----------
        weight: [d, m1, m2]
        bias: [d, m2]
        """
        super(LocallyConnected, self).__init__()
        self.num_linear = num_linear
        self.input_features = input_features
        self.output_features = output_features

        self.weight = nn.Parameter(torch.Tensor(num_linear,
                                                input_features,
                                                output_features))
        if bias:
            self.bias = nn.Parameter(torch.Tensor(num_linear, output_features))
        else:
            # You should always register all possible parameters, but the
            # optional ones can be None if you want.
            self.register_parameter('bias', None)

        self.reset_parameters()

    @torch.no_grad()
    def reset_parameters(self):
        k = 1.0 / self.input_features
        bound = math.sqrt(k)
        nn.init.uniform_(self.weight, -bound, bound)
        if self.bias is not None:
            nn.init.uniform_(self.bias, -bound, bound)

    def forward(self, input: torch.Tensor):
        # [n, d, 1, m2] = [n, d, 1, m1] @ [1, d, m1, m2]
        out = torch.matmul(input.unsqueeze(dim=2), self.weight.unsqueeze(dim=0))
        out = out.squeeze(dim=2)
        if self.bias is not None:
            # [n, d, m2] += [d, m2]
            out += self.bias
        return out

    def extra_repr(self):
        # (Optional)Set the extra information about this module. You can test
        # it by printing an object of this class.
        return 'num_linear={}, in_features={}, out_features={}, bias={}'.format(
            self.num_linear, self.in_features, self.out_features,
            self.bias is not None
        )

