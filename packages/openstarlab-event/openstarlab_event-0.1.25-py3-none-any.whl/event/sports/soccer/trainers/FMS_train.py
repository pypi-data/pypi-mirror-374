import torch
import numpy as np
from ..utils.FMS_cost_function import FMS_cost_function
import torchprofile
import warnings
import pdb

def FMS_epoch_function(model, dataloader, min_dict, max_dict, optimizer, device, train=True, print_freq=10,config=None):
    """
    Function to run one epoch of training or evaluation.
    
    Parameters:
    - model: The neural network model.
    - dataloader: DataLoader for the dataset.
    - optimizer: Optimizer for training (if train=True).
    - train: Boolean, True for training, False for evaluation.
    - print_freq: Frequency of printing the loss.

    Returns:
    - Average loss for the epoch.
    """
    if train:
        model.train()
    else:
        model.eval()

    total_loss = 0
    total_loss_components = [0]*9
    total_batches = len(dataloader)
    
    for i, (inputs, gt, _) in enumerate(dataloader):
        
        inputs, gt = inputs.to(device), gt.to(device)
        
        optimizer.zero_grad() if train else None

        # Forward pass
        outputs = model(inputs)
    
        loss, loss_components= FMS_cost_function(gt, outputs,  min_dict=min_dict, max_dict=max_dict, device=device,config=config)

        if train:
            # Backward pass and optimization
            loss.backward()
            optimizer.step()

        total_loss += loss.item()
        #detach the loss components
        loss_components = [i.cpu().detach().numpy() for i in loss_components] if device != "cpu" else [i.detach().numpy() for i in loss_components]
        total_loss_components = [total_loss_components[j] + loss_components[j] for j in range(len(loss_components))]

        if (i + 1) % print_freq == 0 or (i + 1) == total_batches:

            average_loss = total_loss / (i + 1)
            average_loss_components = [total_loss_components[j] / (i + 1) for j in range(len(loss_components))]
            
            print(f"Batch [{i + 1}/{total_batches}] | Loss: {average_loss:.4f} | "
                    f"CEL_action: {average_loss_components[0]:.4f} | CEL_deltaT: {average_loss_components[1]:.4f} | "
                    f"CEL_start_x: {average_loss_components[2]:.4f} | CEL_start_y: {average_loss_components[3]:.4f} | "
                    f"ACC_action: {average_loss_components[4]:.4f} | "
                    f"F1_action: {average_loss_components[5]:.4f} | "
                    f"MAE_deltaT: {average_loss_components[6]:.4f} | MAE_x: {average_loss_components[7]:.4f} | "
                    f"MAE_y: {average_loss_components[8]:.4f}")

    average_loss = total_loss / total_batches

    if train:
        return average_loss, average_loss_components, model.state_dict()
    else:
        return average_loss, average_loss_components

def FMS_train(model, train_loader, valid_loader, min_dict, max_dict, optimizer, device, epochs=10, print_freq=10, patience=5,config=None):
    """
    Function to train the model with both training and validation datasets, with early stopping.

    Parameters:
    - model: The neural network model.
    - train_loader: DataLoader for the training dataset.
    - valid_loader: DataLoader for the validation dataset.
    - mean_dict: Dictionary for the mean of each feature.
    - std_dict: Dictionary for the standard deviation of each feature.
    - optimizer: Optimizer for training.
    - epochs: Number of epochs to train.
    - print_freq: Frequency of printing the loss during training.
    - patience: Number of epochs with no improvement after which training will be stopped.

    Returns:
    - model: The trained model.
    - train_losses: List of training losses for each epoch.
    - valid_losses: List of validation losses for each epoch.
    - train_loss_components: List of training loss components for each epoch.
    - valid_loss_components: List of validation loss components for each epoch.
    """
    torch.cuda.empty_cache(); import gc; gc.collect()
    train_losses = []
    valid_losses = []
    train_loss_components = []
    valid_loss_components = []

    best_valid_loss = float('inf')
    epochs_no_improve = 0
    best_epoch = 0

    for epoch in range(epochs):
        torch.cuda.empty_cache(); import gc; gc.collect()
        print(f"Epoch [{epoch + 1}/{epochs}]")

        # Training phase
        train_loss, average_loss_components, model_state_dict = FMS_epoch_function(model, train_loader, min_dict, max_dict, optimizer, device, train=True, print_freq=print_freq,config=config)
        train_losses.append(train_loss)
        train_loss_components.append(average_loss_components)
        print(f"Training Loss: {train_loss:.4f}")

        # Validation phase
        with torch.no_grad():
            torch.cuda.empty_cache(); import gc; gc.collect()
            valid_loss, average_loss_components = FMS_epoch_function(model, valid_loader, min_dict, max_dict, optimizer=None, device=device, train=False, print_freq=print_freq,config=config)
        valid_losses.append(valid_loss)
        valid_loss_components.append(average_loss_components)
        print(f"Validation Loss: {valid_loss:.4f}\n")

        # Check if validation loss improved
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            best_model = model_state_dict
            best_epoch = epoch
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1

        # Early stopping
        if epochs_no_improve >= patience:
            print(f"Early stopping triggered after {epoch + 1} epochs.")
            model_state_dict = best_model if best_model else model.state_dict()
            epoch = best_epoch
            break

    #Print the best epoch, the best validation loss and the corresponding training loss
    print(f"Best epoch: {best_epoch + 1} | Best validation loss: {best_valid_loss:.4f} | Corresponding training loss: {train_losses[best_epoch]:.4f}")

    warnings.filterwarnings("ignore", message="No handlers found: .*")
    def get_flops(model, dataloader, device='cpu'):
        # Move model to the specified device
        model.to(device)
        
        # Get a batch of data from the DataLoader and move it to the same device
        inputs, _, _ = next(iter(dataloader))
        inputs = inputs.to(device)
        
        # Ensure the model is in evaluation mode
        model.eval()
        
        # Profile FLOPs based on the provided input data
        flops = torchprofile.profile_macs(model, inputs)
        
        # Multiply by 2 (if needed for your specific calculation)
        flops = flops * 2
        
        return flops
    
    # Get the FLOPs for the model
    flops = get_flops(model, train_loader, device=device)

    #get the best model number of parameters
    best_model = model_state_dict
    num_params = sum(p.numel() for p in best_model.values())

    model_stats = {"flops":flops, "num_params":num_params}
    print(f"FLOPs: {flops} | Number of parameters: {num_params}")
    
    return model_state_dict, epoch, train_losses, valid_losses, train_loss_components, valid_loss_components, model_stats

