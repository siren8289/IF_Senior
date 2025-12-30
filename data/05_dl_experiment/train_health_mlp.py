import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# =========================
# 1. 데이터 로드
# =========================
df = pd.read_csv(
    "data/01_feature_source/Health_Condition/seniors_clean.csv"
)

# 컬럼 순서 교정
df = df.rename(columns={
    "work_intent": "activity_level_tmp",
    "activity_level": "work_intent"
})
df = df.rename(columns={
    "activity_level_tmp": "activity_level"
})

# 문자열 정리
for col in ["health_score", "work_intent", "activity_level"]:
    df[col] = df[col].astype(str).str.strip()

# =========================
# 2. 수치화
# =========================
health_map = {
    "매우나쁨": 1,
    "나쁨": 2,
    "보통": 3,
    "좋음": 4,
    "매우좋음": 5
}

activity_map = {
    "약함": 1,
    "중간": 2,
    "강함": 3
}

work_intent_map = {
    "필요없음": 0,
    "약간필요": 1,
    "많이필요": 1
}

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["chronic_disease_count"] = pd.to_numeric(
    df["chronic_disease_count"], errors="coerce"
)

df["health_score"] = df["health_score"].map(health_map)
df["activity_level"] = df["activity_level"].map(activity_map)
df["work_intent"] = df["work_intent"].map(work_intent_map)

df = df.dropna()

X = df[[
    "age",
    "health_score",
    "chronic_disease_count",
    "activity_level"
]].values

y = df["work_intent"].values

# =========================
# 3. 정규화
# =========================
scaler = StandardScaler()
X = scaler.fit_transform(X)

# =========================
# 4. Train / Test split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 5. Dataset
# =========================
class HealthDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

train_loader = DataLoader(
    HealthDataset(X_train, y_train),
    batch_size=32,
    shuffle=True
)

test_loader = DataLoader(
    HealthDataset(X_test, y_test),
    batch_size=32
)

# =========================
# 6. MLP 모델
# =========================
class HealthMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

model = HealthMLP()
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# =========================
# 7. 학습
# =========================
epochs = 30

for epoch in range(epochs):
    model.train()
    total_loss = 0

    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        preds = model(X_batch).squeeze()
        loss = criterion(preds, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss:.4f}")

# =========================
# 8. 평가
# =========================
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for X_batch, y_batch in test_loader:
        preds = model(X_batch).squeeze()
        predicted = (preds > 0.5).int()
        correct += (predicted == y_batch.int()).sum().item()
        total += y_batch.size(0)

accuracy = correct / total
print(f"\n✅ Test Accuracy: {accuracy:.4f}")
