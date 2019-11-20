# Source: https://github.com/pytorch/tutorials/blob/master/beginner_source/chatbot_tutorial.py

import torch

def get_device():
    USE_CUDA = torch.cuda.is_available()
    return torch.device("cuda" if USE_CUDA else "cpu")