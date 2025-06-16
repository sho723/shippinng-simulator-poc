import pandas as pd
import numpy as np
from typing import Dict, List
import random

def generate_sample_data():
    """サンプルデータを生成"""
    
    # サンプル船舶データ
    ships_data = [
        {'ship_id': 'SHIP001', 'name': 'Ocean Star', 'capacity': 1000, 'speed': 18, 'fuel_consumption': 150, 'ship_type': 'Container'},
        {'ship_id': 'SHIP002', 'name': 'Sea Dragon', 'capacity': 1500, 'speed': 20, 'fuel_consumption': 180, 'ship_type': 'Container'},
        {'ship_id': 'SHIP003', 'name': 'Wave Rider', 'capacity': 800, 'speed': 16, 'fuel_consumption': 120, 'ship_type': 'Container'},
        {'ship_id': 'SHIP004', 'name': 'Port Master', 'capacity': 2000, 'speed': 22, 'fuel_consumption': 200, 'ship_type': 'Container'},
        {'ship_id': 'SHIP005', 'name': 'Cargo King', 'capacity': 1200, 'speed': 19, 'fuel_consumption': 160, 'ship_type': 'Container'},
    ]
    
    # サンプル港湾データ
    ports_data = [
        {'port_id': 'PORT001', 'name': '東京港', 'latitude': 35.6295, 'longitude': 139.7431, 'berth_count': 3},
        {'port_id': 'PORT002', 'name': '横浜港', 'latitude': 35.4437, 'longitude': 139.6380, 'berth_count': 4},
        {'port_id': 'PORT003', 'name': '大阪港', 'latitude': 34.6518, 'longitude': 135.4222, 'berth_count': 2},
        {'port_id': 'PORT004', 'name': '神戸港', 'latitude': 34.6901, 'longitude': 135.1956, 'berth_count': 3},
        {'port_id': 'PORT005', 'name': '名古屋港', 'latitude': 35.0839, 'longitude': 136.8849, 'berth_count': 2},
    ]
    
    return pd.DataFrame(ships_data), pd.DataFrame(ports_data)

def validate_data(df: pd.DataFrame, data_type: str) -> Dict:
    """データの妥当性を検証"""
    errors = []
    warnings = []
    
    if data_type == "ships":
        required_columns = ['ship_id', 'name', 'capacity', 'speed', 'fuel_consumption']
        
        # 必須列の確認
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"必須列が不足しています: {', '.join(missing_cols)}")
        
        # データ型の確認
        if 'capacity' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['capacity']):
                errors.append("容量は数値である必要があります")
            elif (df['capacity'] <= 0).any():
                warnings.append("容量に0以下の値があります")
        
        if 'speed' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['speed']):
                errors.append("速度は数値である必要があります")
            elif (df['speed'] <= 0).any():
                warnings.append("速度に0以下の値があります")
        
        # 重複チェック
        if 'ship_id' in df.columns and df['ship_id'].duplicated().any():
            errors.append("船舶IDに重複があります")
    
    elif data_type == "ports":
        required_columns = ['port_id', 'name', 'latitude', 'longitude']
        
        # 必須列の確認
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"必須列が不足しています: {', '.join(missing_cols)}")
        
        # 緯度経度の確認
        if 'latitude' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['latitude']):
                errors.append("緯度は数値である必要があります")
            elif not df['latitude'].between(-90, 90).all():
                errors.append("緯度は-90〜90の範囲である必要があります")
        
        if 'longitude' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['longitude']):
                errors.append("経度は数値である必要があります")
            elif not df['longitude'].between(-180, 180).all():
                errors.append("経度は-180〜180の範囲である必要があります")
        
        # 重複チェック
        if 'port_id' in df.columns and df['port_id'].duplicated().any():
            errors.append("港湾IDに重複があります")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def calculate_route_efficiency(distance: float, fuel_consumption: float, cargo_volume: float) -> float:
    """ルート効率を計算"""
    if fuel_consumption == 0:
        return 0
    return (cargo_volume * distance) / fuel_consumption

def format_simulation_results(results: Dict) -> Dict:
    """シミュレーション結果をフォーマット"""
    formatted = {}
    
    # サマリー情報
    if 'summary' in results:
        summary = results['summary']
        formatted['summary_text'] = f"""
        シミュレーション結果サマリー:
        - 期間: {summary.get('simulation_period', 0)}日間
        - 総貨物取扱量: {summary.get('total_cargo_handled', 0):,.0f} TEU
        - 総燃料消費量: {summary.get('total_fuel_consumed', 0):,.0f} L
        - 総移動距離: {summary.get('total_distance_traveled', 0):,.0f} km
        - 燃費効率: {summary.get('average_fuel_efficiency', 0):.2f} TEU/L
        """
    
    # ログデータの整理
    if 'simulation_log' in results and not results['simulation_log'].empty:
        log_df = results['simulation_log']
        formatted['daily_summary'] = log_df.groupby(log_df['timestamp'].dt.date).agg({
            'cargo_volume': 'sum',
            'ship_id': 'nunique'
        }).rename(columns={'ship_id': 'active_ships'})
    
    return formatted
