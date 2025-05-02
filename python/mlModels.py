import pandas as pd
from xgboost import XGBRegressor
import torch
import torch.nn as nn
import numpy as np

SBP_MAX = 180
DBP_MAX = 120
class CNNLSTM_BP(nn.Module):
    def __init__(self):
        super(CNNLSTM_BP, self).__init__()
        self.conv1 = nn.Conv1d(1, 16, kernel_size=15, stride=2, padding=7)
        self.bn1 = nn.BatchNorm1d(16)
        self.dropout1 = nn.Dropout(0.3)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=15, stride=2, padding=7)
        self.bn2 = nn.BatchNorm1d(32)
        self.dropout2 = nn.Dropout(0.3)
        self.conv3 = nn.Conv1d(32, 64, kernel_size=15, stride=2, padding=7)
        self.bn3 = nn.BatchNorm1d(64)
        self.dropout3 = nn.Dropout(0.3)
        self.lstm = nn.LSTM(input_size=64, hidden_size=64, batch_first=True)
        self.fc1 = nn.Linear(64, 64)
        self.fc2 = nn.Linear(64, 2)

    def forward(self, x):
        x = x.unsqueeze(1)
        x = torch.relu(self.bn1(self.conv1(x)))
        x = self.dropout1(x)
        x = torch.relu(self.bn2(self.conv2(x)))
        x = self.dropout2(x)
        x = torch.relu(self.bn3(self.conv3(x)))
        x = self.dropout3(x)
        x = x.permute(0, 2, 1)
        _, (hn, _) = self.lstm(x)
        x = torch.relu(self.fc1(hn[-1]))
        return self.fc2(x)

class mlModel:
    def __init__(self, xgmodel_path: str, bpmodel_path:str) -> None:
        self.xgmodel = XGBRegressor()
        self.xgmodel.load_model(xgmodel_path)
        
        self.bpModel=CNNLSTM_BP()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.bpModel.load_state_dict(torch.load(bpmodel_path, map_location=self.device))
        self.bpModel.eval()
        self.bpModel = self.bpModel.to(self.device)

    def stressCalculation(self, data:list) -> int:
        return int(self.xgmodel.predict(data)[0])
    
    def preprocess_signal(self,new_signal, max_length=2000):
        signal_mean = np.mean(new_signal)
        signal_std = np.std(new_signal) + 1e-6
        signal = (new_signal - signal_mean) / signal_std

        if len(signal) < max_length:
            signal = np.pad(signal, (0, max_length - len(signal)))
        else:
            signal = signal[:max_length]

        tensor = torch.tensor(signal, dtype=torch.float32).unsqueeze(0)
        return tensor
    
    def bpCalculation(self,SignalInput):
        signal_np = np.array(SignalInput)
        processed_signal = self.preprocess_signal(signal_np).to(self.device)

        with torch.no_grad():
            output = self.bpModel(processed_signal)
            sbp_pred, dbp_pred = output.squeeze().cpu().numpy()
            predicted_sbp = sbp_pred * SBP_MAX
            predicted_dbp = dbp_pred * DBP_MAX

        return round(float(predicted_sbp), 2), round(float(predicted_dbp), 2)


