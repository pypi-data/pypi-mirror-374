"""
SKADA (Statistical Knowledge Adaptation for Domain Adaptation) 모듈
도메인 적응을 위한 통계적 지식 적응 기법들과 교육용 제출 시스템을 제공합니다.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix
from xgboost import XGBClassifier
import warnings
import os
import json
import pickle
import re
import requests
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Type, Callable, Any, Union, NamedTuple
from functools import wraps, partial
from sys import stderr
import inspect
from inspect import signature, Signature

# 경고 출력 함수
warn = partial(print, file=stderr)

# API 설정
SKADA_API_URL = "https://skada.quest/api/miniskada"
DEFAULT_TIMEOUT = 30

# Matplotlib 한글 설정
import seaborn as sns
import matplotlib
import matplotlib.figure as figure
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정 (시스템에 따라 다를 수 있음)
matplotlib.rcParams['axes.unicode_minus'] = False
try:
    # macOS/Linux용 한글 폰트 경로들
    font_paths = [
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Ubuntu
        '/System/Library/Fonts/AppleGothic.ttf',  # macOS
        '/System/Library/Fonts/Helvetica.ttc',  # macOS fallback
    ]
    
    font_path = None
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            break
    
    if font_path:
        font_name = fm.FontProperties(fname=font_path, size=10).get_name()
        plt.rc('font', family=font_name)
    else:
        # 시스템 기본 한글 폰트 사용
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Malgun Gothic', 'AppleGothic', 'NanumGothic']
except Exception:
    # 폰트 설정 실패시 기본 설정 유지
    pass


# =============================================================================
# API 제출 시스템
# =============================================================================

class SubmissionError(Exception):
    """제출 관련 오류"""
    pass


def serialize_data(data: Any) -> Dict[str, Any]:
    """
    다양한 데이터 타입을 JSON 직렬화 가능한 형태로 변환
    
    Args:
        data: 직렬화할 데이터
        
    Returns:
        Dict containing serialized data with type information
    """
    if isinstance(data, np.ndarray):
        return {
            "type": "numpy",
            "content": base64.b64encode(data.tobytes()).decode('utf-8'),
            "dtype": str(data.dtype),
            "shape": data.shape
        }
    elif isinstance(data, pd.DataFrame):
        return {
            "type": "dataframe", 
            "content": data.to_json(orient='records'),
            "columns": list(data.columns),
            "index": list(data.index)
        }
    elif isinstance(data, pd.Series):
        return {
            "type": "series",
            "content": data.to_json(),
            "name": data.name,
            "index": list(data.index)
        }
    elif isinstance(data, (list, tuple)):
        return {
            "type": "list" if isinstance(data, list) else "tuple",
            "content": [serialize_data(item)["content"] if isinstance(item, (np.ndarray, pd.DataFrame, pd.Series)) 
                       else item for item in data]
        }
    elif isinstance(data, dict):
        return {
            "type": "dict",
            "content": {k: serialize_data(v)["content"] if isinstance(v, (np.ndarray, pd.DataFrame, pd.Series)) 
                       else v for k, v in data.items()}
        }
    elif callable(data):
        # 함수의 경우 pickle로 직렬화
        return {
            "type": "function",
            "content": base64.b64encode(pickle.dumps(data)).decode('utf-8'),
            "name": getattr(data, '__name__', 'anonymous_function')
        }
    else:
        # 기본 JSON 직렬화 가능한 타입들 (int, float, str, bool, None)
        return {
            "type": "primitive",
            "content": data
        }


def submit_to_api(problem_id: str, answer_data: Any, email: str = None, 
                 session_id: str = None, metadata: Dict = None) -> Dict[str, Any]:
    """
    답안을 SKADA API 서버로 제출
    
    Args:
        problem_id: 문제 ID (예: "Q4_1", "Q5_2")
        answer_data: 제출할 답안 데이터
        email: 학생 이메일 주소
        session_id: 세션 ID
        metadata: 추가 메타데이터
        
    Returns:
        서버 응답 데이터
        
    Raises:
        SubmissionError: 제출 실패 시
    """
    # 이메일과 세션 ID 확인
    if email is None:
        email = os.environ.get('SKADA_EMAIL')
        if not email:
            raise SubmissionError("이메일 주소가 설정되지 않았습니다. SKADA.instance(email='your@email.com')으로 설정해주세요.")
    
    if session_id is None:
        session_id = os.environ.get('SKADA_SESSION_ID', f'session_{email.replace("@", "_").replace(".", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    # 데이터 직렬화
    serialized_data = serialize_data(answer_data)
    
    # 제출 페이로드 구성
    payload = {
        "email": email,
        "session_id": session_id,
        "problem_id": problem_id,
        "answer_data": serialized_data,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metadata": metadata or {}
    }
    
    try:
        # API 호출
        response = requests.post(
            f"{SKADA_API_URL}/submit",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "mySUNI-SKADA/2.0.3"
            },
            timeout=DEFAULT_TIMEOUT
        )
        
        # 응답 처리
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {problem_id} 답안 제출 성공!")
            if result.get('score') is not None:
                print(f"📊 점수: {result['score']}")
            if result.get('feedback'):
                print(f"💬 피드백: {result['feedback']}")
            return result
        else:
            error_msg = f"제출 실패 (HTTP {response.status_code})"
            try:
                error_detail = response.json().get('error', response.text)
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {response.text}"
            raise SubmissionError(error_msg)
            
    except requests.exceptions.Timeout:
        raise SubmissionError(f"제출 시간 초과 ({DEFAULT_TIMEOUT}초)")
    except requests.exceptions.ConnectionError:
        raise SubmissionError("서버 연결 실패. 네트워크 상태를 확인해주세요.")
    except requests.exceptions.RequestException as e:
        raise SubmissionError(f"제출 중 오류 발생: {str(e)}")


def submit_with_fallback(problem_id: str, answer_data: Any, files: List[str], 
                        submit_root: str, skada_instance=None, **kwargs) -> Dict[str, Any]:
    """
    API 제출을 시도하고, 실패 시 로컬 파일로 백업 저장
    
    Args:
        problem_id: 문제 ID
        answer_data: 답안 데이터
        files: 저장할 파일 목록 (백업용)
        submit_root: 로컬 저장 디렉토리
        skada_instance: SKADA 인스턴스 (이메일/세션 정보 가져오기용)
        **kwargs: submit_to_api에 전달할 추가 인자
        
    Returns:
        제출 결과
    """
    try:
        # SKADA 인스턴스에서 이메일과 세션 ID 가져오기
        if skada_instance and hasattr(skada_instance, 'email') and skada_instance.email:
            kwargs.setdefault('email', skada_instance.email)
            kwargs.setdefault('session_id', skada_instance.session_id)
        
        # API 제출 시도
        return submit_to_api(problem_id, answer_data, **kwargs)
    except SubmissionError as e:
        warn(f"⚠️  API 제출 실패: {e}")
        warn("📁 로컬 파일로 백업 저장합니다...")
        
        # 로컬 백업 저장
        os.makedirs(submit_root, exist_ok=True)
        
        if len(files) == 1:
            file_path = os.path.join(submit_root, files[0])
            
            if files[0].endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(answer_data, f, ensure_ascii=False, indent=2, default=str)
            elif files[0].endswith('.npy'):
                np.save(file_path, answer_data)
            elif files[0].endswith('.pkl'):
                with open(file_path, 'wb') as f:
                    pickle.dump(answer_data, f)
            elif files[0].endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(answer_data))
        
        print(f"💾 로컬 백업 완료: {submit_root}")
        return {"status": "backup_saved", "location": submit_root}


class DomainAdapter(BaseEstimator, TransformerMixin):
    """
    도메인 적응을 위한 기본 클래스
    """
    
    def __init__(self, method='coral', n_components=None):
        """
        Parameters:
        -----------
        method : str, default='coral'
            적응 방법 ('coral', 'mmd', 'dann')
        n_components : int, optional
            차원 축소할 컴포넌트 수
        """
        self.method = method
        self.n_components = n_components
        self.scaler_source = StandardScaler()
        self.scaler_target = StandardScaler()
        self.pca = None
        
    def fit(self, X_source, X_target):
        """
        소스와 타겟 도메인 데이터로 적응기를 학습합니다.
        
        Parameters:
        -----------
        X_source : array-like, shape (n_source_samples, n_features)
            소스 도메인 데이터
        X_target : array-like, shape (n_target_samples, n_features)
            타겟 도메인 데이터
        """
        X_source = np.array(X_source)
        X_target = np.array(X_target)
        
        # 데이터 정규화
        self.scaler_source.fit(X_source)
        self.scaler_target.fit(X_target)
        
        X_source_scaled = self.scaler_source.transform(X_source)
        X_target_scaled = self.scaler_target.transform(X_target)
        
        # 차원 축소 (선택적)
        if self.n_components:
            self.pca = PCA(n_components=self.n_components)
            X_combined = np.vstack([X_source_scaled, X_target_scaled])
            self.pca.fit(X_combined)
        
        # 도메인 적응 방법별 학습
        if self.method == 'coral':
            self._fit_coral(X_source_scaled, X_target_scaled)
        elif self.method == 'mmd':
            self._fit_mmd(X_source_scaled, X_target_scaled)
        else:
            warnings.warn(f"Method '{self.method}' not implemented. Using identity transformation.")
        
        return self
    
    def transform(self, X, domain='source'):
        """
        데이터를 적응된 공간으로 변환합니다.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
            변환할 데이터
        domain : str, default='source'
            데이터의 도메인 ('source' 또는 'target')
        
        Returns:
        --------
        X_transformed : array-like, shape (n_samples, n_features_out)
            변환된 데이터
        """
        X = np.array(X)
        
        # 정규화
        if domain == 'source':
            X_scaled = self.scaler_source.transform(X)
        else:
            X_scaled = self.scaler_target.transform(X)
        
        # 차원 축소
        if self.pca:
            X_scaled = self.pca.transform(X_scaled)
        
        # 도메인 적응 변환
        if self.method == 'coral' and hasattr(self, 'coral_transform_'):
            X_transformed = self._transform_coral(X_scaled, domain)
        else:
            X_transformed = X_scaled
        
        return X_transformed
    
    def _fit_coral(self, X_source, X_target):
        """CORAL (Correlation Alignment) 방법으로 학습"""
        # 공분산 행렬 계산
        cov_source = np.cov(X_source.T) + np.eye(X_source.shape[1]) * 1e-6
        cov_target = np.cov(X_target.T) + np.eye(X_target.shape[1]) * 1e-6
        
        # CORAL 변환 행렬 계산
        try:
            # Cholesky 분해를 사용한 안정적인 계산
            L_source = np.linalg.cholesky(cov_source)
            L_target = np.linalg.cholesky(cov_target)
            
            self.coral_transform_ = np.linalg.solve(L_source, L_target)
        except np.linalg.LinAlgError:
            # Cholesky 분해 실패시 SVD 사용
            U_s, S_s, Vt_s = np.linalg.svd(cov_source)
            U_t, S_t, Vt_t = np.linalg.svd(cov_target)
            
            sqrt_source_inv = U_s @ np.diag(1.0 / np.sqrt(S_s + 1e-6)) @ Vt_s
            sqrt_target = U_t @ np.diag(np.sqrt(S_t)) @ Vt_t
            
            self.coral_transform_ = sqrt_source_inv @ sqrt_target
    
    def _transform_coral(self, X, domain):
        """CORAL 변환 적용"""
        if domain == 'source':
            return X @ self.coral_transform_.T
        else:
            return X
    
    def _fit_mmd(self, X_source, X_target):
        """MMD (Maximum Mean Discrepancy) 방법으로 학습"""
        # 간단한 MMD 기반 변환 (실제로는 더 복잡한 최적화 필요)
        mean_source = np.mean(X_source, axis=0)
        mean_target = np.mean(X_target, axis=0)
        self.mmd_shift_ = mean_target - mean_source


class CORAL(DomainAdapter):
    """
    CORAL (Correlation Alignment) 도메인 적응
    """
    
    def __init__(self, n_components=None):
        super().__init__(method='coral', n_components=n_components)


class MMD(DomainAdapter):
    """
    MMD (Maximum Mean Discrepancy) 도메인 적응
    """
    
    def __init__(self, n_components=None):
        super().__init__(method='mmd', n_components=n_components)


def domain_adaptation_score(X_source, X_target, y_source, y_target, adapter=None):
    """
    도메인 적응 성능을 평가합니다.
    
    Parameters:
    -----------
    X_source : array-like
        소스 도메인 특성
    X_target : array-like
        타겟 도메인 특성
    y_source : array-like
        소스 도메인 레이블
    y_target : array-like
        타겟 도메인 레이블
    adapter : DomainAdapter, optional
        사용할 도메인 적응기
    
    Returns:
    --------
    score : dict
        평가 점수들
    """
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.ensemble import RandomForestClassifier
    
    if adapter is None:
        adapter = CORAL()
    
    # 도메인 적응기 학습
    adapter.fit(X_source, X_target)
    
    # 데이터 변환
    X_source_adapted = adapter.transform(X_source, domain='source')
    X_target_adapted = adapter.transform(X_target, domain='target')
    
    # 분류기 학습 (소스 도메인)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_source_adapted, y_source)
    
    # 타겟 도메인에서 예측
    y_pred = clf.predict(X_target_adapted)
    
    # 성능 평가
    accuracy = accuracy_score(y_target, y_pred)
    f1 = f1_score(y_target, y_pred, average='weighted')
    
    return {
        'accuracy': accuracy,
        'f1_score': f1,
        'adapter': adapter.__class__.__name__
    }


def compare_domain_adapters(X_source, X_target, y_source, y_target):
    """
    여러 도메인 적응 방법을 비교합니다.
    
    Parameters:
    -----------
    X_source : array-like
        소스 도메인 특성
    X_target : array-like
        타겟 도메인 특성
    y_source : array-like
        소스 도메인 레이블
    y_target : array-like
        타겟 도메인 레이블
    
    Returns:
    --------
    results : pd.DataFrame
        비교 결과
    """
    adapters = [
        ('No Adaptation', None),
        ('CORAL', CORAL()),
        ('MMD', MMD()),
    ]
    
    results = []
    
    for name, adapter in adapters:
        if adapter is None:
            # 적응 없이 직접 학습
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import accuracy_score, f1_score
            
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_source, y_source)
            y_pred = clf.predict(X_target)
            
            accuracy = accuracy_score(y_target, y_pred)
            f1 = f1_score(y_target, y_pred, average='weighted')
            
            results.append({
                'Method': name,
                'Accuracy': accuracy,
                'F1_Score': f1
            })
        else:
            score = domain_adaptation_score(X_source, X_target, y_source, y_target, adapter)
            results.append({
                'Method': name,
                'Accuracy': score['accuracy'],
                'F1_Score': score['f1_score']
            })
    
    return pd.DataFrame(results)


# 편의 함수들
def load_sample_domain_data():
    """
    샘플 도메인 적응 데이터를 생성합니다.
    """
    np.random.seed(42)
    
    # 소스 도메인 (정규분포)
    X_source = np.random.normal(0, 1, (200, 10))
    y_source = (X_source[:, 0] + X_source[:, 1] > 0).astype(int)
    
    # 타겟 도메인 (분포가 약간 다름)
    X_target = np.random.normal(0.5, 1.2, (150, 10))
    y_target = (X_target[:, 0] + X_target[:, 1] > 0.5).astype(int)
    
    return X_source, X_target, y_source, y_target


def plot_domain_comparison(X_source, X_target, adapter=None, feature_indices=[0, 1]):
    """
    도메인 적응 전후의 데이터 분포를 시각화합니다.
    """
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 원본 데이터
    axes[0].scatter(X_source[:, feature_indices[0]], X_source[:, feature_indices[1]], 
                   alpha=0.6, label='Source', color='blue')
    axes[0].scatter(X_target[:, feature_indices[0]], X_target[:, feature_indices[1]], 
                   alpha=0.6, label='Target', color='red')
    axes[0].set_title('Original Data')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 적응된 데이터
    if adapter is not None:
        adapter.fit(X_source, X_target)
        X_source_adapted = adapter.transform(X_source, domain='source')
        X_target_adapted = adapter.transform(X_target, domain='target')
        
        axes[1].scatter(X_source_adapted[:, feature_indices[0]], X_source_adapted[:, feature_indices[1]], 
                       alpha=0.6, label='Source (Adapted)', color='blue')
        axes[1].scatter(X_target_adapted[:, feature_indices[0]], X_target_adapted[:, feature_indices[1]], 
                       alpha=0.6, label='Target (Adapted)', color='red')
        axes[1].set_title(f'After {adapter.__class__.__name__} Adaptation')
    else:
        axes[1].text(0.5, 0.5, 'No Adapter Provided', 
                    transform=axes[1].transAxes, ha='center', va='center')
        axes[1].set_title('No Adaptation')
    
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


# ===== 제출 및 캐싱 시스템 =====

def type_checker(obj, type_hint: Type) -> bool:
    """타입 체크 함수"""
    try:
        if getattr(type_hint, "_name", None) is not None:
            if type_hint._name == "Any":
                return True
            elif type_hint._name == "List":
                return all(type_checker(sub, type_hint.__args__[0]) for sub in obj)
            elif type_hint._name == "Tuple":
                return all(type_checker(sub, sub_type) for sub, sub_type in zip(obj, type_hint.__args__))
            elif type_hint._name == "Callable":
                return callable(obj)
        else:
            return isinstance(obj, type_hint)
    except:
        pass
    return False


def submit(files: List[str], submit_root: str):
    """제출 데코레이터"""
    os.makedirs(submit_root, exist_ok=True)

    for file in files:
        file_path = os.path.join(submit_root, file)
        if not os.path.isfile(file_path):
            with open(file_path, 'w'):
                pass

    def wrapping(func):
        sig = signature(func)
        type_map = {
            name: param.annotation for name, param in sig.parameters.items()
            if param.annotation is not Signature.empty
        }

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 타입 체크
            params = sig.bind_partial(self, *args, **kwargs)
            for name, annotation in type_map.items():
                assert name in params.arguments and type_checker(params.arguments[name], annotation), \
                       f"{name}을 {annotation} 타입으로 제출 바랍니다."

            self.path = [Path(os.path.join(submit_root, file)) for file in files] 
            
            # 실제 함수 실행
            result = func(self, *args, **kwargs)
            
            # 문제 ID 추출 (함수명에서)
            problem_id = func.__name__.replace('_answer', '').replace('_', '_')
            
            # 답안 데이터 결정 (첫 번째 인자 또는 여러 인자를 튜플로)
            if len(args) == 1:
                answer_data = args[0]
            else:
                answer_data = args
            
            # API 제출 시도 (실패 시 로컬 백업)
            try:
                submission_result = submit_with_fallback(
                    problem_id=problem_id,
                    answer_data=answer_data,
                    files=files,
                    submit_root=submit_root,
                    skada_instance=self,  # SKADA 인스턴스 전달
                    metadata={
                        "function_name": func.__name__,
                        "args_count": len(args),
                        "file_names": files
                    }
                )
                
                if submission_result.get("status") == "backup_saved":
                    warn("📁 로컬 백업 저장 완료. 최종 제출을 위해선 런박스 상단의 제출버튼을 눌러주세요.")
                
                return submission_result
            except Exception as e:
                warn(f"제출 중 예상치 못한 오류: {e}")
                warn("📁 로컬 백업으로 저장합니다. 최종 제출을 위해선 런박스 상단의 제출버튼을 눌러주세요.")
                return {"status": "error", "error": str(e)}
        
        return wrapper

    return wrapping


class Singleton:
    """싱글톤 패턴 구현"""
    __instance = None

    def __init__(self) -> None:
        assert type(self).__instance is ..., ".instance() 메소드를 이용하여 생성해주세요."

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kwargs):
        cls.__instance = ...
        cls.__instance = cls(*args, **kwargs)
        cls.instance = cls.__getInstance
        return cls.__instance


# ===== 유틸리티 함수들 =====

def disp_confusion_matrix(X_train, y_train, X_test, y_test):
    """혼동 행렬 시각화"""
    model = XGBClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    conf_mat = confusion_matrix(y_test, y_pred)
    df_conf_mat = pd.DataFrame(conf_mat, columns=['Prediction_Fail', 'Prediction_Pass'], 
                              index=['Real_Fail', 'Real_Pass'])
    plt.figure(figsize=(10, 7))
    plt.title('Confusion Matrix for XGBoost Classifier')
    sns.heatmap(df_conf_mat, annot=True, fmt='g')
    plt.show()


def draw_histograms(variables: pd.DataFrame, n_rows: int, n_cols: int):
    """히스토그램 그리기"""
    fig = plt.figure(figsize=(20, 10))
    for i, var_name in enumerate(variables):
        ax = fig.add_subplot(n_rows, n_cols, i+1)
        variables.iloc[:, i].hist(bins=10, ax=ax)
        ax.set_title(var_name + " Distribution")
    fig.tight_layout()
    plt.show()


def train_and_evaluate_xgb_model(X_train, y_train, X_test, y_test):
    """XGBoost 모델 학습 및 평가"""
    model = XGBClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    positive_tp = np.sum((y_pred == 1) & (y_test == 1))
    positive_fp = np.sum((y_pred == 1) & (y_test != 1))
    positive_fn = np.sum((y_pred != 1) & (y_test == 1))

    negative_tp = np.sum((y_pred == 0) & (y_test == 0))
    negative_fp = np.sum((y_pred == 0) & (y_test != 0))
    negative_fn = np.sum((y_pred != 0) & (y_test == 0))

    positive_precision = positive_tp / (positive_tp + positive_fp)
    positive_recall = positive_tp / (positive_tp + positive_fn)

    negative_precision = negative_tp / (negative_tp + negative_fp)
    negative_recall = negative_tp / (negative_tp + negative_fn)

    positive_f1 = 2 * (positive_precision * positive_recall) / (positive_precision + positive_recall)
    negative_f1 = 2 * (negative_precision * negative_recall) / (negative_precision + negative_recall)

    macro_f1 = (positive_f1 + negative_f1) / 2
    
    total_tp = positive_tp + negative_tp
    total_fp = positive_fp + negative_fp
    total_fn = positive_fn + negative_fn
    micro_precision = total_tp / (total_tp + total_fp)
    micro_recall = total_tp / (total_tp + total_fn)
    micro_f1 = 2 * (micro_precision * micro_recall) / (micro_precision + micro_recall)
    
    print(f"Pass (Class 1): {(y_test == 1).sum()} Samples".title())
    print(f"TP: {positive_tp}")
    print(f"FP: {positive_fp}")
    print(f"FN: {positive_fn}")
    print("#" * 100)
    print(f"Fail (Class 0): {(y_test == 0).sum()} Samples".title())
    print(f"TP: {negative_tp}")
    print(f"FP: {negative_fp}")
    print(f"FN: {negative_fn}")
    print("#" * 100)
    print(f'Micro F1 Score: {micro_f1:.4f}')
    print(f'Macro F1 Score: {macro_f1:.4f}')
    
    return macro_f1


def check_Q2_2_answer(submit):
    """Q2_2 답안 체크 함수"""
    answer = ['s242', 's281', 's285', 's161', 's84', 's290', 's167', 's227', 's293', 's268', 's150', 's16', 's74', 's278', 's159', 's296', 's106', 's243', 's83', 's279', 's277', 's26', 's87', 's238', 's297', 's32', 's75', 's151', 's231', 's267', 's264', 's276', 's157', 's235', 's295', 's228', 's239', 's284', 's76', 's292', 's230', 's233', 's288', 's291', 's82', 's287', 's97', 's229', 's299', 's85', 's109', 's80', 's273', 's274', 's149', 's275', 's282', 's283', 's79', 's91', 's176', 's294', 's269', 's154', 's300', 's286', 's179', 's88', 's240', 's166', 's236', 's164', 's73', 's298']
    assert set(answer) == set(submit), "잘못 구하였으므로 다시 확인하시오."
    print("통과하였으므로 아래 답안 제출을 수행하시오.") 


# ===== SKADA 메인 클래스 =====

class SKADA(Singleton):
    """SKADA 메인 클래스 - 미니스카다 1번과 2번 문제 통합"""
    SUBMISSION = 'submit'
    
    def __init__(self, email: str = None, cache_root='.cache') -> None:
        super().__init__()
        self.cache_root = cache_root
        self.path: List[Path] = None
        self.email = email
        self.session_id = None
        
        # 이메일 설정 및 세션 ID 생성
        if email:
            self.email = email
            self.session_id = f"session_{email.replace('@', '_').replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"📧 SKADA 세션 시작: {email}")
            print(f"🔑 세션 ID: {self.session_id}")
        else:
            print("⚠️  이메일이 설정되지 않았습니다. SKADA.instance(email='your@email.com')으로 설정해주세요.")
    
    @classmethod
    def instance(cls, email: str = None):
        """
        SKADA 싱글톤 인스턴스 생성/반환
        
        Args:
            email: 학생 이메일 주소 (필수)
            
        Returns:
            SKADA 인스턴스
        """
        if not hasattr(cls, '_instance') or cls._instance is None:
            if not email:
                # 환경변수에서 이메일 확인
                email = os.environ.get('SKADA_EMAIL')
                if not email:
                    raise ValueError(
                        "이메일 주소가 필요합니다. 다음 중 하나의 방법을 사용하세요:\n"
                        "1. SKADA.instance(email='your@email.com')\n"
                        "2. os.environ['SKADA_EMAIL'] = 'your@email.com'"
                    )
            cls._instance = cls(email=email)
        elif email and cls._instance.email != email:
            # 다른 이메일로 새 인스턴스 생성
            cls._instance = cls(email=email)
        
        return cls._instance

    # ===== 미니스카다 1번 문제들 =====
    
    @submit(['data1.npy'], SUBMISSION)
    def Q1_answer(self, X_test):
        """Q1 답안 제출"""
        np.save(self.path[0], X_test)

    @submit(['data2-1.npy', 'data2-1_2.npy'], SUBMISSION)
    def Q2_1_answer(self, X_test, mu):
        """Q2-1 답안 제출"""
        np.save(self.path[0], X_test)
        np.save(self.path[1], mu)

    @submit(['data2-2.txt'], SUBMISSION)
    def Q2_2_answer(self, drop_cols):
        """Q2-2 답안 제출"""
        with open(self.path[0], "w") as f:
            f.write(" ".join(drop_cols))

    @submit(['result2-3.pkl', 'result2-3.npy'], SUBMISSION)
    def Q2_3_answer(self, function, result):
        """Q2-3 답안 제출"""
        with open(self.path[0], "wb") as f:
            pickle.dump(function, f)
        np.save(self.path[1], result)
            
    @submit(['data3-1.txt'], SUBMISSION)
    def Q3_1_answer(self, resampled_sm_X_train, resampled_sm_y_train, resampled_ada_X_train, resampled_ada_y_train):
        """Q3-1 답안 제출"""
        with open(self.path[0], 'w') as f:
            f.write(str(len(resampled_sm_y_train) + len(resampled_ada_y_train)))

    @submit(['best_hyper_parameters.json'], SUBMISSION)
    def Q3_2_answer(self, best_hyper_parameters):
        """Q3-2 답안 제출"""
        with open(self.path[0], "w") as f:
            json.dump(best_hyper_parameters, f)

    # ===== 미니스카다 2번 문제들 =====
    
    @submit(['Q4_1.json'], SUBMISSION)
    def Q4_1_answer(self, answer):
        """Q4-1 답안 제출"""
        with self.path[0].open('w') as fd:
            a = answer.shape == (7043, 21)
            b = '6840-RESVD' not in answer['customerID'].tolist()
            json.dump(int(a and b), fd)
            
    @submit(['Q4_2.json'], SUBMISSION)
    def Q4_2_answer(self, answer):
        """Q4-2 답안 제출"""
        with self.path[0].open('w') as fd:
            a = answer['TotalCharges'].dtype == 'float64'
            b = not answer['TotalCharges'].isnull().any()
            json.dump(int(a and b), fd) 

    @submit(['Q4_3.json'], SUBMISSION)
    def Q4_3_answer(self, answer, numerical_features):
        """Q4-3 답안 제출"""
        with self.path[0].open('w') as fd:
            a = answer.shape == (7043, 29)
            b = sum(answer[numerical_features].max().round() == 1.0) == 3
            c = sum(answer[numerical_features].min().round() == 0.0) == 3
            d = 'customerID' in answer.columns
            e = 'SeniorCitizen' in answer.columns
            json.dump(int(a and b and c and d and e), fd) 
            
    @submit(['Q5_1.json'], SUBMISSION)
    def Q5_1_answer(self, answer):
        """Q5-1 답안 제출"""
        with self.path[0].open('w') as fd:
            a = len(answer) == 27
            b = True
            for i in range(26):
                if i == 0:
                    b = answer[i][1] >= answer[i+1][1]
                else:
                    b = (answer[i][1] >= answer[i+1][1]) and b
            
            json.dump(int(a and b), fd)
    
    @submit(['Q5_2.json'], SUBMISSION)
    def Q5_2_answer(self, f_count, f):
        """Q5-2 답안 제출"""
        with self.path[0].open('w') as fd:
            a = len(f) == f_count == 11
            b = f[0] == 'Contract_Month-to-month'
            c = f[-1] == 'OnlineSecurity'
            json.dump(int(a and b and c), fd)
    
    @submit(['Q6_1.json'], SUBMISSION)
    def Q6_1_answer(self, answer_1, answer_2):
        """Q6-1 답안 제출"""
        with self.path[0].open('w') as fd:
            a = round(answer_1, 3) == 0.806
            b = round(answer_2, 3) == 0.99
            json.dump(int(a and b), fd)
    
    @submit(['Q6_2.json'], SUBMISSION)
    def Q6_2_answer(self, answer_1, answer_2):
        """Q6-2 답안 제출"""
        with self.path[0].open('w') as fd:
            a = len(answer_1) == 580
            b = len(answer_2) == 133
            json.dump(int(a and b), fd)


# 모듈 레벨 변수들
__all__ = [
    # 도메인 적응 관련
    'DomainAdapter',
    'CORAL', 
    'MMD',
    'domain_adaptation_score',
    'compare_domain_adapters',
    'load_sample_domain_data',
    'plot_domain_comparison',
    
    # SKADA 시스템 관련
    'SKADA',
    'Singleton',
    'submit',
    'type_checker',
    
    # API 제출 시스템
    'SubmissionError',
    'serialize_data',
    'submit_to_api',
    'submit_with_fallback',
    
    # 유틸리티 함수들
    'disp_confusion_matrix',
    'draw_histograms',
    'train_and_evaluate_xgb_model',
    'check_Q2_2_answer',
]
