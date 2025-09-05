from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from . import config

def ML_lr(X_train, y_train, X_val = None, y_val = None, random_seed = config.seed_value):
    if X_val is not None:
        # 初始化模型
        ML_model = LogisticRegression(max_iter=200, random_state = random_seed)
        # 训练模型
        ML_model.fit(X_train, y_train)

        # 预测
        y_train_pred_score = ML_model.predict_proba(X_train)[:, 1]
        y_val_pred_score = ML_model.predict_proba(X_val)[:, 1]

        y_train_pred = ML_model.predict(X_train)
        y_val_pred = ML_model.predict(X_val)

        # Testing dataset指标
        accuracy_val = accuracy_score(y_val, y_val_pred)
        precision_val = precision_score(y_val, y_val_pred, average='weighted')
        recall_val = recall_score(y_val, y_val_pred, average='weighted')
        f1_val = f1_score(y_val, y_val_pred, average='weighted')
        auc_val = roc_auc_score(y_val, y_val_pred_score)
        fpr, tpr, _ = roc_curve(y_val, y_val_pred_score)

        # Training dataset指标
        accuracy_train = accuracy_score(y_train, y_train_pred)
        precision_train = precision_score(y_train, y_train_pred, average='weighted')
        recall_train = recall_score(y_train, y_train_pred, average='weighted')
        f1_train = f1_score(y_train, y_train_pred, average='weighted')
        auc_train = roc_auc_score(y_train, y_train_pred_score)

        # 打印指标
        print(f'Logistic Regression:')
        print(f"Training dataset Accuracy: {accuracy_train:.4f}, Precision: {precision_train:.4f}, Recall: {recall_train:.4f}, F1-Score: {f1_train:.4f}, AUC:{auc_train:.4f}")
        print(f"Testing dataset Accuracy: {accuracy_val:.4f}, Precision: {precision_val:.4f}, Recall: {recall_val:.4f}, F1-Score: {f1_val:.4f}, AUC:{auc_val:.4f}")
        print("*" * 100)

        return ML_model,\
            {'auc_train': auc_train, 'accuracy_train':accuracy_train, 'precision_train': precision_train, 'recall_train': recall_train, 'f1_train': f1_train}, \
                {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
                    {'fpr':fpr, 'tpr':tpr}
    else:
        # 初始化模型
        ML_model = LogisticRegression(max_iter=200, random_state = random_seed)
        # 训练模型
        ML_model.fit(X_train, y_train)

        # 预测
        y_train_pred_score = ML_model.predict_proba(X_train)[:, 1]
        y_train_pred = ML_model.predict(X_train)

        # Training dataset指标
        accuracy_train = accuracy_score(y_train, y_train_pred)
        precision_train = precision_score(y_train, y_train_pred, average='weighted')
        recall_train = recall_score(y_train, y_train_pred, average='weighted')
        f1_train = f1_score(y_train, y_train_pred, average='weighted')
        auc_train = roc_auc_score(y_train, y_train_pred_score)

        # 打印指标
        print(f'Logistic Regression:')
        print(f"Training dataset Accuracy: {accuracy_train:.4f}, Precision: {precision_train:.4f}, Recall: {recall_train:.4f}, F1-Score: {f1_train:.4f}, AUC:{auc_train:.4f}")
        print("*" * 100)

        return ML_model


def ML_svm(X_train, y_train, X_val, y_val, random_seed = config.seed_value):
    # 初始化模型
    ML_model = SVC(probability=True, random_state = random_seed)
    # 训练模型
    ML_model.fit(X_train, y_train)

    # 预测
    y_train_pred_score = ML_model.predict_proba(X_train)[:, 1]
    y_val_pred_score = ML_model.predict_proba(X_val)[:, 1]

    y_train_pred = ML_model.predict(X_train)
    y_val_pred = ML_model.predict(X_val)

    # Testing dataset指标
    accuracy_val = accuracy_score(y_val, y_val_pred)
    precision_val = precision_score(y_val, y_val_pred, average='weighted')
    recall_val = recall_score(y_val, y_val_pred, average='weighted')
    f1_val = f1_score(y_val, y_val_pred, average='weighted')
    auc_val = roc_auc_score(y_val, y_val_pred_score)
    fpr, tpr, _ = roc_curve(y_val, y_val_pred_score)

    # Training dataset指标
    accuracy_train = accuracy_score(y_train, y_train_pred)
    precision_train = precision_score(y_train, y_train_pred, average='weighted')
    recall_train = recall_score(y_train, y_train_pred, average='weighted')
    f1_train = f1_score(y_train, y_train_pred, average='weighted')
    auc_train = roc_auc_score(y_train, y_train_pred_score)

    # 打印指标
    print(f'SVM:')
    print(f"Training dataset Accuracy: {accuracy_train:.4f}, Precision: {precision_train:.4f}, Recall: {recall_train:.4f}, F1-Score: {f1_train:.4f}, AUC:{auc_train:.4f}")
    print(f"Testing dataset Accuracy: {accuracy_val:.4f}, Precision: {precision_val:.4f}, Recall: {recall_val:.4f}, F1-Score: {f1_val:.4f}, AUC:{auc_val:.4f}")
    print("*" * 100)

    return ML_model,\
        {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
            {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
                {'fpr':fpr, 'tpr':tpr}

def ML_rf(X_train, y_train, X_val, y_val, random_seed = config.seed_value):
    # 初始化模型
    ML_model = RandomForestClassifier(n_estimators=300, random_state = random_seed)
    # 训练模型
    ML_model.fit(X_train, y_train)

    # 预测
    y_train_pred_score = ML_model.predict_proba(X_train)[:, 1]
    y_val_pred_score = ML_model.predict_proba(X_val)[:, 1]

    y_train_pred = ML_model.predict(X_train)
    y_val_pred = ML_model.predict(X_val)

    # Testing dataset指标
    accuracy_val = accuracy_score(y_val, y_val_pred)
    precision_val = precision_score(y_val, y_val_pred, average='weighted')
    recall_val = recall_score(y_val, y_val_pred, average='weighted')
    f1_val = f1_score(y_val, y_val_pred, average='weighted')
    auc_val = roc_auc_score(y_val, y_val_pred_score)
    fpr, tpr, _ = roc_curve(y_val, y_val_pred_score)

    # Training dataset指标
    accuracy_train = accuracy_score(y_train, y_train_pred)
    precision_train = precision_score(y_train, y_train_pred, average='weighted')
    recall_train = recall_score(y_train, y_train_pred, average='weighted')
    f1_train = f1_score(y_train, y_train_pred, average='weighted')
    auc_train = roc_auc_score(y_train, y_train_pred_score)

    # 打印指标
    print(f'RandomForestClassifier:')
    print(f"Training dataset Accuracy: {accuracy_train:.4f}, Precision: {precision_train:.4f}, Recall: {recall_train:.4f}, F1-Score: {f1_train:.4f}, AUC:{auc_train:.4f}")
    print(f"Testing dataset Accuracy: {accuracy_val:.4f}, Precision: {precision_val:.4f}, Recall: {recall_val:.4f}, F1-Score: {f1_val:.4f}, AUC:{auc_val:.4f}")
    print("*" * 100)

    return ML_model,\
        {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
            {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
                {'fpr':fpr, 'tpr':tpr}

def ML_ada(X_train, y_train, X_val, y_val, random_seed = config.seed_value):
    # 初始化模型
    ML_model = AdaBoostClassifier(random_state = random_seed)
    # 训练模型
    ML_model.fit(X_train, y_train)

    # 预测
    y_train_pred_score = ML_model.predict_proba(X_train)[:, 1]
    y_val_pred_score = ML_model.predict_proba(X_val)[:, 1]

    y_train_pred = ML_model.predict(X_train)
    y_val_pred = ML_model.predict(X_val)

    # Testing dataset指标
    accuracy_val = accuracy_score(y_val, y_val_pred)
    precision_val = precision_score(y_val, y_val_pred, average='weighted')
    recall_val = recall_score(y_val, y_val_pred, average='weighted')
    f1_val = f1_score(y_val, y_val_pred, average='weighted')
    auc_val = roc_auc_score(y_val, y_val_pred_score)
    fpr, tpr, _ = roc_curve(y_val, y_val_pred_score)

    # Training dataset指标
    accuracy_train = accuracy_score(y_train, y_train_pred)
    precision_train = precision_score(y_train, y_train_pred, average='weighted')
    recall_train = recall_score(y_train, y_train_pred, average='weighted')
    f1_train = f1_score(y_train, y_train_pred, average='weighted')
    auc_train = roc_auc_score(y_train, y_train_pred_score)

    # 打印指标
    print(f'AdaBoostClassifier:')
    print(f"Training dataset Accuracy: {accuracy_train:.4f}, Precision: {precision_train:.4f}, Recall: {recall_train:.4f}, F1-Score: {f1_train:.4f}, AUC:{auc_train:.4f}")
    print(f"Testing dataset Accuracy: {accuracy_val:.4f}, Precision: {precision_val:.4f}, Recall: {recall_val:.4f}, F1-Score: {f1_val:.4f}, AUC:{auc_val:.4f}")
    print("*" * 100)

    return ML_model,\
        {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
            {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
                {'fpr':fpr, 'tpr':tpr}

def ML_dt(X_train, y_train, X_val, y_val, random_seed = config.seed_value):
    # 初始化模型
    ML_model = DecisionTreeClassifier(random_state = random_seed)
    # 训练模型
    ML_model.fit(X_train, y_train)

    # 预测
    y_train_pred_score = ML_model.predict_proba(X_train)[:, 1]
    y_val_pred_score = ML_model.predict_proba(X_val)[:, 1]

    y_train_pred = ML_model.predict(X_train)
    y_val_pred = ML_model.predict(X_val)

    # Testing dataset指标
    accuracy_val = accuracy_score(y_val, y_val_pred)
    precision_val = precision_score(y_val, y_val_pred, average='weighted')
    recall_val = recall_score(y_val, y_val_pred, average='weighted')
    f1_val = f1_score(y_val, y_val_pred, average='weighted')
    auc_val = roc_auc_score(y_val, y_val_pred_score)
    fpr, tpr, _ = roc_curve(y_val, y_val_pred_score)

    # Training dataset指标
    accuracy_train = accuracy_score(y_train, y_train_pred)
    precision_train = precision_score(y_train, y_train_pred, average='weighted')
    recall_train = recall_score(y_train, y_train_pred, average='weighted')
    f1_train = f1_score(y_train, y_train_pred, average='weighted')
    auc_train = roc_auc_score(y_train, y_train_pred_score)

    # 打印指标
    print(f'DecisionTreeClassifier:')
    print(f"Training dataset Accuracy: {accuracy_train:.4f}, Precision: {precision_train:.4f}, Recall: {recall_train:.4f}, F1-Score: {f1_train:.4f}, AUC:{auc_train:.4f}")
    print(f"Testing dataset Accuracy: {accuracy_val:.4f}, Precision: {precision_val:.4f}, Recall: {recall_val:.4f}, F1-Score: {f1_val:.4f}, AUC:{auc_val:.4f}")
    print("*" * 100)

    return ML_model,\
        {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
            {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
                {'fpr':fpr, 'tpr':tpr}

def ML_knn(X_train, y_train, X_val, y_val, random_seed = config.seed_value):
    # 初始化模型
    ML_model = KNeighborsClassifier()
    # 训练模型
    ML_model.fit(X_train, y_train)

    # 预测
    y_train_pred_score = ML_model.predict_proba(X_train)[:, 1]
    y_val_pred_score = ML_model.predict_proba(X_val)[:, 1]

    y_train_pred = ML_model.predict(X_train)
    y_val_pred = ML_model.predict(X_val)

    # Testing dataset指标
    accuracy_val = accuracy_score(y_val, y_val_pred)
    precision_val = precision_score(y_val, y_val_pred, average='weighted')
    recall_val = recall_score(y_val, y_val_pred, average='weighted')
    f1_val = f1_score(y_val, y_val_pred, average='weighted')
    auc_val = roc_auc_score(y_val, y_val_pred_score)
    fpr, tpr, _ = roc_curve(y_val, y_val_pred_score)

    # Training dataset指标
    accuracy_train = accuracy_score(y_train, y_train_pred)
    precision_train = precision_score(y_train, y_train_pred, average='weighted')
    recall_train = recall_score(y_train, y_train_pred, average='weighted')
    f1_train = f1_score(y_train, y_train_pred, average='weighted')
    auc_train = roc_auc_score(y_train, y_train_pred_score)

    # 打印指标
    print(f'KNeighborsClassifier:')
    print(f"Training dataset Accuracy: {accuracy_train:.4f}, Precision: {precision_train:.4f}, Recall: {recall_train:.4f}, F1-Score: {f1_train:.4f}, AUC:{auc_train:.4f}")
    print(f"Testing dataset Accuracy: {accuracy_val:.4f}, Precision: {precision_val:.4f}, Recall: {recall_val:.4f}, F1-Score: {f1_val:.4f}, AUC:{auc_val:.4f}")
    print("*" * 100)

    return ML_model,\
        {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
            {'auc_val': auc_val, 'accuracy_val':accuracy_val, 'precision_val': precision_val, 'recall_val': recall_val, 'f1_val': f1_val}, \
                {'fpr':fpr, 'tpr':tpr}
