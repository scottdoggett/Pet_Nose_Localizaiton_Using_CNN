# For Colab Pruposes
from google.colab import drive
drive.mount('/content/drive')
import sys
sys.path.append('/content/drive/MyDrive/ELEC 475 Lab 2 CO')

import torch
import torch.nn as nn
from torchvision.transforms import v2   # module for image transformations
import torch.optim as optim
import matplotlib.pyplot as plt
import datetime
import argparse
from torchsummary import summary
from model import SnoutNet
from dataset import SnoutNoseDataset, DataLoader

# Added so that I can run the code on PyCharm and Colab
ColabPath = "/content/drive/My Drive/ELEC 475 Lab 2 CO/oxford-iiit-pet-noses/"
HomePath = "/Users/christianlevec/Documents/475 Lab 2/oxford-iiit-pet-noses/"

save_file = 'weights.pth'
n_epochs = 30
batch_size = 256
plot_file = 'plot_file.png'

def train(n_epochs, optimizer, model, loss_fn, train_loader, scheduler, device, save_file=None, plot_file=None):
    print('Training ...')
    model.train()

    losses_train = []
    for epoch in range(1, n_epochs+1):
        print('Epoch ', epoch)
        loss_train = 0.0
        for data in train_loader:
            print('New batch...')
            # The returned value from train_loader is a tuple need to unpack it
            image = data[0]
            label = data[1]
            # Pass dataset to GPU
            image = image.to(device=device)
            label = label.to(device=device)
            outputs = model(image)

            loss = loss_fn(outputs, label)
            optimizer.zero_grad() # Reset gradient each epoch
            loss.backward() # Compute the gradient (vector) through backpropagation and slowly nudge the weights of the weights vector
                            # Goal is to come to a local minima of the cost function in a non-linear way
            optimizer.step() # Apply new weights to the model
            loss_train += loss.item() # Accumulate total training loss as scalar

        # Scheduler adjusts the learning rate after each epoch
        scheduler.step(loss_train)

        # Loss_train holds accumulated loss over all batches in the epoch
        # Compute avg loss per batch then fill new array with these values
        # Used for analysis purposes
        losses_train += [loss_train/len(train_loader)]

        print('{} Epoch {}, Training loss {}'.format(
            datetime.datetime.now(), epoch, loss_train/len(train_loader)))

        if save_file is not None:
            torch.save(model.state_dict(), save_file)

        if plot_file is not None:
            plt.figure(2, figsize=(12, 7))
            plt.clf()
            plt.plot(losses_train, label='train')
            plt.xlabel('epoch')
            plt.ylabel('loss')
            plt.legend(loc=1)
            print('saving ', plot_file)
            plt.savefig(plot_file)

def init_weights(m):
    if type(m) == nn.Linear:
        torch.nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0.01)


def main():
    import torch
    global save_file, n_epochs, batch_size, plot_file

    print('running main ...')

    #   read arguments from command line
    """argParser = argparse.ArgumentParser()
    argParser.add_argument('-s', metavar='state', type=str, help='parameter file (.pth)')
    argParser.add_argument('-e', metavar='epochs', type=int, help='# of epochs [30]')
    argParser.add_argument('-b', metavar='batch size', type=int, help='batch size [32]')
    argParser.add_argument('-p', metavar='plot', type=str, help='output loss plot file (.png)')

    args = argParser.parse_args()

    if args.s != None:
        save_file = args.s
    if args.e != None:
        n_epochs = args.e
    if args.b != None:
        batch_size = args.b
    if args.p != None:
        plot_file = args.p"""

    print('\t\tn epochs = ', n_epochs)
    print('\t\tbatch size = ', batch_size)
    print('\t\tsave file = ', save_file)
    print('\t\tplot file = ', plot_file)

    device = 'cpu'
    if torch.cuda.is_available():
        device = 'cuda'
    print('\t\tusing device ', device)

    model = SnoutNet()
    model.to(device)
    model.apply(init_weights)
    summary(model, input_size=(3, 227, 227), device='cuda') # Manually change to cpu if running on cpu

    transform1 = v2.Compose([
        v2.Resize((227, 227)),  # Resize to desired shape
        v2.ToDtype(torch.float32, scale=True)
    ])

    # Manually change path names if running on cpu
    trainSet = SnoutNoseDataset(ColabPath+"train_noses.txt",
                                ColabPath+"images-original/images",
                                transform=transform1,
                                num_workers=4)

    testSet = SnoutNoseDataset(ColabPath+"test_noses.txt",
                               ColabPath+"images-original/images",
                               transform=transform1,
                               num_workers=4)

    train_dataloader = DataLoader(trainSet, batch_size=batch_size, shuffle=True)  # experiment with batch_size

    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer,'min')
    loss_fn = nn.MSELoss(size_average=None, reduce=None, reduction='mean')

    train(
            n_epochs=n_epochs,
            optimizer=optimizer,
            model=model,
            loss_fn=loss_fn,
            train_loader=train_dataloader,
            scheduler=scheduler,
            device=device,
            save_file=save_file,
            plot_file = plot_file)

###################################################################

if __name__ == '__main__':
    main()