"""基本测试用例"""

from depchecker import DependencyChecker, quick_check

def test_dependency_checker():
    """测试DependencyChecker类"""
    # 测试一些常见的基础包
    requirements = {
        "requests": "2.25.0",  # 较低版本要求
        "setuptools": "50.0.0"
    }
    
    checker = DependencyChecker(requirements)
    
    # 检查所有依赖
    results = checker.check_all()
    assert isinstance(results, dict)
    
    # 检查是否包含所有要求的包
    assert all(pkg in results for pkg in requirements.keys())
    
    print("✓ DependencyChecker类测试通过")

def test_quick_check():
    """测试quick_check函数"""
    requirements = {
        "pip": "20.0.0",  # 很低的版本要求，应该都能满足
        "setuptools": "50.0.0"
    }
    
    # 测试不自动安装
    ready = quick_check(requirements, auto_install=False, verbose=False)
    assert isinstance(ready, bool)
    
    print("✓ quick_check函数测试通过")

def test_package_check():
    """测试单个包检查"""
    checker = DependencyChecker({})
    
    # 检查一个肯定存在的包
    installed, version, status = checker.check_package("pip")
    assert isinstance(installed, bool)
    assert isinstance(version, str)
    assert isinstance(status, str)
    
    print("✓ 单个包检查测试通过")

if __name__ == "__main__":
    test_dependency_checker()
    test_quick_check()
    test_package_check()
    print("🎉 所有测试通过！")