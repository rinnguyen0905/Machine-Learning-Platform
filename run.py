import argparse
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Credit Scoring và Scorecard System')
    parser.add_argument('--action', type=str, required=True,
                        choices=['preprocess', 'train', 'scorecard', 'all', 'api', 'generate_data', 'web', 'server'],
                        help='Hành động cần thực hiện')
    parser.add_argument('--model', type=str, default='all',
                        choices=['application', 'behavior', 'collections', 'desertion', 'all'],
                        help='Loại mô hình để huấn luyện hoặc tạo scorecard')
    
    args = parser.parse_args()
    
    # Tạo thư mục cần thiết
    needed_dirs = [
        'data', 'data/raw', 'data/processed', 'data/sample', 
        'models', 'results'
    ]
    for d in needed_dirs:
        os.makedirs(Path(__file__).parent / d, exist_ok=True)
    
    if args.action == 'generate_data':
        try:
            print("Tạo dữ liệu mẫu...")
            from src.data.sample_generator import main as generate_sample_data
            generate_sample_data()
        except Exception as e:
            print(f"Lỗi khi tạo dữ liệu mẫu: {e}")
    
    if args.action == 'preprocess' or args.action == 'all':
        try:
            print("Bắt đầu tiền xử lý dữ liệu...")
            from src.data.preprocessor import DataPreprocessor
            preprocessor = DataPreprocessor()
            if args.model == 'application' or args.model == 'all':
                preprocessor.prepare_application_data()
            if args.model == 'behavior' or args.model == 'all':
                preprocessor.prepare_behavior_data()
            if args.model == 'collections' or args.model == 'all':
                preprocessor.prepare_collections_data()
            if args.model == 'desertion' or args.model == 'all':
                preprocessor.prepare_desertion_data()
            print("Tiền xử lý dữ liệu hoàn tất!")
        except Exception as e:
            print(f"Lỗi khi tiền xử lý dữ liệu: {e}")
            print("Gợi ý: Hãy chạy 'python run.py --action generate_data' trước để tạo dữ liệu mẫu")
    
    if args.action == 'train' or args.action == 'all':
        print("Bắt đầu huấn luyện mô hình...")
        
        if args.model == 'application' or args.model == 'all':
            try:
                print("Huấn luyện Application Scorecard...")
                from src.models.application_scorecard import ApplicationScorecard
                app_model = ApplicationScorecard()
                app_metrics = app_model.process_and_train()
                print(f"Metrics: {app_metrics}")
            except Exception as e:
                print(f"Lỗi khi huấn luyện Application Scorecard: {e}")
            
        if args.model == 'behavior' or args.model == 'all':
            try:
                print("Huấn luyện Behavior Scorecard...")
                from src.models.behavior_scorecard import BehaviorScorecard
                behavior_model = BehaviorScorecard()
                behavior_metrics = behavior_model.process_and_train()
                print(f"Metrics: {behavior_metrics}")
            except Exception as e:
                print(f"Lỗi khi huấn luyện Behavior Scorecard: {e}")
            
        if args.model == 'collections' or args.model == 'all':
            try:
                print("Huấn luyện Collections Scoring...")
                from src.models.collections_scoring import CollectionsScoring
                collections_model = CollectionsScoring()
                collections_metrics = collections_model.process_and_train()
                print(f"Metrics: {collections_metrics}")
            except Exception as e:
                print(f"Lỗi khi huấn luyện Collections Scoring: {e}")
            
        if args.model == 'desertion' or args.model == 'all':
            try:
                print("Huấn luyện Desertion Scoring...")
                from src.models.desertion_scoring import DesertionScoring
                desertion_model = DesertionScoring()
                desertion_metrics = desertion_model.process_and_train()
                print(f"Metrics: {desertion_metrics}")
            except Exception as e:
                print(f"Lỗi khi huấn luyện Desertion Scoring: {e}")
            
        print("Huấn luyện mô hình hoàn tất!")
    
    if args.action == 'scorecard' or args.action == 'all':
        print("Bắt đầu tạo scorecard...")
        import xgboost as xgb
        from src.scorecard.scorecard_builder import ScorecardBuilder
        import pandas as pd
        
        if args.model == 'application' or args.model == 'all':
            try:
                print("Tạo Application Scorecard...")
                model_type = 'application_scorecard'
                model_path = Path(__file__).parent / f'models/{model_type}_xgb_model.json'
                
                # Đảm bảo thư mục results tồn tại
                results_dir = Path(__file__).parent / 'results'
                os.makedirs(results_dir, exist_ok=True)
                
                # Kiểm tra xem model đã tồn tại chưa
                if not os.path.exists(model_path):
                    print(f"Không tìm thấy model tại {model_path}. Vui lòng huấn luyện model trước.")
                else:
                    # Tải mô hình và dữ liệu mẫu
                    xgb_model = xgb.Booster()
                    xgb_model.load_model(str(model_path))
                    
                    # Tải dữ liệu mẫu cho phân tích
                    data_path = Path(__file__).parent / 'data/processed/processed_application_data.csv'
                    if os.path.exists(data_path):
                        sample_data = pd.read_csv(data_path)
                        if 'customer_id' in sample_data.columns:
                            sample_data = sample_data.drop(columns=['customer_id'])
                        if args.model_target in sample_data.columns:  # Loại bỏ biến mục tiêu
                            sample_data = sample_data.drop(columns=[args.model_target])
                        sample_data = sample_data.head(1000)  # Lấy mẫu nhỏ để phân tích
                    else:
                        sample_data = None
                        print(f"Không tìm thấy dữ liệu mẫu tại {data_path}")
                    
                    # Xây dựng scorecard
                    builder = ScorecardBuilder(model_type)
                    scorecard = builder.build_scorecard_from_model(xgb_model)
                    
                    # Tạo bảng và các biểu đồ
                    builder.create_scorecard_table(Path(__file__).parent / f'results/{model_type}_scorecard.xlsx')
                    builder.visualize_scorecard(Path(__file__).parent / f'results/{model_type}_scorecard_viz.png')
                    
                    # Tạo các biểu đồ phân tích thay thế cho SHAP
                    builder.visualize_feature_importance(xgb_model, sample_data, 
                                                      Path(__file__).parent / f'results/{model_type}_feature_importance.png')
                    builder.visualize_feature_effects(sample_data, 
                                                   Path(__file__).parent / f'results/{model_type}_feature_effects.png')
                    
                    # Lưu scorecard
                    builder.save_scorecard()
            except Exception as e:
                import traceback
                print(f"Lỗi khi tạo Application Scorecard: {e}")
                print(traceback.format_exc())
        
        if args.model == 'behavior' or args.model == 'all':
            try:
                print("Tạo Behavior Scorecard...")
                model_type = 'behavior_scorecard'
                model_path = Path(__file__).parent / f'models/{model_type}_xgb_model.json'
                
                # Kiểm tra xem model đã tồn tại chưa
                if not os.path.exists(model_path):
                    print(f"Không tìm thấy model tại {model_path}. Vui lòng huấn luyện model trước.")
                else:
                    xgb_model = xgb.Booster()
                    xgb_model.load_model(str(model_path))
                    
                    builder = ScorecardBuilder(model_type)
                    scorecard = builder.build_scorecard_from_model(xgb_model)
                    builder.create_scorecard_table(Path(__file__).parent / f'results/{model_type}_scorecard.xlsx')
                    builder.visualize_scorecard(Path(__file__).parent / f'results/{model_type}_scorecard_viz.png')
                    builder.save_scorecard()
            except Exception as e:
                import traceback
                print(f"Lỗi khi tạo Behavior Scorecard: {e}")
                print(traceback.format_exc())
            
        print("Tạo scorecard hoàn tất!")
    
    if args.action == 'api':
        print("Khởi động API...")
        import subprocess
        subprocess.run(["python", "-m", "api.main"])

    if args.action == 'web':
        print("Khởi động Web UI...")
        try:
            import subprocess
            # Make sure Flask is installed
            try:
                import flask
            except ImportError:
                print("Installing Flask...")
                subprocess.run(["pip", "install", "flask"])
            # Start the web application
            subprocess.run(["python", "web/app.py"])
        except Exception as e:
            print(f"Error starting web UI: {e}")
    
    if args.action == 'server':
        print("Khởi động server (Web UI + API)...")
        try:
            import threading
            import subprocess
            import time
            
            # Make sure Flask is installed
            try:
                import flask
            except ImportError:
                print("Installing Flask...")
                subprocess.run(["pip", "install", "flask"])
            
            # Function to start the API
            def start_api():
                print("Khởi động API backend...")
                subprocess.run(["python", "-m", "api.main"])
            
            # Function to start the Web UI
            def start_web():
                # Give API a moment to start
                time.sleep(2)
                print("Khởi động Web UI frontend...")
                subprocess.run(["python", "web/app.py"])
            
            # Start API in a separate thread
            api_thread = threading.Thread(target=start_api)
            api_thread.daemon = True
            api_thread.start()
            
            # Start Web UI in the main thread
            start_web()
            
        except Exception as e:
            print(f"Lỗi khi khởi động server: {e}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    main()
