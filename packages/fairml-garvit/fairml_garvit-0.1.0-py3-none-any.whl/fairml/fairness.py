import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import random
import matplotlib.pyplot as plt



# ---------------------------
# Utility seeds for reproducibility
# ---------------------------
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
random.seed(SEED)

# ---------------------------
# Models
# ---------------------------
class Predictor(nn.Module):
    def __init__(self, input_dim, output_dim=1, hidden=32):
        super(Predictor, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, output_dim)
        )

    def forward(self, x):
        return self.net(x)  # logits for binary classification

class Critic(nn.Module):
    """Predicts positive 'delta' per sample -- use Softplus to avoid dead zeros"""
    def __init__(self, input_dim, hidden=16):
        super(Critic, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),
            nn.Softplus()   # strictly > 0, differentiable
        )

    def forward(self, x):
        return self.net(x)

# ---------------------------
# Evaluation helpers
# ---------------------------
def evaluate_predictor(predictor, X, X_cf, y):
    predictor.eval()
    with torch.no_grad():
        logits = predictor(torch.tensor(X, dtype=torch.float32)).squeeze(1)
        probs = torch.sigmoid(logits).numpy()
        preds = (probs > 0.5).astype(int)

        logits_cf = predictor(torch.tensor(X_cf, dtype=torch.float32)).squeeze(1)
        probs_cf = torch.sigmoid(logits_cf).numpy()

    disparity = (probs - probs_cf)**2
    overall_acc = accuracy_score(y, preds)

    genders = X[:, 1].astype(int)
    acc_by_group = {}
    mean_prob_by_group = {}

    for g in np.unique(genders):
        idx = genders == g
        if idx.sum() > 0:
            acc_by_group[int(g)] = accuracy_score(y[idx], preds[idx])
            mean_prob_by_group[int(g)] = float(probs[idx].mean())
        else:
            acc_by_group[int(g)] = None
            mean_prob_by_group[int(g)] = None

    return {
        "mean_disparity": float(disparity.mean()),
        "median_disparity": float(np.median(disparity)),
        "overall_acc": float(overall_acc),
        "acc_by_group": acc_by_group,
        "mean_prob_by_group": mean_prob_by_group,
        "disparity_array": disparity,
        "probs": probs,
        "probs_cf": probs_cf
    }

# ---------------------------
# FairnessModel wrapper
# ---------------------------
class FairnessModel:
    def __init__(self, input_dim, lr=1e-3, task_type="classification", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.predictor = Predictor(input_dim).to(self.device)
        self.critic = Critic(input_dim).to(self.device)
        self.lr = lr
        self.task_type = task_type

        # per-sample losses
        if task_type == "classification":
            self.task_loss_fn = nn.BCEWithLogitsLoss(reduction='none')
        else:
            self.task_loss_fn = nn.MSELoss(reduction='none')

        # joint optimizer for predictor and critic
        self.optimizer = optim.Adam(
            list(self.predictor.parameters()) + list(self.critic.parameters()),
            lr=self.lr
        )

    def train_baseline(self, X, y, epochs=50, batch_size=32, verbose=False):
        """Train predictor only on task loss to get baseline model."""
        dataset = torch.utils.data.TensorDataset(
            torch.tensor(X, dtype=torch.float32),
            torch.tensor(y, dtype=torch.float32).unsqueeze(1)
        )
        
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        opt = optim.Adam(self.predictor.parameters(), lr=self.lr)
        loss_fn = nn.BCEWithLogitsLoss() if self.task_type == "classification" else nn.MSELoss()

        for epoch in range(epochs):
            epoch_loss = 0.0
            for X_batch, y_batch in loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)
                opt.zero_grad()
                logits = self.predictor(X_batch)
                loss = loss_fn(logits, y_batch)
                loss.backward()
                opt.step()
                epoch_loss += loss.item() * X_batch.size(0)
            if verbose and (epoch+1) % max(1, epochs//5) == 0:
                print(f"[Baseline] Epoch {epoch+1}/{epochs} task_loss: {epoch_loss/len(loader.dataset):.6f}")

    def fit_fair(self, X, y, X_cf, epochs=100, batch_size=32, verbose=True):
        """Train predictor+critic to minimize per-sample fair loss:
           per_sample_fair = delta_pred * disparity * per_sample_task_loss
        """
        dataset = torch.utils.data.TensorDataset(
            torch.tensor(X, dtype=torch.float32),
            torch.tensor(y, dtype=torch.float32).unsqueeze(1),
            torch.tensor(X_cf, dtype=torch.float32)
        )
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        for epoch in range(epochs):
            accum_fair = 0.0
            accum_task = 0.0
            accum_disp = 0.0
            accum_delta = 0.0

            for X_batch, y_batch, X_cf_batch in loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)
                X_cf_batch = X_cf_batch.to(self.device)

                self.optimizer.zero_grad()

                # logits
                y_logit = self.predictor(X_batch)          # (B,1)
                y_logit_cf = self.predictor(X_cf_batch)    # (B,1)

                # per-sample task loss (B,1)
                per_sample_loss = self.task_loss_fn(y_logit, y_batch)  # (B,1)

                # probabilities for disparity calculation
                y_prob = torch.sigmoid(y_logit).squeeze(1)        # (B,)
                y_prob_cf = torch.sigmoid(y_logit_cf).squeeze(1)  # (B,)

                disparity = (y_prob - y_prob_cf).pow(2).unsqueeze(1)  # (B,1)

                # critic predicts delta > 0
                delta_pred = self.critic(X_batch)  # (B,1)

                # per-sample fair loss
                per_sample_fair = delta_pred * disparity * per_sample_loss  # (B,1)
                fair_loss = per_sample_fair.mean()

                # backprop & step
                fair_loss.backward()
                self.optimizer.step()

                # accumulate for logging
                n = X_batch.size(0)
                accum_fair += float(fair_loss.item()) * n
                accum_task += float(per_sample_loss.mean().item()) * n
                accum_disp += float(disparity.mean().item()) * n
                accum_delta += float(delta_pred.mean().item()) * n

            N = len(loader.dataset)
            epoch_fair = accum_fair / N
            epoch_task = accum_task / N
            epoch_disp = accum_disp / N
            epoch_delta = accum_delta / N

            if verbose:
                print(f"Epoch {epoch+1}/{epochs}, "
                      f"Fair Loss: {epoch_fair:.8f}, "
                      f"Task Loss: {epoch_task:.8f}, "
                      f"Mean Disparity: {epoch_disp:.8f}, "
                      f"Mean Delta: {epoch_delta:.8f}")

    def predict_proba(self, X):
        self.predictor.eval()
        with torch.no_grad():
            logits = self.predictor(torch.tensor(X, dtype=torch.float32).to(self.device)).squeeze(1)
            probs = torch.sigmoid(logits).cpu().numpy()
        return probs