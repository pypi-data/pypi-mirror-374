__version__ = "2.0.4"

# 패키지 정보
__author__ = "BAEM1N, Teddy Lee"
__email__ = "baemin.dev@gmail.com, teddylee777@gmail.com"
__description__ = "mySUNI CDS - 데이터 과학 교육용 라이브러리"
__url__ = "https://github.com/braincrew/cds"

# 주요 모듈 import
from .cds import *
from .utils import *
from . import skada

# 패키지 레벨에서 사용할 수 있는 주요 함수들
__all__ = [
    # 데이터셋 관련
    'list_data',
    'download_data',
    
    # 워크샵 관련
    'list_workshop', 
    'download_workshop',
    
    # 프로젝트 관련
    'download_project',
    'submit',
    'end_project',
    'update_project',
    
    # 유틸리티 관련
    'plot_error',
    'plot_all',
    'set_plot_error',
    'add_error',
    'remove_error',
    'clear_error',
    'set_plot_options',
    'summary',
    'rmsle',
    'gini',
    'check_error',
    'set_error_values',
    'convert_ipynb',
    'convert_ipynb_folder',
    'ModelPlot',
    'ErrorChecker',
    
    # SKADA 모듈
    'skada',
]
