# -*- coding: utf-8 -*-
"""finetune.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eNsyQrOk0cfyds4QIqPKVOPWFS3WuTNu
"""

from __future__ import print_function, division

import os
import numpy as np
import random

import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim
import torchvision
from torchvision import datasets, models, transforms
from torch.optim import lr_scheduler
import pandas as pd
import matplotlib.pyplot as plt

import time
import copy
import shutil
import re
import PIL

#Mounting Google drive for Colab execution

from google.colab import drive
drive.mount('/content/drive')

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

your_module = drive.CreateFile({'id':'1dBH4qAfLeP5AUbIlLZunJqcBzQ2BOUFF'})
your_module.GetContentFile('util.py')

from util import plot_confusion_matrix

torch.manual_seed(0)
# Define train and test directories
base_dir = '/content/drive/My Drive/dataset/places/'

# Pre-processing the dataset
# Normalize the images
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
# Resize the images
resize = transforms.Resize((224, 224))

transforms = {
'train':transforms.Compose([
        resize,
        transforms.RandomRotation(20, resample=PIL.Image.BILINEAR),
        transforms.ColorJitter(hue=.05, saturation=.05),
        transforms.ToTensor(),
        normalize
]), 
'test': transforms.Compose([
        resize,
        transforms.ToTensor(),
        normalize
]),
}

# Dataset augmentation is not performed on the training images therefore the transform can be common

# Normalize the test set same as training set No need to perform augmentation
#transform_test = transforms.Compose([
#    resize,
#    transforms.ToTensor(),
#    normalize,
#])

# Applying the transforms to the datasets
# trainset = datasets.ImageFolder( os.path.join( base_dir, 'train') , transform_images)
# trainloader = torch.utils.data.DataLoader( trainset , batch_size = 4, shuffle = True, num_workers = 4)
# The shuffle is set to true for the taining images
# testset = datasets.ImageFolder( os.path.join( base_dir, 'test') , transform_images)
# testloader = torch.utils.data.DataLoader( testset , batch_size = 4, shuffle = True, num_workers = 4)

# Use the image folder function to create datasets
dataset = { x: datasets.ImageFolder( os.path.join( base_dir, x ), transforms[x] )for x in ['train', 'test']}

dataloader = { x: torch.utils.data.DataLoader( dataset[x], batch_size = 4, shuffle = True, num_workers = 4) for x in ['train', 'test']}

# Defining the classes
dataset_sizes = { x: len(dataset[x]) for x in ['train', 'test']}
class_names = dataset['train'].classes


print(class_names)

# Number of classes in the dataset
num_classes = 9

# Number of epochs to train for
# num_epochs = 2

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

alexnet = torchvision.models.alexnet(pretrained = True)

#for name, child in alexnet.named_children():
#  print(child)
#  print(name)

alexnet.classifier[6] = nn.Linear(4096,num_classes)
input_size = 224

model = alexnet.to(device)
print(model)

criterion = nn.CrossEntropyLoss()
criterion = criterion.to(device)

# Observe that all parameters are being optimized
optimizer_ft = optim.SGD(model.parameters(), lr=0.001, momentum=0.6)

# Decay LR by a factor of 0.1 every 7 epochs
exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=3, gamma=0.1)

def train_model(model, criterion, optimizer, scheduler, num_epochs):
    since = time.time()
    flag = 0
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'test']:
            if phase == 'train':
                if flag == 1:
                  scheduler.step()
                model.train()  # Set model to training mode
            else:
                model.eval()   # Set model to evaluate mode

            current_loss = 0.0
            current_corrects = 0

            # Here's where the training happens
            print('Iterating through data...')

            for inputs, labels in dataloader[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # We need to zero the gradients, don't forget it
                optimizer.zero_grad()
                flag = 1
                # Time to carry out the forward training pass
                # We only need to log the loss stats if we are in training phase
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # We want variables to hold the loss statistics
                current_loss += loss.item() * inputs.size(0)
                current_corrects += torch.sum(preds == labels.data)

            epoch_loss = current_loss / dataset_sizes[phase]
            epoch_acc = current_corrects.double() / dataset_sizes[phase]

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            # Make a copy of the model if the accuracy on the validation set has improved
            if phase == 'test' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

        print()

    time_since = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_since // 60, time_since % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    # Now we'll load in the best model weights and return it
    model.load_state_dict(best_model_wts)
    return model

def predict_model(model, num_images=6):
    was_training = model.training
    model.eval()
    images_handeled = 0
    fig = plt.figure()

    with torch.no_grad():
        for i, (inputs, labels) in enumerate(dataloader['test']):
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            for j in range(inputs.size()[0]):
                images_handeled += 1
                ax = plt.subplot(num_images//2, 2, images_handeled)
                ax.axis('off')
                ax.set_title('predicted: {}'.format(class_names[preds[j]]))
                imshow(inputs.cpu().data[j])

                if images_handeled == num_images:
                    model.train(mode=was_training)
                    return
        model.train(mode=was_training)

base_model = train_model(model, criterion, optimizer_ft, exp_lr_scheduler, 2)
predict_model(base_model)
plt.show()

model_save_name = 'finemodel.pt'
path = F"/content/drive/My Drive/{model_save_name}" 
torch.save(base_model.state_dict(), path)

confusion_matrix = torch.zeros(num_classes, num_classes)
with torch.no_grad():
    for i, (inputs, classes) in enumerate(dataloaders['test']):
        inputs = inputs.to(device)
        classes = classes.to(device)
        # print(classes)
        outputs = base_model(inputs)
        _, preds = torch.max(outputs, 1)
        # print(preds)
        for t, p in zip(classes.view(-1), preds.view(-1)):
                confusion_matrix[t.long(), p.long()] += 1

print(confusion_matrix)
cm = confusion_matrix.cpu().numpy()
df = pd.DataFrame(cm, index = class_names, columns = class_names)
plt.savefig('conf_finetune.png')
df.style.background_gradient(cmap='Blues')