# mySUNI CDS

[![PyPI version](https://badge.fury.io/py/mySUNI.svg)](https://badge.fury.io/py/mySUNI)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

mySUNI CDS는 데이터 과학 교육을 위한 Python 라이브러리입니다. 데이터셋 다운로드, 워크샵 자료 관리, 프로젝트 제출 등의 기능을 제공합니다.

## 주요 기능

### 📊 데이터셋 관리
- 다양한 교육용 데이터셋 목록 조회 및 다운로드
- 자동 데이터 폴더 생성 및 관리
- 인증이 필요한 데이터셋 자동 다운로드

### 🎓 워크샵 자료
- 워크샵 목록 조회
- 실습용 및 해설용 Jupyter 노트북 다운로드
- 로컬 및 서버 환경 지원

### 📝 프로젝트 제출
- 프로젝트 파일 자동 다운로드
- 결과 제출 및 자동 채점
- 최종 프로젝트 제출 기능

### 🛠 유틸리티 도구
- 머신러닝 모델 성능 시각화
- 다양한 평가 지표 지원 (MSE, RMSE, RMSLE, MAE, Gini)
- Jupyter 노트북 변환 도구
- 데이터프레임 요약 정보 제공

### 🎯 SKADA (도메인 적응 및 미니스카다)
- 도메인 적응 알고리즘 (CORAL, MMD)
- 미니스카다 문제 제출 시스템
- 자동 채점 및 검증 기능
- XGBoost 기반 모델 평가 도구

## 설치

```bash
pip install mySUNI
```

## 사용법

### 데이터셋 사용

```python
import mySUNI as ms

# 데이터셋 목록 조회
ms.list_data()

# 특정 데이터셋 다운로드
ms.download_data('타이타닉')

# 여러 데이터셋 다운로드
ms.download_data(['타이타닉', '보스턴 주택가격'])
```

### 워크샵 자료 사용

```python
# 워크샵 목록 조회
ms.list_workshop()

# 워크샵 실습 파일 다운로드
ms.download_workshop('mySUNI-WorkShop-01-StepWalk')

# 워크샵 해설 파일 다운로드
ms.download_workshop('mySUNI-WorkShop-01-StepWalk', sol=True)
```

### 프로젝트 제출

```python
# 프로젝트 정보 설정
class_info = {
    'edu_name': '데이터분석과정',
    'edu_rnd': '1',
    'edu_class': 'A'
}

# 프로젝트 다운로드
ms.download_project('프로젝트명', class_info, 'your-email@example.com')

# 결과 제출
ms.submit(submission_dataframe)

# 최종 프로젝트 제출
ms.end_project('이름', 'notebook.ipynb')
```

### 모델 성능 시각화

```python
from mySUNI.utils import plot_error, set_plot_error

# 평가 지표 설정
set_plot_error('rmse')

# 모델 성능 시각화
plot_error('Linear Regression', y_true, y_pred)
plot_error('Random Forest', y_true, y_pred2)

# 전체 모델 비교
ms.plot_all()
```

### 데이터 요약

```python
from mySUNI.utils import summary

# 데이터프레임 요약 정보
summary_info = summary(df)
print(summary_info)
```

### SKADA 도메인 적응

```python
from mysuni import skada

# 샘플 도메인 데이터 생성
X_source, X_target, y_source, y_target = skada.load_sample_domain_data()

# CORAL 도메인 적응
coral_adapter = skada.CORAL()
coral_adapter.fit(X_source, X_target)

# 데이터 변환
X_source_adapted = coral_adapter.transform(X_source, domain='source')
X_target_adapted = coral_adapter.transform(X_target, domain='target')

# 성능 평가
score = skada.domain_adaptation_score(X_source, X_target, y_source, y_target, coral_adapter)
print(f"정확도: {score['accuracy']:.4f}")

# 여러 방법 비교
results = skada.compare_domain_adapters(X_source, X_target, y_source, y_target)
print(results)
```

### 미니스카다 제출 시스템

```python
from mysuni.skada import SKADA

# SKADA 인스턴스 생성 (싱글톤 패턴)
skada = SKADA.instance()

# 미니스카다 1번 문제 답안 제출
skada.Q1_answer(X_test)
skada.Q2_1_answer(X_test, mu)
skada.Q2_2_answer(drop_cols)
skada.Q2_3_answer(function, result)
skada.Q3_1_answer(sm_X_train, sm_y_train, ada_X_train, ada_y_train)
skada.Q3_2_answer(best_hyper_parameters)

# 미니스카다 2번 문제 답안 제출
skada.Q4_1_answer(processed_data)
skada.Q4_2_answer(cleaned_data)
skada.Q4_3_answer(normalized_data, numerical_features)
skada.Q5_1_answer(feature_importance_list)
skada.Q5_2_answer(f_count, selected_features)
skada.Q6_1_answer(accuracy_1, accuracy_2)
skada.Q6_2_answer(train_indices, test_indices)

# XGBoost 모델 평가
macro_f1 = skada.train_and_evaluate_xgb_model(X_train, y_train, X_test, y_test)

# 혼동 행렬 시각화
skada.disp_confusion_matrix(X_train, y_train, X_test, y_test)
```

## API 참조

### 주요 함수

- `list_data()`: 사용 가능한 데이터셋 목록 조회
- `download_data(dataset_name)`: 데이터셋 다운로드
- `list_workshop()`: 워크샵 목록 조회
- `download_workshop(workshop_name, sol=False, local=False)`: 워크샵 자료 다운로드
- `download_project(project_name, class_info, email)`: 프로젝트 다운로드
- `submit(submission)`: 프로젝트 결과 제출
- `end_project(name, ipynb_file_path)`: 최종 프로젝트 제출

### 유틸리티 함수

- `plot_error(name, actual, prediction)`: 모델 성능 시각화
- `set_plot_error(error_type)`: 평가 지표 설정
- `summary(dataframe)`: 데이터프레임 요약 정보
- `convert_ipynb(from_file, to_file)`: 노트북 파일 변환

## 요구사항

- Python 3.7+
- pandas
- matplotlib
- seaborn
- scikit-learn
- jupyter
- requests
- tqdm
- ipywidgets
- xgboost

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여하기

버그 리포트, 기능 요청, 풀 리퀘스트는 언제나 환영합니다!

1. 이 저장소를 포크하세요
2. 기능 브랜치를 생성하세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`)
5. 풀 리퀘스트를 생성하세요

## 지원

문제가 있거나 질문이 있으시면 [GitHub Issues](https://github.com/braincrew/cds/issues)에 등록해 주세요.

## 작성자

- **BAEM1N** - *초기 작업* - [GitHub](https://github.com/baem1n)
- **Teddy Lee** - *개발 및 유지보수* - [GitHub](https://github.com/teddylee777)

## 🌐 API 제출 시스템

mySUNI v2.0.3부터 `https://skada.quest/api`로 답안을 자동 제출하는 시스템을 지원합니다.

### 환경 설정

```python
import os

# 학생 ID와 세션 ID 설정
os.environ['SKADA_STUDENT_ID'] = 'your_student_id'
os.environ['SKADA_SESSION_ID'] = 'your_session_id'
```

또는 Jupyter 노트북에서:

```python
%env SKADA_STUDENT_ID=your_student_id
%env SKADA_SESSION_ID=your_session_id
```

### 자동 제출

기존 답안 제출 방식과 동일하게 사용하면 자동으로 API 제출을 시도합니다:

```python
from mySUNI.skada import SKADA

skada_instance = SKADA.instance()

# Q4_1 답안 제출 (자동으로 API 제출 시도)
skada_instance.Q4_1_answer(merged_df)

# 제출 성공시: ✅ Q4_1 답안 제출 성공! 📊 점수: 85
# 제출 실패시: 📁 로컬 백업 저장 완료. 최종 제출을 위해선 런박스 상단의 제출버튼을 눌러주세요.
```

### 직접 API 호출

```python
from mySUNI.skada import submit_to_api, SubmissionError

try:
    result = submit_to_api(
        problem_id="Q4_1",
        answer_data=your_answer,
        student_id="your_id",
        session_id="session_001"
    )
    print(f"제출 결과: {result}")
except SubmissionError as e:
    print(f"제출 실패: {e}")
```

### 지원하는 데이터 타입

- **NumPy 배열**: 자동으로 base64 인코딩하여 전송
- **Pandas DataFrame/Series**: JSON 형식으로 직렬화
- **Python 기본 타입**: int, float, str, bool, list, dict
- **함수**: pickle로 직렬화하여 전송

### 백업 시스템

API 제출이 실패할 경우 자동으로 로컬 파일에 백업 저장됩니다:

- 네트워크 오류
- 서버 오류  
- 타임아웃 (30초)

백업 파일은 `submit/` 디렉토리에 저장되며, 런박스 상단의 제출 버튼으로 수동 제출할 수 있습니다.

## 변경 이력

### v2.0.3
- **🌐 API 제출 시스템 추가**: `https://skada.quest/api`로 자동 제출
- **📦 SKADA 모듈 통합**: 미니스카다 제출 시스템 통합
- **🔧 네트워크 오류 처리**: CDS 모듈 안정성 개선
- **📁 백업 시스템**: API 제출 실패시 로컬 백업 자동 저장

### v2.0.2
- 안정성 개선 및 버그 수정
- 의존성 업데이트

### v2.0.1
- 새로운 데이터셋 추가
- 워크샵 자료 업데이트

### v2.0.0
- 메이저 리팩토링
- 새로운 API 구조
- 성능 최적화
