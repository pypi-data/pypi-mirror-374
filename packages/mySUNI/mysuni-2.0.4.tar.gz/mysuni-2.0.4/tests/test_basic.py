"""
기본 테스트 모듈
"""
import pytest
import mySUNI


def test_version():
    """버전 정보 테스트"""
    assert hasattr(mySUNI, '__version__')
    assert isinstance(mySUNI.__version__, str)


def test_imports():
    """주요 모듈 import 테스트"""
    # 데이터셋 관련 함수들
    assert hasattr(mySUNI, 'list_data')
    assert hasattr(mySUNI, 'download_data')
    
    # 워크샵 관련 함수들
    assert hasattr(mySUNI, 'list_workshop')
    assert hasattr(mySUNI, 'download_workshop')
    
    # 프로젝트 관련 함수들
    assert hasattr(mySUNI, 'download_project')
    assert hasattr(mySUNI, 'submit')
    assert hasattr(mySUNI, 'end_project')


def test_utils_imports():
    """유틸리티 함수 import 테스트"""
    assert hasattr(mySUNI, 'plot_error')
    assert hasattr(mySUNI, 'summary')
    assert hasattr(mySUNI, 'rmsle')
    assert hasattr(mySUNI, 'gini')


def test_classes():
    """클래스 import 테스트"""
    assert hasattr(mySUNI, 'ModelPlot')
    assert hasattr(mySUNI, 'ErrorChecker')


if __name__ == '__main__':
    pytest.main([__file__])
