import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import math
import numpy as np
import pandas as pd
import json
import os
import time

from ..dataloaders.UEID_loader import UEID_loader
from ..trainers.FMS_train import FMS_train
from ..utils.UEID_preprocessing import UEID_preprocessing

import pdb

class BasicTransformer(nn.Transformer):
    #ref https://github.com/danielhocevar/Foundation-Model-for-Soccer/blob/main/models/transformer.py
    def __init__(self, input_dim, output_dim, num_actions=9, ninp=50, nhead=5, nhid=500, nlayers=4, dropout=0.2):
        """
        num_actions: dictionary length
        ninp: size of word embeddings
        nhead: number of heads in the encoder/decoder
        nhid: number of hidden units in hidden layers
        nlayers: number of hidden layers
        dropout: dropout probability
        """
        self.input_padding = nhead* (input_dim//nhead+1)-input_dim
        self.input_dim = input_dim + self.input_padding
        super(BasicTransformer, self).__init__(d_model=self.input_dim, nhead=nhead, dim_feedforward=nhid, num_encoder_layers=nlayers)
        self.model_type = 'Transformer'
        self.src_mask = None
        self.pos_encoder = PositionalEncoding(self.input_dim, dropout)

        self.input_emb = nn.Embedding(num_actions, ninp)
        self.ninp = ninp
        self.decoder = nn.Linear(self.input_dim, output_dim)

        self.init_weights()

    def _generate_square_subsequent_mask(self, sz):
        return torch.log(torch.tril(torch.ones(sz,sz)))

    def init_weights(self):
        initrange = 0.1
        nn.init.uniform_(self.input_emb.weight, -initrange, initrange)
        nn.init.zeros_(self.decoder.bias)
        nn.init.uniform_(self.decoder.weight, -initrange, initrange)

    def forward(self, src, has_mask=True):
        if has_mask:
            device = src.device
            if self.src_mask is None or self.src_mask.size(0) != len(src):
                mask = self._generate_square_subsequent_mask(len(src)).to(device)
                self.src_mask = mask
        else:
            self.src_mask = None

        src_action=src[:,:,0].long()
        src_action = self.input_emb(src_action) * math.sqrt(self.ninp)

        padding = torch.zeros(src.shape[0], src.shape[1], self.input_padding).to(src.device)

        src = torch.cat((src_action, src[:,:,1:], padding), dim=-1)
        src = self.pos_encoder(src)
        output = self.encoder(src, mask=self.src_mask)
        output = self.decoder(output[:,-1,:])
        return output

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        # Apply cos to odd indices in the array (1, 3, 5, ...)
        if d_model % 2 == 0:
            pe[:, 1::2] = torch.cos(position * div_term)
        else:
            pe[:, 1::2] = torch.cos(position * div_term[:(d_model // 2)])
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

def train_FMS(current_time, config, train_df, valid_df, seq_len, features, epochs, batch_size,
            delta_T_bin, start_x_bin, start_y_bin,
            ninp, nhead, nhid, nlayers, dropout,
            num_actions=9, device=None, print_freq=10, patience=5, num_workers=4, optuna=False,
            learning_rate=0.01,eps=1e-16):

    # check if the train_df and valid_df are pandas dataframe
    if not isinstance(train_df, pd.DataFrame):
        #check if the train_df is a path
        if isinstance(train_df, str):
            train_df = pd.read_csv(train_df) if not config['test'] else pd.read_csv(train_df).head(1000)
        else:
            raise ValueError("train_df must be a pandas dataframe or a path to a csv file")
    if not isinstance(valid_df, pd.DataFrame):
        #check if the valid_df is a path
        if isinstance(valid_df, str):
            valid_df = pd.read_csv(valid_df) if not config['test'] else pd.read_csv(valid_df).head(1000)
        else:
            raise ValueError("valid_df must be a pandas dataframe or a path to a csv file")
        
    # Preprocess the data
    train_df, min_dict, max_dict = UEID_preprocessing(train_df)
    valid_df, _, _ = UEID_preprocessing(valid_df, min_dict, max_dict)

    # Define fixed hyperparameters 
    input_dim = len(features)-1+ ninp
    output_dim = num_actions + delta_T_bin + start_x_bin + start_y_bin

    #if not device is given, check if cuda is available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if device is None or device == 'None' else device

    # Initialize model layers based on data
    model = BasicTransformer(input_dim, output_dim, num_actions, ninp, nhead, nhid, nlayers, dropout).to(device)
    
    # Create data loaders
    train_loader = UEID_loader(train_df, seq_len, features)
    valid_loader = UEID_loader(valid_df, seq_len, features)

    # Convert data loaders to torch DataLoader
    train_loader = DataLoader(train_loader, batch_size=batch_size, shuffle=True, drop_last=True, num_workers=num_workers)
    valid_loader = DataLoader(valid_loader, batch_size=batch_size, shuffle=False, drop_last=False, num_workers=num_workers)
    
    # Define optimizer
    optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate,eps=eps)

    # Training logic here
    model_state_dict, best_epoch, train_losses, valid_losses, train_loss_components, valid_loss_components, flops = FMS_train(model, train_loader, valid_loader, min_dict, max_dict, optimizer, device, epochs, print_freq, patience,config=config)

    #create one csv file for the training and validation losses
    columns = ['train_loss', 'CEL_action', 'CEL_deltaT','CEL_start_x','CEL_start_y', 'ACC_action', 'F1_action', 'MAE_deltaT', 'MAE_x', 'MAE_y',
                'valid_loss', 'CEL_action_v', 'CEL_deltaT_v','CEL_start_x_v','CEL_start_y_v', 'ACC_action_v', 'F1_action_v', 'MAE_deltaT_v', 'MAE_x_v', 'MAE_y_v']
    data = [train_losses, np.array(train_loss_components)[:,0], np.array(train_loss_components)[:,1], np.array(train_loss_components)[:,2], np.array(train_loss_components)[:,3], np.array(train_loss_components)[:,4], np.array(train_loss_components)[:,5], np.array(train_loss_components)[:,6], np.array(train_loss_components)[:,7], np.array(train_loss_components)[:,8],
            valid_losses, np.array(valid_loss_components)[:,0], np.array(valid_loss_components)[:,1], np.array(valid_loss_components)[:,2], np.array(valid_loss_components)[:,3], np.array(valid_loss_components)[:,4], np.array(valid_loss_components)[:,5], np.array(valid_loss_components)[:,6], np.array(valid_loss_components)[:,7], np.array(valid_loss_components)[:,8]]
    data = np.array(data).T
    loss_df = pd.DataFrame(data, columns=columns)
    #round the loss_df to 4 decimal places
    loss_df = loss_df.round(4)

    
    #save the model and the loss_df
    if config['optuna']:
        method = "optuna"
    else:
        method = "train"
    i=1
    save_path = config['save_path']+f"/out/{method}/{current_time}/run_{i}/"
    while os.path.exists(save_path):
        i+=1
        save_path = config['save_path']+f"/out/{method}/{current_time}/run_{i}/"
    os.makedirs(save_path)

    model_save_path = save_path + f"_model_{best_epoch}.pth"
    loss_save_path = save_path + "_loss.csv"
    hyperparameters_save_path = save_path + "hyperparameters.json"
    model_stats_save_path = save_path + "_model_stats.txt"
    
    #save the min_dict and max_dict
    min_max_dict_path = config['save_path']+f"/out/{method}/{current_time}/min_max_dict.json"
    with open(min_max_dict_path, 'w') as f:
        json.dump({'min_dict':min_dict, 'max_dict':max_dict}, f, indent=4)

    #save all the hyperparameters values
    hyperparameters = {'current_time': current_time,
                        'train_path': config['train_path'], 'valid_path': config['valid_path'], 'save_path': config['save_path'],
                        'test': config['test'], 'batch_size': batch_size, 'num_epoch': config['num_epoch'],
                        'print_freq': print_freq, 'early_stop_patience': config['early_stop_patience'],
                        'dataloader_num_worker': config['dataloader_num_worker'], 'device': config['device'], 
                        'basic_features': config['basic_features'], 'other_features': config['other_features'],
                        'use_other_features': config['use_other_features'],
                        'features':features, 'num_actions': num_actions, 'seq_len': seq_len,
                        'optuna': config['optuna'], 'optuna_n_trials': config['optuna_n_trials'],
                        'learning_rate': learning_rate, 'eps': eps,
                        'delta_T_bin': delta_T_bin, 'start_x_bin': start_x_bin, 'start_y_bin': start_y_bin,
                        'ninp': ninp, 'nhead': nhead, 'nhid': nhid, 'nlayers': nlayers, 'dropout': dropout,
                        'input_dim': input_dim, 'output_dim': output_dim,
                        'model':model.__class__.__name__,
                        'best_epoch':best_epoch}
                
    torch.save(model_state_dict, model_save_path)
    loss_df.to_csv(loss_save_path, index=False)
    with open(hyperparameters_save_path, 'w') as f:
        json.dump(hyperparameters, f, indent=4)
    with open(model_stats_save_path, "w") as f:
        f.write(str(flops))
        
    print("Model and loss saved at", save_path)

    if optuna:
        return valid_losses[best_epoch]

def main(config):
    train_path = config['train_path']
    valid_path = config['valid_path']

    # Extract input dimensions from train_df
    if config['test']:
        seq_len = 10
        epochs = 2
        features = config['basic_features']+config['other_features']
    else:
        seq_len = config['seq_len']
        epochs = config['num_epoch']
        if config['use_other_features']:
            features = config['basic_features']+config['other_features']
        else:
            features = config['basic_features']
    
    batch_size = config['batch_size']
    num_actions = config['num_actions']
    print_freq = config['print_freq']
    early_stop_patience = config['early_stop_patience']
    dataloader_num_worker = config['dataloader_num_worker']
    learning_rate = config['learning_rate']
    eps = config['eps']
    eps = float(eps) if not isinstance(eps, float) else eps
    device = config['device']

    #tunable hyperparameters
    delta_T_bin = config['delta_T_bin']
    start_x_bin = config['start_x_bin']
    start_y_bin = config['start_y_bin']
    ninp = config['ninp']
    nhead = config['nhead']
    nhid = config['nhid']
    nlayers = config['nlayers']
    dropout = config['dropout']


    current_time = time.strftime("%Y%m%d_%H%M%S")
    train_FMS(current_time, config, train_path, valid_path, seq_len, features, epochs, batch_size,
                delta_T_bin, start_x_bin, start_y_bin,
                 ninp, nhead, nhid, nlayers, dropout,
                num_actions=num_actions,device=device,print_freq=print_freq, patience=early_stop_patience,num_workers=dataloader_num_worker,
                learning_rate=learning_rate,eps=eps)

def main_optuna(config):
    import optuna
    train_path = config['train_path']
    valid_path = config['valid_path']

    # Extract input dimensions from train_df
    if config['test']:
        seq_len = 10
        epochs = 2
        features = config['basic_features']+config['other_features']
    else:
        seq_len = config['seq_len']
        epochs = config['num_epoch']
        if config['use_other_features']:
            features = config['basic_features']+config['other_features']
        else:
            features = config['basic_features']
    
    num_actions = config['num_actions']
    print_freq = config['print_freq']
    early_stop_patience = config['early_stop_patience']
    dataloader_num_worker = config['dataloader_num_worker']
    device = config['device']

    delta_T_bin = config['delta_T_bin']
    start_x_bin = config['start_x_bin']
    start_y_bin = config['start_y_bin']

    def objective(trial):
        # tunable hyperparameters
        try:
            learning_rate=trial.suggest_float('learning_rate', float(config['learning_rate'][0]), float(config['learning_rate'][1])) if len(config['learning_rate'])>1 else config['learning_rate'][0]
            config['eps'] = [float(i) for i in config['eps']]
            eps=trial.suggest_float('eps',  float(config['eps'][1]), float(config['eps'][1])) if len(config['eps'])>1 else config['eps'][0]
            batch_size=trial.suggest_categorical('batch_size', config['batch_size'])  
          
            ninp=trial.suggest_categorical('ninp', config['ninp'])
            nhead=trial.suggest_categorical('nhead', config['nhead'])
            nhid=trial.suggest_categorical('nhid', config['nhid'])
            nlayers=trial.suggest_categorical('nlayers', config['nlayers'])
            dropout=trial.suggest_categorical('dropout', config['dropout'])
        except:
            print("Error in the yaml file")
            
        # Call your train function with these parameters
        valid_loss = train_FMS(current_time, config, train_path, valid_path, seq_len, features, epochs, batch_size,
                delta_T_bin, start_x_bin, start_y_bin,
                ninp, nhead, nhid, nlayers, dropout, optuna=True,
                num_actions=num_actions,device=device,print_freq=print_freq, patience=early_stop_patience,num_workers=dataloader_num_worker,
                learning_rate=learning_rate,eps=eps)
        
        return valid_loss


    n_trials = config['optuna_n_trials'] if not config['test'] else 2

    # Create an Optuna study object
    study = optuna.create_study(direction='minimize')
    
    # Optimize the objective function
    current_time = time.strftime("%Y%m%d_%H%M%S")
    study.optimize(objective, n_trials=n_trials)
    
    # Print the best trial results
    print("Best trial:")
    trial = study.best_trial
    best_trial_number = trial.number+1
    best_params = trial.params
    print(f"  Trial Number: {best_trial_number}")
    print(f"  Best Valid Loss: {trial.value:.4f}")
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")
    
    # Add the trial number to the parameters dictionary
    best_params_with_trial = {
        'best_trial_number': best_trial_number,
        'best_valid_loss': trial.value,
        **best_params
    }

    # Save the best hyperparameters with the trial number to a JSON file
    with open(config['save_path']+f'out/optuna/{current_time}/optuna_best_hyperparameters.json', 'w') as f:
        json.dump(best_params_with_trial, f, indent=4)

if __name__ == "__main__":
    import pandas as pd
    import argparse
    import yaml

    prase = argparse.ArgumentParser()
    prase.add_argument('--config_path', '-c', type=str, default=os.getcwd()+'/event/sports/soccer/models/model_yaml_test/train_FMS.yaml')
    args = prase.parse_args()
    config_path = args.config_path

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    if config['optuna']:
        main_optuna(config)
    else:
        main(config)

    '''
    all_features = ['match_id','poss_id','team','home_team','action','success','goal','home_score',
                'away_score','goal_diff','Period','Minute','Second','seconds','delta_T',
                'start_x','start_y','deltaX','deltaY','distance','dist2goal','angle2goal']
    basic_features = ['action', 'delta_T', 'start_x','start_y'] 
    derivable_features = ['team','home_team','action','success','seconds','delta_T','start_x','start_y','deltaX','deltaY','distance','dist2goal','angle2goal']
    other_features = ['team','home_team','success','seconds','deltaX','deltaY','distance','dist2goal','angle2goal']
    '''
    
