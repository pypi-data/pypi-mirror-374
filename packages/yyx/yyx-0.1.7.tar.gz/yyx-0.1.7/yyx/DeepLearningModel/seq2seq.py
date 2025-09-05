import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = ['SimHei', 'Times New Roman']
plt.rcParams["axes.unicode_minus"] = False

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")

class Encoder(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.lstm=nn.LSTM(input_size=input_size, hidden_size=hidden_size, batch_first=True,num_layers=2,dropout=0.2)
        self.input_size=input_size
    def forward(self,x):
        output,(hidden,cell)=self.lstm(x)
        return hidden,cell#[num_layers,B,H]

class Decoder(nn.Module):
    def __init__(self,input_size,hidden_size,output_size):
        super().__init__()
        self.lstm=nn.LSTM(input_size=input_size,hidden_size=hidden_size,batch_first=True,num_layers=2,dropout=0.2)
        self.fc=nn.Linear(hidden_size,output_size)
    def forward(self,x,hidden,cell):
        output,(hidden,cell)=self.lstm(x,(hidden,cell))
        prediction=self.fc(output)
        return prediction,hidden,cell#pre:[B,c]


class Model(nn.Module):
    def __init__(self,enc_input_size,hidden_size,output_size,teacher_forcing_ratio=1):
        super().__init__()
        self.encoder=Encoder(enc_input_size,hidden_size)
        self.decoder=Decoder(1,hidden_size,output_size)
        self.teacher_forcing_ratio=teacher_forcing_ratio
        self.enc_input_size=enc_input_size
    def forward(self,source,context=None,pre_len=7):
        batch_size = source.shape[0]
        hidden,cell=self.encoder(source)#[layer,B,H]
        input_tensor=source[:,-1,0:self.enc_input_size].unsqueeze(1)#[B,1,c]
        res=torch.zeros(batch_size,pre_len,1).to(device)#[B,7,1]h
        for t in range(pre_len):
            output,hidden,cell=self.decoder(input_tensor,hidden,cell)
            res[:,t,:]=output.squeeze(1)#[B,1,c]
            use_teacher_forcing = False
            if self.training and context is not None:
                use_teacher_forcing=torch.rand(1).item()<self.teacher_forcing_ratio
            input_tensor=context[:,t:t+1,:] if use_teacher_forcing else output
        return res#res:[B,T,c]

def create_sliding_windows(data:np.ndarray, seq_len, pre_len):
    x,y=[],[]
    for i in range(len(data) - seq_len - pre_len + 1):
        sale= data[i:i + seq_len].reshape(-1, 1)
        x.append(sale)
        y.append(data[i + seq_len:i + seq_len + pre_len].reshape(-1, 1))
    return np.array(x),np.array(y)#x:[B,T,c],用于训练，y用于测试

def split_train_test(x:np.ndarray, y:np.ndarray, test_ratio=0.2):
    split_idx=int(len(x)*(1-test_ratio))
    x_train,x_test=x[:split_idx],x[split_idx:]
    y_train,y_test=y[:split_idx],y[split_idx:]
    return x_train,y_train,x_test,y_test

def train_model(model,train_loader,epochs=100,lr=0.001):
    #训练集是tensor
    optimizer=optim.Adam(model.parameters(),lr=lr)
    loss_fn=nn.MSELoss()
    model=model.to(device)
    model.train()
    for epoch in range(epochs):
        cur_loss=0.0
        for batch_x,batch_y in train_loader:
            batch_x=batch_x.to(device)
            batch_y=batch_y.to(device)
            output=model(batch_x,batch_y)
            loss=loss_fn(output,batch_y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            cur_loss+=loss.item()
        if (epoch+1)%10==0:
            print(f"Epoch:{epoch+1},损失:{cur_loss/len(train_loader):.6f}")
    return model

def evaluate_model(model:nn.Module,x_test:np.ndarray,y_test:np.ndarray,scaler_sales):
    model.eval()
    with torch.no_grad():
        x_test_tensor=torch.FloatTensor(x_test).to(device)
        pre_scaled=model(x_test_tensor,pre_len=y_test.shape[1])
        pre=scaler_sales.inverse_transform(pre_scaled.cpu().numpy().reshape(-1,1)).reshape(y_test.shape)
        true=scaler_sales.inverse_transform(y_test.reshape(-1,1)).reshape(y_test.shape)
    fla_pre=pre.flatten()
    fla_true=true.flatten()
    metrics={
        'R²':r2_score(fla_true,fla_pre),
        'MSE':mean_squared_error(fla_true,fla_pre),
        'RMSE':np.sqrt(mean_squared_error(fla_true,fla_pre)),
        'MAE':mean_absolute_error(fla_true,fla_pre),
    }
    return metrics,true,pre

def run(df:pd.DataFrame, seq_len=30, pre_len=7, test_ratio=0.2, feature_size=1, epochs=50, lr=0.001,
        hidden_size=64, output_size=1, batch_size=8):
    if 'Unnamed: 0' in df.columns:
        df.drop(columns='Unnamed: 0',inplace=True)
    columns=df.columns
    for column in columns:
        print(f'处理品类{column}')
        data=df[column].values.astype('float32')
        scaler=MinMaxScaler()
        scaled_data=scaler.fit_transform(data.reshape(-1,1))
        x,y=create_sliding_windows(scaled_data,seq_len,pre_len)
        print(f'生成滑动窗口数据，共{len(x)}个数据，每个输入{seq_len}天，预测{pre_len}天')
        x_train,y_train,x_test,y_test=split_train_test(x,y,test_ratio)
        train_loader=DataLoader(TensorDataset(torch.FloatTensor(x_train),torch.FloatTensor(y_train)),batch_size=batch_size,shuffle=False)
        print('-'*50)
        print('开始训练模型')
        print('-'*50)
        model=Model(enc_input_size=feature_size,hidden_size=hidden_size,output_size=output_size)
        model=train_model(model,train_loader,epochs=epochs,lr=lr)
        print('训练完成')
        metrics,true,pre=evaluate_model(model,x_test,y_test,scaler)
        print(f"\n测试集评估指标:")
        print(f"  R²: {metrics['R²']:.4f}")
        print(f"  MSE: {metrics['MSE']:.4f}")
        print(f"  RMSE: {metrics['RMSE']:.4f}")
        print(f"  MAE: {metrics['MAE']:.4f}")
        print('开始全量训练')
        full_loader=DataLoader(TensorDataset(torch.FloatTensor(x),torch.FloatTensor(y)),batch_size=batch_size,shuffle=False)
        model=Model(enc_input_size=feature_size,hidden_size=hidden_size,output_size=output_size)
        model=train_model(model,full_loader,epochs=epochs,lr=lr)
        print("全量训练完成，下面开始预测")
        pre_data=scaled_data[-seq_len:]
        model.eval()
        with torch.no_grad():
            seq_tensor=torch.FloatTensor(pre_data).to(device)
            scaled_output=model(seq_tensor,pre_len=pre_len)
            output=scaler.inverse_transform(scaled_output.cpu().numpy().reshape(-1,1)).flatten()
        print('预测结果为：')
        for i,val in enumerate(output):
            print(f'第{i+1}天，预测值为{val}')
        plt.figure(figsize=(12,6))
        plt.plot()
        plt.plot(true[0], label='真实值', marker='o')  # 当数据形状为(T, 1)时，plt.plot会自动将其视为一维序列
        plt.plot(pre[0], label='预测值', marker='x')
        plt.title(f'{column}测试值与真实值对比')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    df=pd.read_excel('销量.xlsx')
    run(df, seq_len=30, pre_len=7, test_ratio=0.2, epochs=50)
