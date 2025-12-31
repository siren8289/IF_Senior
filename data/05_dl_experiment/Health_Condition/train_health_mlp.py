"""
Health Care Prediction Model (PyTorch MLP)
==========================================
문제 유형: 이진 분류
타깃(Y): care_need (돌봄 필요 여부)
피처(X): age, health_score, chronic_disease_count, work_willingness

목적: sklearn baseline과 비교하여 구조적 확장 가능성 실험
"""
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from collections import Counter

# =========================
# 1. 경로 설정
# =========================
base_dir = Path(__file__).parent.parent.parent.parent
data_path = base_dir / "data" / "01_feature_source" / "Health_Condition" / "seniors_clean.csv"

if not data_path.exists():
    raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

# =========================
# 2. 데이터 로드
# =========================
df = pd.read_csv(data_path, encoding="utf-8-sig")

# 필수 컬럼 확인
REQUIRED_COLS = ["age", "health_score", "chronic_disease_count", "work_willingness", "care_need"]
missing = set(REQUIRED_COLS) - set(df.columns)
if missing:
    raise ValueError(f"필수 컬럼이 없습니다: {missing}")

print(f"원본 데이터: {len(df)}행")

# =========================
# 3. 데이터 전처리
# =========================
# 문자열 정리
for col in ["health_score", "work_willingness", "care_need"]:
    df[col] = df[col].astype(str).str.strip()

# 숫자형 변환
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["chronic_disease_count"] = pd.to_numeric(df["chronic_disease_count"], errors="coerce")

# =========================
# 4. Feature Encoding (표준 규칙)
# =========================
health_map = {
    "매우나쁨": 1,
    "나쁨": 2,
    "보통": 3,
    "좋음": 4,
    "매우좋음": 5
}

work_willingness_map = {
    "약함": 1,
    "중간": 2,
    "강함": 3
}

df["health_score"] = df["health_score"].map(health_map)
df["work_willingness"] = df["work_willingness"].map(work_willingness_map)

# =========================
# 5. Target Encoding (표준 규칙)
# =========================
care_need_map = {
    "필요없음": 0,
    "약간필요": 1,
    "많이필요": 1
}

df["care_need"] = df["care_need"].map(care_need_map)

# =========================
# 6. 결측치 제거
# =========================
df = df.dropna()
print(f"전처리 후 데이터: {len(df)}행")

if len(df) == 0:
    raise ValueError("전처리 후 사용 가능한 데이터가 없습니다.")

# =========================
# 7. Feature / Target 분리
# =========================
X = df[[
    "age",
    "health_score",
    "chronic_disease_count",
    "work_willingness"
]].values

y = df["care_need"].values

print(f"타깃 분포: {Counter(y)}")

# =========================
# 8. 정규화
# =========================
scaler = StandardScaler()
X = scaler.fit_transform(X)

# =========================
# 9. Train / Test Split
# =========================
# stratify 안전 처리
y_counts = Counter(y)
can_stratify = len(y_counts) > 1 and min(y_counts.values()) >= 2

if can_stratify:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("✅ Stratified split 적용")
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print("⚠️ Stratified split 불가 (클래스 불균형)")

# =========================
# 10. Dataset
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
    batch_size=32,
    shuffle=False
)

# =========================
# 11. MLP 모델
# =========================
class HealthMLP(nn.Module):
    def __init__(self, input_dim=4, hidden_dims=[16, 8], dropout=0.2):
        super().__init__()
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())
        
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)

model = HealthMLP(input_dim=4, hidden_dims=[16, 8], dropout=0.2)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

print(f"\n모델 구조:\n{model}")

# =========================
# 12. 학습
# =========================
epochs = 30
train_losses = []

for epoch in range(epochs):
    model.train()
    total_loss = 0
    batch_count = 0

    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        preds = model(X_batch).squeeze()
        loss = criterion(preds, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        batch_count += 1

    avg_loss = total_loss / batch_count if batch_count > 0 else 0
    train_losses.append(avg_loss)
    
    if (epoch + 1) % 5 == 0:
        print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")

# =========================
# 13. 평가
# =========================
model.eval()
correct = 0
total = 0
all_preds = []
all_labels = []

with torch.no_grad():
    for X_batch, y_batch in test_loader:
        preds = model(X_batch).squeeze()
        predicted = (preds > 0.5).int()
        correct += (predicted == y_batch.int()).sum().item()
        total += y_batch.size(0)
        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(y_batch.int().cpu().numpy())

accuracy = correct / total if total > 0 else 0

print(f"\n=== PyTorch MLP 결과 ===")
print(f"Test Accuracy: {accuracy:.4f}")
print(f"Train Loss (final): {train_losses[-1]:.4f}")
print(f"✅ PyTorch MLP 학습 완료")
