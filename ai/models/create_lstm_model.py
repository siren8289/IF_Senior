import torch
from lstm_model import AnomalyLSTM

if __name__ == "__main__":
    model = AnomalyLSTM()
    torch.save(model.state_dict(), "ai/models/lstm_model.pt")
    print("✅ LSTM state_dict 저장 완료")
