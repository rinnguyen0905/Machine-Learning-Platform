import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

def calculate_metrics(y_true, y_pred_proba, threshold=0.5):
    """
    Tính toán các chỉ số hiệu suất cho mô hình chấm điểm tín dụng
    
    Parameters:
    -----------
    y_true : array-like
        Giá trị thực
    y_pred_proba : array-like
        Xác suất dự đoán
    threshold : float, optional
        Ngưỡng để chuyển xác suất thành phân loại nhị phân
        
    Returns:
    --------
    dict
        Dictionary chứa các chỉ số hiệu suất
    """
    y_pred = (y_pred_proba >= threshold).astype(int)
    
    # Tính AUC-ROC
    auc = roc_auc_score(y_true, y_pred_proba)
    
    # Tính Gini từ AUC
    gini = 2 * auc - 1
    
    # Tính KS statistic
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    ks_statistic = max(tpr - fpr)
    
    # Tính Confusion Matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # Tính precision, recall, accuracy
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    
    # Tính F1 score
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    # Tạo dictionary kết quả
    metrics = {
        'AUC': auc,
        'Gini': gini,
        'KS_statistic': ks_statistic,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1_score': f1,
        'True_Negatives': tn,
        'False_Positives': fp,
        'False_Negatives': fn,
        'True_Positives': tp
    }
    
    return metrics

def plot_roc_curve(y_true, y_pred_proba):
    """
    Vẽ đường cong ROC
    
    Parameters:
    -----------
    y_true : array-like
        Giá trị thực
    y_pred_proba : array-like
        Xác suất dự đoán
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    auc = roc_auc_score(y_true, y_pred_proba)
    gini = 2 * auc - 1
    
    plt.plot(fpr, tpr, label=f'AUC = {auc:.4f}, Gini = {gini:.4f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)

def plot_ks_curve(y_true, y_pred_proba):
    """
    Vẽ đường cong KS (Kolmogorov-Smirnov)
    
    Parameters:
    -----------
    y_true : array-like
        Giá trị thực
    y_pred_proba : array-like
        Xác suất dự đoán
    """
    # Tính toán các tỷ lệ
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    
    # Tính KS
    ks_values = tpr - fpr
    max_ks_idx = np.argmax(ks_values)
    max_ks = ks_values[max_ks_idx]
    threshold_at_max_ks = thresholds[max_ks_idx]
    
    # Vẽ đường cong KS
    plt.plot(thresholds, tpr, label='True Positive Rate')
    plt.plot(thresholds, fpr, label='False Positive Rate')
    plt.plot(thresholds, ks_values, label=f'KS = {max_ks:.4f}')
    plt.axvline(x=threshold_at_max_ks, color='red', linestyle='--', 
                label=f'Threshold at max KS = {threshold_at_max_ks:.4f}')
    
    plt.xlabel('Threshold')
    plt.ylabel('Rate')
    plt.title('KS Curve')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)

def calculate_psi(expected, actual, buckets=10):
    """
    Tính chỉ số PSI (Population Stability Index)
    
    Parameters:
    -----------
    expected : array-like
        Phân phối mong đợi (ví dụ: điểm của tập huấn luyện)
    actual : array-like
        Phân phối thực tế (ví dụ: điểm của tập kiểm tra)
    buckets : int, optional
        Số lượng phân đoạn
        
    Returns:
    --------
    float
        Giá trị PSI
    """
    def psi_for_single_bin(e_perc, a_perc):
        """Tính PSI cho một bin"""
        if a_perc == 0:
            a_perc = 0.0001
        if e_perc == 0:
            e_perc = 0.0001
        return (a_perc - e_perc) * np.log(a_perc / e_perc)
    
    # Tạo các bin với khoảng đều nhau
    breakpoints = np.linspace(0, 1, buckets + 1)
    
    # Tính Histogram cho expected và actual
    e_hist, _ = np.histogram(expected, breakpoints)
    a_hist, _ = np.histogram(actual, breakpoints)
    
    # Tính tỷ lệ phần trăm
    e_perc = e_hist / sum(e_hist)
    a_perc = a_hist / sum(a_hist)
    
    # Tính PSI cho từng bin
    psi_values = [psi_for_single_bin(e, a) for e, a in zip(e_perc, a_perc)]
    
    # Tổng của tất cả giá trị PSI
    psi_total = sum(psi_values)
    
    return psi_total

def calculate_gini(auc):
    """
    Tính hệ số Gini từ AUC
    
    Parameters:
    -----------
    auc : float
        Giá trị AUC (Area Under ROC Curve)
        
    Returns:
    --------
    float
        Hệ số Gini
    """
    return 2 * auc - 1

def plot_score_distribution(scores, target, bins=50, figsize=(12, 6)):
    """
    Vẽ phân phối điểm theo nhóm tốt/xấu
    
    Parameters:
    -----------
    scores : array-like
        Điểm credit score của khách hàng 
    target : array-like
        Biến mục tiêu (0: good, 1: bad)
    bins : int, optional
        Số lượng bin cho histogram
    figsize : tuple, optional
        Kích thước của biểu đồ
    """
    plt.figure(figsize=figsize)
    
    # Tạo DataFrame
    df = pd.DataFrame({'Score': scores, 'Target': target})
    
    # Vẽ phân phối cho nhóm tốt (0)
    sns.histplot(df[df['Target'] == 0]['Score'], 
                 bins=bins, alpha=0.5, color='green', label='Good', kde=True)
    
    # Vẽ phân phối cho nhóm xấu (1)
    sns.histplot(df[df['Target'] == 1]['Score'], 
                 bins=bins, alpha=0.5, color='red', label='Bad', kde=True)
    
    plt.title('Score Distribution by Target')
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    return plt
