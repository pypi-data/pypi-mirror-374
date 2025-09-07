import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score
import random
import warnings

class FairnessModel:
    def __init__(self, input_dim, output_dim=1, hidden_pred=32, hidden_critic=16, 
                 lr=1e-3, task_type="classification", seed=42, device=None):
        """
        Fairness-aware model combining predictor and critic.
        """
        # Reproducibility
        self.seed = seed
        np.random.seed(seed)
        torch.manual_seed(seed)
        random.seed(seed)

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Predictor network
        self.predictor = nn.Sequential(
            nn.Linear(input_dim, hidden_pred),
            nn.ReLU(),
            nn.Linear(hidden_pred, output_dim)
        ).to(self.device)

        # Critic network
        self.critic = nn.Sequential(
            nn.Linear(input_dim, hidden_critic),
            nn.ReLU(),
            nn.Linear(hidden_critic, 1),
            nn.Softplus()
        ).to(self.device)

        self.lr = lr
        self.task_type = task_type

        # Task loss
        if task_type == "classification":
            self.task_loss_fn = nn.BCEWithLogitsLoss(reduction='none')
        elif task_type == "regression":
            self.task_loss_fn = nn.MSELoss(reduction='none')
        else:
            raise ValueError("task_type must be 'classification' or 'regression'")

        # Optimizer (joint for predictor + critic)
        self.optimizer = optim.Adam(
            list(self.predictor.parameters()) + list(self.critic.parameters()),
            lr=self.lr
        )

    def train_baseline(self, X, y, epochs=50, batch_size=32, verbose=False):
        """Train only predictor on task loss (baseline)."""
        if X is None or y is None:
            raise ValueError("X and y must not be None")

        dataset = torch.utils.data.TensorDataset(
            torch.tensor(X, dtype=torch.float32),
            torch.tensor(y, dtype=torch.float32).unsqueeze(1)
        )
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        opt = optim.Adam(self.predictor.parameters(), lr=self.lr)
        loss_fn = nn.BCEWithLogitsLoss() if self.task_type == "classification" else nn.MSELoss()

        for epoch in range(epochs):
            total_loss = 0.0
            for Xb, yb in loader:
                Xb, yb = Xb.to(self.device), yb.to(self.device)
                opt.zero_grad()
                logits = self.predictor(Xb)
                loss = loss_fn(logits, yb)
                loss.backward()
                opt.step()
                total_loss += loss.item() * Xb.size(0)

            if verbose and (epoch+1) % max(1, epochs//5) == 0:
                print(f"[Baseline] Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(loader.dataset):.6f}")

    def fit_fair(self, X, y, X_cf, epochs=100, batch_size=32, verbose=True):
        """Train predictor + critic with fairness objective."""
        if X is None or y is None or X_cf is None:
            raise ValueError("X, y, and X_cf must not be None")

        dataset = torch.utils.data.TensorDataset(
            torch.tensor(X, dtype=torch.float32),
            torch.tensor(y, dtype=torch.float32).unsqueeze(1),
            torch.tensor(X_cf, dtype=torch.float32)
        )
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        for epoch in range(epochs):
            total_fair, total_task, total_disp, total_delta = 0, 0, 0, 0

            for Xb, yb, Xcf in loader:
                Xb, yb, Xcf = Xb.to(self.device), yb.to(self.device), Xcf.to(self.device)
                self.optimizer.zero_grad()

                y_logit = self.predictor(Xb)
                y_logit_cf = self.predictor(Xcf)

                per_sample_loss = self.task_loss_fn(y_logit, yb)
                y_prob = torch.sigmoid(y_logit).squeeze(1)
                y_prob_cf = torch.sigmoid(y_logit_cf).squeeze(1)

                disparity = (y_prob - y_prob_cf).pow(2).unsqueeze(1)
                delta_pred = self.critic(Xb)

                fair_loss = (delta_pred * disparity * per_sample_loss).mean()
                fair_loss.backward()
                self.optimizer.step()

                n = Xb.size(0)
                total_fair += fair_loss.item() * n
                total_task += per_sample_loss.mean().item() * n
                total_disp += disparity.mean().item() * n
                total_delta += delta_pred.mean().item() * n

            if verbose:
                N = len(loader.dataset)
                print(f"Epoch {epoch+1}/{epochs}, "
                      f"Fair Loss: {total_fair/N:.6f}, "
                      f"Task Loss: {total_task/N:.6f}, "
                      f"Mean Disparity: {total_disp/N:.6f}, "
                      f"Mean Delta: {total_delta/N:.6f}")

    def predict_proba(self, X):
        """Return predicted probabilities."""
        if X is None:
            raise ValueError("X must not be None")

        self.predictor.eval()
        with torch.no_grad():
            logits = self.predictor(torch.tensor(X, dtype=torch.float32).to(self.device)).squeeze(1)
            probs = torch.sigmoid(logits).cpu().numpy()
        return probs

    def evaluate(self, X, X_cf, y, protected_index=-1):
        """
        Evaluate disparity, accuracy, and group fairness metrics.
        protected_index: column index of protected attribute in X (default last col).
        """
        if X is None or X_cf is None or y is None:
            raise ValueError("X, X_cf, and y must not be None")

        self.predictor.eval()
        with torch.no_grad():
            logits = self.predictor(torch.tensor(X, dtype=torch.float32).to(self.device)).squeeze(1)
            probs = torch.sigmoid(logits).cpu().numpy()
            preds = (probs > 0.5).astype(int)

            logits_cf = self.predictor(torch.tensor(X_cf, dtype=torch.float32).to(self.device)).squeeze(1)
            probs_cf = torch.sigmoid(logits_cf).cpu().numpy()

        disparity = (probs - probs_cf) ** 2
        overall_acc = accuracy_score(y, preds)

        if protected_index < 0 or protected_index >= X.shape[1]:
            warnings.warn("Invalid protected_index. Skipping group fairness metrics.")
            acc_by_group, mean_prob_by_group = {}, {}
        else:
            protected_vals = X[:, protected_index].astype(int)
            acc_by_group, mean_prob_by_group = {}, {}
            for g in np.unique(protected_vals):
                idx = protected_vals == g
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

    def train_with_fairness(self, X, y, X_cf, epochs=10, batch_size=128, verbose=True):
        """Train predictor + critic with fairness objective and return metrics per epoch."""
        if X is None or y is None or X_cf is None:
            raise ValueError("X, y, and X_cf must not be None")

        dataset = torch.utils.data.TensorDataset(
            torch.tensor(X, dtype=torch.float32),
            torch.tensor(y, dtype=torch.float32).unsqueeze(1),
            torch.tensor(X_cf, dtype=torch.float32)
        )
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        fair_losses, task_losses, disp_losses, delta_means = [], [], [], []

        for epoch in range(epochs):
            accum_fair, accum_task, accum_disp, accum_delta = 0.0, 0.0, 0.0, 0.0
            for X_batch, y_batch, X_cf_batch in loader:
                X_batch, y_batch, X_cf_batch = (
                    X_batch.to(self.device),
                    y_batch.to(self.device),
                    X_cf_batch.to(self.device)
                )

                self.optimizer.zero_grad()

                # predictor logits
                y_logit = self.predictor(X_batch)
                y_logit_cf = self.predictor(X_cf_batch)

                # per-sample task loss
                per_sample_loss = self.task_loss_fn(y_logit, y_batch)

                # disparity
                y_prob = torch.sigmoid(y_logit).squeeze(1)
                y_prob_cf = torch.sigmoid(y_logit_cf).squeeze(1)
                disparity = (y_prob - y_prob_cf).pow(2).unsqueeze(1)

                # critic
                delta_pred = self.critic(X_batch)

                # fairness loss
                per_sample_fair = delta_pred * disparity * per_sample_loss
                fair_loss = per_sample_fair.mean()

                # backprop
                fair_loss.backward()
                self.optimizer.step()

                # accumulate stats
                n = X_batch.size(0)
                accum_fair += fair_loss.item() * n
                accum_task += per_sample_loss.mean().item() * n
                accum_disp += disparity.mean().item() * n
                accum_delta += delta_pred.mean().item() * n

            N = len(loader.dataset)
            fair_losses.append(accum_fair / N)
            task_losses.append(accum_task / N)
            disp_losses.append(accum_disp / N)
            delta_means.append(accum_delta / N)

            if verbose:
                print(f"Epoch {epoch+1}/{epochs} | "
                      f"L_fair: {fair_losses[-1]:.6f} | "
                      f"Task: {task_losses[-1]:.6f} | "
                      f"Disparity: {disp_losses[-1]:.6f} | "
                      f"Delta: {delta_means[-1]:.6f}")

        return fair_losses, task_losses, disp_losses, delta_means
