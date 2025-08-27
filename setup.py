from setuptools import setup, find_packages

setup(
    name="credit_scoring_system",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "xgboost>=1.5.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "PyYAML>=6.0",
        "optbinning>=0.15.0",
        # SHAP là tùy chọn
        # "shap>=0.40.0",
    ],
    python_requires=">=3.8",
    author="Credit Scoring Team",
    description="Hệ thống xây dựng các mô hình chấm điểm tín dụng sử dụng XGBoost"
)
