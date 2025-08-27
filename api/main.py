from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from typing import List

# Thêm thư mục gốc vào path
sys.path.append(str(Path(__file__).parents[1]))

from src.models.application_scorecard import ApplicationScorecard
from src.models.behavior_scorecard import BehaviorScorecard
from src.models.collections_scoring import CollectionsScoring
from src.models.desertion_scoring import DesertionScoring
from src.scorecard.scorecard_builder import ScorecardBuilder
from api.request_examples import (
    APPLICATION_EXAMPLE, 
    BEHAVIOR_EXAMPLE, 
    COLLECTIONS_EXAMPLE, 
    DESERTION_EXAMPLE
)

app = FastAPI(
    title="Credit Scoring API",
    description="API cho hệ thống chấm điểm tín dụng",
    version="1.0.0"
)

# Load models
application_model = ApplicationScorecard()
behavior_model = BehaviorScorecard()
collections_model = CollectionsScoring()
desertion_model = DesertionScoring()

try:
    application_model.load_model()
    behavior_model.load_model()
    collections_model.load_model()
    desertion_model.load_model()
    print("All models loaded successfully")
except Exception as e:
    print(f"Error loading models: {e}")

# Pydantic models
class ApplicationData(BaseModel):
    """Dữ liệu input cho Application Scorecard"""
    customer_id: str
    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., ge=0)
    employment_length: float = Field(..., ge=0)
    debt_to_income: float = Field(..., ge=0)
    credit_history_length: float = Field(..., ge=0)
    number_of_debts: int = Field(..., ge=0)
    number_of_delinquent_debts: int = Field(..., ge=0)
    homeowner: int = Field(..., ge=0, le=1)
    
    class Config:
        schema_extra = {
            "example": APPLICATION_EXAMPLE
        }

class BehaviorData(BaseModel):
    """Dữ liệu input cho Behavior Scorecard"""
    customer_id: str
    current_balance: float = Field(..., ge=0)
    average_monthly_payment: float = Field(..., ge=0)
    payment_ratio: float = Field(..., ge=0, le=1)
    number_of_late_payments: int = Field(..., ge=0)
    months_since_last_late_payment: int = Field(..., ge=0)
    number_of_credit_inquiries: int = Field(..., ge=0)
    current_limit: float = Field(..., ge=0)
    average_utilization: float = Field(..., ge=0, le=1)
    
    class Config:
        schema_extra = {
            "example": BEHAVIOR_EXAMPLE
        }

class CollectionsData(BaseModel):
    """Dữ liệu input cho Collections Scoring"""
    customer_id: str
    days_past_due: int = Field(..., ge=0)
    outstanding_amount: float = Field(..., ge=0)
    number_of_contacts: int = Field(..., ge=0)
    previous_late_payments: int = Field(..., ge=0)
    promised_payment_amount: float = Field(..., ge=0)
    broken_promises: int = Field(..., ge=0)
    # Thêm các trường bị thiếu
    months_on_book: int = Field(..., ge=0, description="Số tháng khách hàng đã sử dụng sản phẩm")
    last_payment_amount: float = Field(..., ge=0, description="Số tiền thanh toán gần nhất")
    
    class Config:
        schema_extra = {
            "example": COLLECTIONS_EXAMPLE[0]
        }

class DesertionData(BaseModel):
    """Dữ liệu input cho Desertion Scoring"""
    customer_id: str
    months_to_maturity: int = Field(..., ge=0)
    total_relationship_value: float = Field(..., ge=0)
    number_of_products: int = Field(..., ge=0)
    satisfaction_score: float = Field(..., ge=0, le=10)
    number_of_complaints: int = Field(..., ge=0)
    months_since_last_interaction: float = Field(..., ge=0)
    # Thêm các trường bị thiếu
    age: int = Field(..., ge=18, le=100, description="Tuổi của khách hàng")
    tenure_months: int = Field(..., ge=0, description="Số tháng khách hàng đã gắn bó với ngân hàng")
    monthly_average_balance: float = Field(..., ge=0, description="Số dư trung bình hàng tháng")
    
    class Config:
        schema_extra = {
            "example": DESERTION_EXAMPLE[0]
        }

class CustomerIDList(BaseModel):
    customer_ids: List[str] = Field(..., description="Danh sách ID khách hàng cần dự đoán")
    
    class Config:
        schema_extra = {
            "example": {
                "customer_ids": ["CUS000123", "CUS000124", "CUS000125"]
            }
        }

# Thay thế CustomerIDList bằng các model batch mới
class BatchApplicationRequest(BaseModel):
    customers: List[ApplicationData] = Field(..., description="Danh sách khách hàng cần dự đoán")
    
    class Config:
        schema_extra = {
            "example": {
                "customers": [
                    APPLICATION_EXAMPLE,
                    {
                        "customer_id": "CUS000124",
                        "age": 42,
                        "income": 60000,
                        "employment_length": 8.0,
                        "debt_to_income": 0.15,
                        "credit_history_length": 12,
                        "number_of_debts": 1,
                        "number_of_delinquent_debts": 0,
                        "homeowner": 1
                    }
                ]
            }
        }

class BatchBehaviorRequest(BaseModel):
    customers: List[BehaviorData] = Field(..., description="Danh sách khách hàng cần dự đoán")
    
    class Config:
        schema_extra = {
            "example": {
                "customers": [
                    BEHAVIOR_EXAMPLE,
                    {
                        "customer_id": "CUS000457",
                        "current_balance": 4500,
                        "average_monthly_payment": 950,
                        "payment_ratio": 0.7,
                        "number_of_late_payments": 0,
                        "months_since_last_late_payment": 12,
                        "number_of_credit_inquiries": 1,
                        "current_limit": 12000,
                        "average_utilization": 0.38
                    }
                ]
            }
        }

class BatchCollectionsRequest(BaseModel):
    customers: List[CollectionsData] = Field(..., description="Danh sách khách hàng cần dự đoán")
    
    class Config:
        schema_extra = {
            "example": {
                "customers": [
                    COLLECTIONS_EXAMPLE[0],
                    {
                        "customer_id": "CUS000791",
                        "days_past_due": 75,
                        "outstanding_amount": 3200,
                        "number_of_contacts": 4,
                        "previous_late_payments": 3,
                        "promised_payment_amount": 800,
                        "broken_promises": 2,
                        "months_on_book": 30,
                        "last_payment_amount": 350
                    }
                ]
            }
        }

class BatchDesertionRequest(BaseModel):
    customers: List[DesertionData] = Field(..., description="Danh sách khách hàng cần dự đoán")
    
    class Config:
        schema_extra = {
            "example": {
                "customers": [
                    DESERTION_EXAMPLE[0],
                    {
                        "customer_id": "CUS000323",
                        "months_to_maturity": 2,
                        "total_relationship_value": 95000,
                        "number_of_products": 2,
                        "satisfaction_score": 7.5,
                        "number_of_complaints": 0,
                        "months_since_last_interaction": 1,
                        "age": 38,
                        "tenure_months": 48,
                        "monthly_average_balance": 9500
                    }
                ]
            }
        }

@app.get("/")
def read_root():
    return {"message": "Welcome to Credit Scoring API", "version": "1.0.0"}

@app.post("/application-score/", 
          description="Tính điểm tín dụng cho khách hàng mới dựa trên thông tin đơn vay",
          response_description="Hồ sơ rủi ro và điểm tín dụng của khách hàng")
def get_application_score(data: ApplicationData):
    """
    Tính điểm tín dụng cho khách hàng mới
    
    **Ví dụ Request:**
    ```json
    {
        "customer_id": "CUS000123",
        "age": 35,
        "income": 50000,
        "employment_length": 5.5,
        "debt_to_income": 0.25,
        "credit_history_length": 7,
        "number_of_debts": 2,
        "number_of_delinquent_debts": 0,
        "homeowner": 1
    }
    ```
    """
    try:
        # Chuyển đổi dữ liệu thành DataFrame
        customer_df = pd.DataFrame([data.dict()])
        
        # Lưu customer_id để trả về sau
        customer_id = data.customer_id
        
        # Loại bỏ cột customer_id trước khi truyền vào mô hình
        if 'customer_id' in customer_df.columns:
            customer_df_for_model = customer_df.drop(columns=['customer_id'])
        else:
            customer_df_for_model = customer_df
            
        # Đảm bảo tất cả các cột đều có kiểu dữ liệu phù hợp 
        for col in customer_df_for_model.columns:
            if customer_df_for_model[col].dtype == 'object':
                try:
                    customer_df_for_model[col] = pd.to_numeric(customer_df_for_model[col])
                except:
                    # Nếu không thể chuyển sang numeric, chuyển sang category
                    customer_df_for_model[col] = customer_df_for_model[col].astype('category')
        
        # Kiểm tra và thực hiện dự đoán trực tiếp nếu không có phương thức risk profile
        if hasattr(application_model, 'get_application_risk_profile'):
            # Tính điểm và tạo hồ sơ rủi ro
            risk_profile = application_model.get_application_risk_profile(customer_df_for_model)
            # Chuyển đổi các giá trị numpy về Python types
            risk_profile = {k: float(v) if isinstance(v, (np.floating, np.integer)) else v 
                          for k, v in risk_profile.items()}
        else:
            # Dự đoán xác suất mặc định
            default_prob = float(application_model.predict(customer_df_for_model)[0])
            risk_profile = {
                'default_probability': float(default_prob),
                'risk_level': 'High' if default_prob > 0.5 else ('Medium' if default_prob > 0.3 else 'Low'),
                'suggested_action': 'Reject' if default_prob > 0.5 else ('Review' if default_prob > 0.3 else 'Approve')
            }
        
        # Tính điểm scorecard nếu có
        try:
            # Kiểm tra xem mô hình đã được tải chưa
            if application_model.model is None:
                application_model.load_model()
                
            # Thử tính điểm trực tiếp từ mô hình
            y_pred_proba = application_model.predict(customer_df_for_model)
            # Chuyển đổi xác suất thành điểm (600-850) - đảm bảo dùng Python float
            proba_value = float(y_pred_proba[0])
            score = int(600 + 250 * (1 - proba_value))
            risk_profile['credit_score'] = score
        except Exception as e:
            risk_profile['credit_score'] = 600  # Điểm mặc định
            print(f"Error calculating scorecard: {e}")
        
        return {
            "customer_id": customer_id,
            "risk_profile": risk_profile
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Detailed error in application-score: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/behavior-score/",
          description="Tính điểm hành vi và đề xuất giới hạn tín dụng cho khách hàng hiện tại",
          response_description="Đề xuất giới hạn tín dụng và điểm tín dụng của khách hàng")
def get_behavior_score(data: BehaviorData):
    """
    Tính điểm hành vi cho khách hàng hiện tại
    
    **Ví dụ Request:**
    ```json
    {
        "customer_id": "CUS000456",
        "current_balance": 3500,
        "average_monthly_payment": 850,
        "payment_ratio": 0.65,
        "number_of_late_payments": 1,
        "months_since_last_late_payment": 8,
        "number_of_credit_inquiries": 2,
        "current_limit": 10000,
        "average_utilization": 0.35
    }
    ```
    """
    try:
        # Chuyển đổi dữ liệu thành DataFrame
        customer_df = pd.DataFrame([data.dict()])
        
        # Lưu customer_id và current_limit để sử dụng sau
        customer_id = data.customer_id
        current_limit = data.current_limit
        
        # Loại bỏ cột customer_id trước khi truyền vào mô hình
        if 'customer_id' in customer_df.columns:
            customer_df_for_model = customer_df.drop(columns=['customer_id'])
        else:
            customer_df_for_model = customer_df
        
        # Đảm bảo tất cả các cột đều có kiểu dữ liệu phù hợp
        for col in customer_df_for_model.columns:
            if customer_df_for_model[col].dtype == 'object':
                try:
                    customer_df_for_model[col] = pd.to_numeric(customer_df_for_model[col])
                except:
                    # Nếu không thể chuyển sang numeric, chuyển sang category
                    customer_df_for_model[col] = customer_df_for_model[col].astype('category')
        
        # Kiểm tra và thực hiện dự đoán trực tiếp nếu không có phương thức recommend_credit_limit
        if hasattr(behavior_model, 'recommend_credit_limit'):
            # Tính toán đề xuất giới hạn tín dụng
            recommendation = behavior_model.recommend_credit_limit(customer_df_for_model, current_limit)
            # Chuyển đổi các giá trị numpy về Python types
            recommendation = {k: float(v) if isinstance(v, (np.floating, np.integer)) else v 
                            for k, v in recommendation.items()}
        else:
            # Dự đoán xác suất mặc định
            default_prob = float(behavior_model.predict(customer_df_for_model)[0])
            
            # Tạo đề xuất đơn giản dựa trên xác suất mặc định
            if (default_prob < 0.2):
                new_limit = float(current_limit * 1.2)  # Tăng hạn mức 20%
                action = "Increase"
            elif (default_prob > 0.5):
                new_limit = float(current_limit * 0.7)  # Giảm hạn mức 30%
                action = "Decrease"
            else:
                new_limit = float(current_limit)  # Giữ nguyên
                action = "Maintain"
                
            recommendation = {
                'default_probability': float(default_prob),
                'suggested_limit': new_limit,
                'suggested_action': action,
                'risk_level': 'High' if default_prob > 0.5 else ('Medium' if default_prob > 0.3 else 'Low')
            }
        
        # Tính điểm scorecard nếu có
        try:
            # Kiểm tra xem mô hình đã được tải chưa
            if behavior_model.model is None:
                behavior_model.load_model()
                
            # Thử tính điểm trực tiếp từ mô hình
            y_pred_proba = behavior_model.predict(customer_df_for_model)
            # Chuyển đổi xác suất thành điểm (600-850) - đảm bảo dùng Python float
            proba_value = float(y_pred_proba[0])
            score = int(600 + 250 * (1 - proba_value))
            recommendation['credit_score'] = score
        except Exception as e:
            recommendation['credit_score'] = 600  # Điểm mặc định
            print(f"Error calculating scorecard: {e}")
        
        return {
            "customer_id": customer_id,
            "credit_recommendation": recommendation
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Detailed error in behavior-score: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/collections-prioritize/",
          description="Ưu tiên các tài khoản thu hồi nợ dựa trên khả năng tiếp tục trễ hạn",
          response_description="Danh sách tài khoản đã sắp xếp theo mức độ ưu tiên thu hồi nợ")
def prioritize_collection(data_list: list[CollectionsData]):
    """
    Ưu tiên các tài khoản thu hồi nợ
    
    **Ví dụ Request:**
    ```json
    [
        {
            "customer_id": "CUS000789",
            "days_past_due": 45,
            "outstanding_amount": 2500,
            "number_of_contacts": 3,
            "previous_late_payments": 2,
            "promised_payment_amount": 500,
            "broken_promises": 1
        },
        {
            "customer_id": "CUS000790",
            "days_past_due": 60,
            "outstanding_amount": 3600,
            "number_of_contacts": 5,
            "previous_late_payments": 3,
            "promised_payment_amount": 1000,
            "broken_promises": 2
        }
    ]
    ```
    """
    try:
        # Chuyển đổi dữ liệu thành DataFrame
        collection_df = pd.DataFrame([data.dict() for data in data_list])
        
        # Lưu mapping giữa customer_id và index để khôi phục sau
        id_mapping = collection_df['customer_id'].to_dict()
        
        # Loại bỏ cột customer_id trước khi truyền vào mô hình
        if 'customer_id' in collection_df.columns:
            collection_df_for_model = collection_df.drop(columns=['customer_id'])
        else:
            collection_df_for_model = collection_df
        
        # Đảm bảo tất cả các cột đều có kiểu dữ liệu phù hợp
        for col in collection_df_for_model.columns:
            if collection_df_for_model[col].dtype == 'object':
                try:
                    collection_df_for_model[col] = pd.to_numeric(collection_df_for_model[col])
                except:
                    # Nếu không thể chuyển sang numeric, chuyển sang category
                    collection_df_for_model[col] = collection_df_for_model[col].astype('category')
        
        # Ưu tiên thu hồi nợ
        prioritized = collections_model.prioritize_collections(collection_df_for_model)
        
        # Thêm lại cột customer_id
        prioritized['customer_id'] = prioritized.index.map(lambda i: id_mapping.get(i, f"Unknown-{i}"))
        
        # Chuyển kết quả thành JSON-serializable và đảm bảo các giá trị numpy được chuyển đổi
        result = []
        for idx, row in prioritized.iterrows():
            row_dict = {}
            for col, val in row.items():
                if isinstance(val, (np.floating, np.integer)):
                    row_dict[col] = float(val)
                else:
                    row_dict[col] = val
            result.append(row_dict)
        
        return {
            "prioritized_accounts": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/desertion-strategy/",
          description="Tạo chiến lược giữ chân khách hàng dựa trên khả năng từ bỏ",
          response_description="Chiến lược giữ chân khách hàng tùy chỉnh cho từng khách hàng")
def get_retention_strategy(data_list: list[DesertionData]):
    """
    Tạo chiến lược giữ chân khách hàng
    
    **Ví dụ Request:**
    ```json
    [
        {
            "customer_id": "CUS000321",
            "months_to_maturity": 3,
            "total_relationship_value": 75000,
            "number_of_products": 2,
            "satisfaction_score": 6.5,
            "number_of_complaints": 1,
            "months_since_last_interaction": 2
        },
        {
            "customer_id": "CUS000322",
            "months_to_maturity": 1,
            "total_relationship_value": 125000,
            "number_of_products": 3,
            "satisfaction_score": 8.0,
            "number_of_complaints": 0,
            "months_since_last_interaction": 0.5
        }
    ]
    ```
    """
    try:
        # Chuyển đổi dữ liệu thành DataFrame
        customer_df = pd.DataFrame([data.dict() for data in data_list])
        
        # Lưu customer_id trước khi loại bỏ
        customer_ids = customer_df['customer_id'].tolist() if 'customer_id' in customer_df.columns else []
        
        # Loại bỏ cột customer_id trước khi truyền vào mô hình
        if 'customer_id' in customer_df.columns:
            customer_df_for_model = customer_df.drop(columns=['customer_id'])
        else:
            customer_df_for_model = customer_df
            
        # Đảm bảo tất cả các cột đều có kiểu dữ liệu phù hợp
        for col in customer_df_for_model.columns:
            if customer_df_for_model[col].dtype == 'object':
                try:
                    customer_df_for_model[col] = pd.to_numeric(customer_df_for_model[col])
                except:
                    # Nếu không thể chuyển sang numeric, chuyển sang category
                    customer_df_for_model[col] = customer_df_for_model[col].astype('category')
        
        # Tạo chiến lược giữ chân
        strategy_df = desertion_model.create_retention_strategy(customer_df_for_model)
        
        # Thêm customer_id vào kết quả
        if customer_ids and len(customer_ids) == len(strategy_df):
            strategy_df['customer_id'] = customer_ids
        
        # Chuyển kết quả thành JSON-serializable và đảm bảo các giá trị numpy được chuyển đổi
        result = []
        for idx, row in strategy_df.iterrows():
            row_dict = {}
            for col, val in row.items():
                if isinstance(val, (np.floating, np.integer)):
                    row_dict[col] = float(val)
                else:
                    row_dict[col] = val
            result.append(row_dict)
        
        return {
            "retention_strategies": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Thay thế các endpoint batch cũ bằng phiên bản mới
@app.post("/batch/application-score/", 
          description="Đánh giá rủi ro cho nhiều khách hàng mới",
          response_description="Hồ sơ rủi ro và điểm tín dụng của các khách hàng")
def batch_application_score(data: BatchApplicationRequest):
    """
    Đánh giá rủi ro hàng loạt cho các khách hàng mới
    
    **Ví dụ Request:**
    ```json
    {
        "customers": [
            {
                "customer_id": "CUS000123",
                "age": 35,
                "income": 50000,
                "employment_length": 5.5,
                "debt_to_income": 0.25,
                "credit_history_length": 7,
                "number_of_debts": 2,
                "number_of_delinquent_debts": 0,
                "homeowner": 1
            },
            {
                "customer_id": "CUS000124",
                "age": 42,
                "income": 60000,
                "employment_length": 8.0,
                "debt_to_income": 0.15,
                "credit_history_length": 12,
                "number_of_debts": 1,
                "number_of_delinquent_debts": 0,
                "homeowner": 1
            }
        ]
    }
    ```
    """
    try:
        results = []
        
        for customer_data in data.customers:
            # Xử lý từng khách hàng giống như endpoint đơn lẻ
            result = get_application_score(customer_data)
            results.append(result)
        
        return {"results": results}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Detailed error in batch_application_score: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/batch/behavior-score/", 
          description="Đánh giá hành vi cho nhiều khách hàng hiện tại",
          response_description="Đề xuất giới hạn tín dụng và điểm tín dụng của các khách hàng")
def batch_behavior_score(data: BatchBehaviorRequest):
    """
    Đánh giá hành vi hàng loạt cho các khách hàng hiện tại
    
    **Ví dụ Request:**
    ```json
    {
        "customers": [
            {
                "customer_id": "CUS000456",
                "current_balance": 3500,
                "average_monthly_payment": 850,
                "payment_ratio": 0.65,
                "number_of_late_payments": 1,
                "months_since_last_late_payment": 8,
                "number_of_credit_inquiries": 2,
                "current_limit": 10000,
                "average_utilization": 0.35
            },
            {
                "customer_id": "CUS000457",
                "current_balance": 4500,
                "average_monthly_payment": 950,
                "payment_ratio": 0.7,
                "number_of_late_payments": 0,
                "months_since_last_late_payment": 12,
                "number_of_credit_inquiries": 1,
                "current_limit": 12000,
                "average_utilization": 0.38
            }
        ]
    }
    ```
    """
    try:
        results = []
        
        for customer_data in data.customers:
            # Xử lý từng khách hàng giống như endpoint đơn lẻ
            result = get_behavior_score(customer_data)
            results.append(result)
        
        return {"results": results}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Detailed error in batch_behavior_score: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/batch/collections-prioritize/", 
          description="Đánh giá và ưu tiên các tài khoản thu hồi nợ",
          response_description="Danh sách tài khoản đã xếp hạng theo mức độ ưu tiên thu hồi nợ")
def batch_collections_prioritize(data: BatchCollectionsRequest):
    """
    Ưu tiên các tài khoản thu hồi nợ
    
    **Ví dụ Request:**
    ```json
    {
        "customers": [
            {
                "customer_id": "CUS000789",
                "days_past_due": 45,
                "outstanding_amount": 2500,
                "number_of_contacts": 3,
                "previous_late_payments": 2,
                "promised_payment_amount": 500,
                "broken_promises": 1,
                "months_on_book": 24,
                "last_payment_amount": 300
            },
            {
                "customer_id": "CUS000790",
                "days_past_due": 60,
                "outstanding_amount": 3600,
                "number_of_contacts": 5,
                "previous_late_payments": 3,
                "promised_payment_amount": 1000,
                "broken_promises": 2,
                "months_on_book": 18,
                "last_payment_amount": 450
            }
        ]
    }
    ```
    """
    try:
        # Trực tiếp sử dụng phương thức prioritize_collection hiện có
        # vì nó đã được thiết kế để xử lý nhiều khách hàng
        return prioritize_collection(data.customers)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Detailed error in batch_collections_prioritize: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/batch/desertion-strategy/", 
          description="Tạo chiến lược giữ chân cho nhiều khách hàng",
          response_description="Chiến lược giữ chân khách hàng tùy chỉnh cho từng khách hàng")
def batch_desertion_strategy(data: BatchDesertionRequest):
    """
    Tạo chiến lược giữ chân hàng loạt cho các khách hàng
    
    **Ví dụ Request:**
    ```json
    {
        "customers": [
            {
                "customer_id": "CUS000321",
                "months_to_maturity": 3,
                "total_relationship_value": 75000,
                "number_of_products": 2,
                "satisfaction_score": 6.5,
                "number_of_complaints": 1,
                "months_since_last_interaction": 2,
                "age": 42,
                "tenure_months": 36,
                "monthly_average_balance": 8500
            },
            {
                "customer_id": "CUS000322",
                "months_to_maturity": 1,
                "total_relationship_value": 125000,
                "number_of_products": 3,
                "satisfaction_score": 8.0,
                "number_of_complaints": 0,
                "months_since_last_interaction": 0.5,
                "age": 35,
                "tenure_months": 60,
                "monthly_average_balance": 12000
            }
        ]
    }
    ```
    """
    try:
        # Trực tiếp sử dụng phương thức get_retention_strategy hiện có
        # vì nó đã được thiết kế để xử lý nhiều khách hàng
        return get_retention_strategy(data.customers)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Detailed error in batch_desertion_strategy: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Hàm hỗ trợ để lấy dữ liệu khách hàng từ ID
def get_customer_data_by_ids(customer_ids, data_type):
    """
    Lấy dữ liệu khách hàng từ danh sách ID
    
    Parameters:
    -----------
    customer_ids : list
        Danh sách ID khách hàng
    data_type : str
        Loại dữ liệu ('application', 'behavior', 'collections', 'desertion')
        
    Returns:
    --------
    DataFrame
        Dữ liệu của các khách hàng
    """
    # Xác định đường dẫn file dữ liệu dựa trên loại
    base_path = Path(__file__).parents[1] / 'data'
    
    if data_type == "application":
        file_path = base_path / 'processed' / 'processed_application_data.csv'
    elif data_type == "behavior":
        file_path = base_path / 'processed' / 'processed_behavior_data.csv'
    elif data_type == "collections":
        file_path = base_path / 'processed' / 'processed_collections_data.csv'
    elif data_type == "desertion":
        file_path = base_path / 'processed' / 'processed_desertion_data.csv'
    else:
        raise ValueError(f"Không hỗ trợ loại dữ liệu: {data_type}")
    
    try:
        # Đọc dữ liệu
        df = pd.read_csv(file_path)
        
        # Lọc theo ID khách hàng
        filtered_df = df[df['customer_id'].isin(customer_ids)]
        
        return filtered_df
    except Exception as e:
        print(f"Error loading data: {e}")
        # Trả về DataFrame rỗng để xử lý ở hàm gọi
        return pd.DataFrame()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
