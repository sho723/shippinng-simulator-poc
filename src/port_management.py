import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

class Berth:
    def __init__(self, berth_id: str, capacity: float, handling_rate: float):
        self.berth_id = berth_id
        self.capacity = capacity  # TEU
        self.handling_rate = handling_rate  # TEU/hour
        self.is_occupied = False
        self.current_ship = None
        self.queue = []
        
    def to_dict(self) -> Dict:
        return {
            'berth_id': self.berth_id,
            'capacity': self.capacity,
            'handling_rate': self.handling_rate,
            'is_occupied': self.is_occupied,
            'current_ship': self.current_ship
        }

class Port:
    def __init__(self, port_id: str, name: str, latitude: float, longitude: float):
        self.port_id = port_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.berths = {}
        self.waiting_queue = []
        self.statistics = {
            'total_ships_handled': 0,
            'total_cargo_handled': 0,
            'average_waiting_time': 0
        }
    
    def add_berth(self, berth: Berth):
        """バースを追加"""
        self.berths[berth.berth_id] = berth
    
    def get_available_berth(self) -> Optional[Berth]:
        """利用可能なバースを取得"""
        for berth in self.berths.values():
            if not berth.is_occupied:
                return berth
        return None
    
    def get_total_capacity(self) -> float:
        """総処理能力を取得"""
        return sum(berth.handling_rate for berth in self.berths.values())
    
    def to_dict(self) -> Dict:
        return {
            'port_id': self.port_id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'berth_count': len(self.berths),
            'total_capacity': self.get_total_capacity()
        }

class PortManager:
    def __init__(self):
        self.ports = {}
    
    def add_port(self, port: Port) -> bool:
        """港湾を追加"""
        if port.port_id in self.ports:
            return False
        self.ports[port.port_id] = port
        return True
    
    def remove_port(self, port_id: str) -> bool:
        """港湾を削除"""
        if port_id in self.ports:
            del self.ports[port_id]
            return True
        return False
    
    def get_port(self, port_id: str) -> Optional[Port]:
        """港湾を取得"""
        return self.ports.get(port_id)
    
    def get_all_ports(self) -> List[Port]:
        """全港湾を取得"""
        return list(self.ports.values())
    
    def calculate_distance(self, port1_id: str, port2_id: str) -> float:
        """港湾間の距離を計算（簡易計算）"""
        port1 = self.get_port(port1_id)
        port2 = self.get_port(port2_id)
        
        if not port1 or not port2:
            return 0
        
        # 簡易的な距離計算（実際はより正確な計算が必要）
        lat_diff = port1.latitude - port2.latitude
        lon_diff = port1.longitude - port2.longitude
        distance = np.sqrt(lat_diff**2 + lon_diff**2) * 111  # km
        return distance
    
    def to_dataframe(self) -> pd.DataFrame:
        """DataFrame形式で出力"""
        data = [port.to_dict() for port in self.ports.values()]
        return pd.DataFrame(data)
    
    def from_dataframe(self, df: pd.DataFrame):
        """DataFrameから港湾データを読み込み"""
        self.ports = {}
        for _, row in df.iterrows():
            port = Port(
                port_id=str(row['port_id']),
                name=str(row['name']),
                latitude=float(row['latitude']),
                longitude=float(row['longitude'])
            )
            # バース情報がある場合は追加
            if 'berth_count' in row and pd.notna(row['berth_count']):
                for i in range(int(row['berth_count'])):
                    berth = Berth(
                        berth_id=f"{port.port_id}_B{i+1}",
                        capacity=100,  # デフォルト値
                        handling_rate=20  # デフォルト値
                    )
                    port.add_berth(berth)
            
            self.ports[port.port_id] = port
