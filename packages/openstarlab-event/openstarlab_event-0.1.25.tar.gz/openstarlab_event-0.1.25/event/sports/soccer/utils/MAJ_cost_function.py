import torch
import torch.nn as nn
import pdb

def calculate_f1_score(gt_classes, pred_classes, num_classes):
    f1_scores = []
    
    for i in range(num_classes):
        # True Positives (TP), False Positives (FP), False Negatives (FN)
        tp = torch.sum((pred_classes == i) & (gt_classes == i)).float()
        fp = torch.sum((pred_classes == i) & (gt_classes != i)).float()
        fn = torch.sum((pred_classes != i) & (gt_classes == i)).float()
        
        # Precision and Recall
        precision = tp / (tp + fp + 1e-8)  # Add small constant to avoid division by zero
        recall = tp / (tp + fn + 1e-8)     # Add small constant to avoid division by zero
        
        # F1 Score
        f1 = 2 * (precision * recall) / (precision + recall + 1e-8)  # Add small constant to avoid division by zero
        f1_scores.append(f1)
    
    # Average F1 Score across all classes
    avg_f1_score = torch.mean(torch.stack(f1_scores))
    
    return avg_f1_score

def MAJ_cost_function(gt, pred,min_dict=None, max_dict=None, device="None",config=None):
    #check if pred is in device
    if pred.device != device:
        pred = pred.to(device)
    num_actions = config["num_actions"] if config is not None and config !="None" else 9
    num_deltaT = config["delta_T_bin"] if config is not None and config !="None" else 61
    num_start_x = config["start_x_bin"] if config is not None and config !="None" else 101
    num_start_y = config["start_y_bin"] if config is not None and config !="None" else 101
    gt_action = gt[:,0:num_actions].float()
    gt_deltaT = gt[:,num_actions:num_actions+num_deltaT].float()
    gt_start_x = gt[:,num_actions+num_deltaT:num_actions+num_deltaT+num_start_x].float()
    gt_start_y = gt[:,num_actions+num_deltaT+num_start_x:].float()
    pred_action = pred[:,0:num_actions]
    pred_deltaT = pred[:,num_actions:num_actions+num_deltaT]
    pred_start_x = pred[:,num_actions+num_deltaT:num_actions+num_deltaT+num_start_x]
    pred_start_y = pred[:,num_actions+num_deltaT+num_start_x:]
    #BCEL
    BCEL_action_loss = torch.nn.BCELoss()
    BCEL_action = torch.mean(BCEL_action_loss(pred_action,gt_action))
    BCEL_deltaT_loss = torch.nn.BCELoss()
    BCEL_deltaT = torch.mean(BCEL_deltaT_loss(pred_deltaT,gt_deltaT))
    BCEL_start_x_loss = torch.nn.BCELoss()
    BCEL_start_x = torch.mean(BCEL_start_x_loss(pred_start_x,gt_start_x))
    BCEL_start_y_loss = torch.nn.BCELoss()
    BCEL_start_y = torch.mean(BCEL_start_y_loss(pred_start_y,gt_start_y))

    train_loss = BCEL_action + BCEL_deltaT + BCEL_start_x + BCEL_start_y

    #AE for deltaT, start_x, start_y
    if max_dict is not None and min_dict is not None:
        ACC_action = torch.mean((torch.argmax(pred,1)==torch.argmax(gt_action,1)).float())
        f1_action = calculate_f1_score(torch.argmax(gt_action,1),torch.argmax(pred,1),num_actions)
        deltaT_pred = torch.argmax(pred_deltaT,1)/100
        deltaT_pred = torch.exp( deltaT_pred * ( torch.tensor(max_dict["delta_T"], device=device) - torch.tensor(min_dict["delta_T"], device=device)) + torch.tensor(min_dict["delta_T"], device=device)) - torch.tensor(1e-6, device=device) 
        deltaT = torch.argmax(gt_deltaT,1)/100
        deltaT = torch.exp( deltaT * ( torch.tensor(max_dict["delta_T"], device=device) - torch.tensor(min_dict["delta_T"], device=device)) + torch.tensor(min_dict["delta_T"], device=device)) - torch.tensor(1e-6, device=device)
        start_x_pred = torch.argmax(pred_start_x,1)/100
        start_x_pred = start_x_pred * ( torch.tensor(max_dict["start_x"], device=device) - torch.tensor(min_dict["start_x"], device=device)) + torch.tensor(min_dict["start_x"], device=device)
        start_x = torch.argmax(gt_start_x,1)/100
        start_x = start_x * ( torch.tensor(max_dict["start_x"], device=device) - torch.tensor(min_dict["start_x"], device=device)) + torch.tensor(min_dict["start_x"], device=device)
        start_y_pred = torch.argmax(pred_start_y,1)/100
        start_y_pred = start_y_pred * ( torch.tensor(max_dict["start_y"], device=device) - torch.tensor(min_dict["start_y"], device=device)) + torch.tensor(min_dict["start_y"], device=device)
        start_y = torch.argmax(gt_start_y,1)/100
        start_y = start_y * ( torch.tensor(max_dict["start_y"], device=device) - torch.tensor(min_dict["start_y"], device=device)) + torch.tensor(min_dict["start_y"], device=device)
        
        #ignore in backpropagation
        AE_deltaT = torch.mean(torch.abs(deltaT_pred-deltaT)).detach()
        AE_start_x = torch.mean(torch.abs(start_x_pred-start_x)).detach()
        AE_start_y = torch.mean(torch.abs(start_y_pred-start_y)).detach()
    else:
        ACC_action = torch.tensor(-1, device=device)
        f1_action = torch.tensor(-1, device=device)
        AE_deltaT = torch.tensor(-1, device=device)
        AE_start_x = torch.tensor(-1, device=device)
        AE_start_y = torch.tensor(-1, device=device)

    return train_loss, [BCEL_action, BCEL_deltaT, BCEL_start_x, BCEL_start_y, ACC_action, f1_action, AE_deltaT, AE_start_x, AE_start_y]