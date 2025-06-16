import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import random
from .ship_management import Ship, ShipManager
from .port_management import Port, PortManager, Berth

class SimulationEvent:
    def __init__(self, timestamp: datetime, event_type: str, ship_id: str, 
                 port_id: str, details: Dict):
        self.timestamp = timestamp
        self.event_type = event_type  # DEPARTURE, ARRIVAL, LOADING_START, LOADING_END
        self.ship_id = ship_id
        self.port_id = port_id
        self.details = details

class ShippingSimulator:
    def __init__(self, ship_manager: ShipManager, port_manager: PortManager):
        self.ship_manager = ship_manager
        self.port_manager = port_manager
        self.current_time = datetime.now()
        self.events = []
        self.simulation_results = []
        
    def setup_simulation(self, start_time: datetime, end_time: datetime):
        """シミュレーションの初期設定"""
        self.start_time = start_time
        self.end_time = end_time
        self.current_time = start_time
        self.events = []
        self.simulation_results = []
    
    def generate_cargo_demand(self, ports: List[str], days: int) -> pd.DataFrame:
        """貨物需要を生成"""
        demand_data = []
        for day in range(days):
            for origin_port in ports:
                for dest_port in ports:
                    if origin_port != dest_port:
                        # ランダムな需要生成（実際は過去データやトレンドを使用）
                        demand = np.random.poisson(50)  # 平均50TEU
                        demand_data.append({
                            'date': self.start_time + timedelta(days=day),
                            'origin_port': origin_port,
                            'destination_port': dest_port,
                            'cargo_volume': demand,
                            'priority': random.choice(['Low', 'Medium', 'High'])
                        })
        return pd.DataFrame(demand_data)
    
    def schedule_ship_routes(self, cargo_demand: pd.DataFrame):
        """船舶ルートをスケジューリング"""
        available_ships = self.ship_manager.get_ships_by_status("Available")
        
        for _, demand in cargo_demand.iterrows():
            if not available_ships:
                break
                
            # 最適な船舶を選択（簡易アルゴリズム）
            best_ship = self.select_best_ship(available_ships, demand)
            if best_ship:
                self.assign_route(best_ship, demand)
                available_ships.remove(best_ship)
    
    def select_best_ship(self, ships: List[Ship], demand) -> Optional[Ship]:
        """最適な船舶を選択"""
        # 容量と効率を考慮した簡易選択
        suitable_ships = [ship for ship in ships if ship.capacity >= demand['cargo_volume']]
        if not suitable_ships:
            return None
        
        # 燃費効率が良い船舶を選択
        return min(suitable_ships, key=lambda s: s.fuel_consumption)
    
    def assign_route(self, ship: Ship, demand):
        """船舶にルートを割り当て"""
        origin_port = self.port_manager.get_port(demand['origin_port'])
        dest_port = self.port_manager.get_port(demand['destination_port'])
        
        if not origin_port or not dest_port:
            return
        
        # 距離と移動時間を計算
        distance = self.port_manager.calculate_distance(
            demand['origin_port'], demand['destination_port']
        )
        travel_time = distance / ship.speed  # 時間
        
        # イベントを生成
        departure_time = demand['date']
        arrival_time = departure_time + timedelta(hours=travel_time)
        
        # 出発イベント
        departure_event = SimulationEvent(
            timestamp=departure_time,
            event_type="DEPARTURE",
            ship_id=ship.ship_id,
            port_id=demand['origin_port'],
            details={'cargo_volume': demand['cargo_volume'], 'destination': demand['destination_port']}
        )
        
        # 到着イベント
        arrival_event = SimulationEvent(
            timestamp=arrival_time,
            event_type="ARRIVAL",
            ship_id=ship.ship_id,
            port_id=demand['destination_port'],
            details={'cargo_volume': demand['cargo_volume'], 'travel_distance': distance}
        )
        
        self.events.extend([departure_event, arrival_event])
        ship.status = "Scheduled"
    
    def run_simulation(self) -> Dict:
        """シミュレーションを実行"""
        # イベントを時系列順にソート
        self.events.sort(key=lambda x: x.timestamp)
        
        simulation_log = []
        port_statistics = {port_id: {'ships_handled': 0, 'cargo_handled': 0, 'waiting_times': []} 
                          for port_id in self.port_manager.ports.keys()}
        ship_statistics = {ship.ship_id: {'total_distance': 0, 'fuel_consumed': 0, 'cargo_delivered': 0}
                          for ship in self.ship_manager.get_all_ships()}
        
        for event in self.events:
            if event.timestamp > self.end_time:
                break
                
            self.current_time = event.timestamp
            
            # イベント処理
            if event.event_type == "DEPARTURE":
                self.handle_departure(event, simulation_log, ship_statistics)
            elif event.event_type == "ARRIVAL":
                self.handle_arrival(event, simulation_log, port_statistics, ship_statistics)
        
        # 結果をまとめる
        results = {
            'simulation_log': pd.DataFrame(simulation_log),
            'port_statistics': port_statistics,
            'ship_statistics': ship_statistics,
            'summary': self.generate_summary(port_statistics, ship_statistics)
        }
        
        return results
    
    def handle_departure(self, event: SimulationEvent, log: List, ship_stats: Dict):
        """出発イベントを処理"""
        ship = self.ship_manager.get_ship(event.ship_id)
        if ship:
            ship.status = "In Transit"
            ship.cargo = event.details['cargo_volume']
            
            log.append({
                'timestamp': event.timestamp,
                'event': 'DEPARTURE',
                'ship_id': event.ship_id,
                'port_id': event.port_id,
                'cargo_volume': event.details['cargo_volume']
            })
    
    def handle_arrival(self, event: SimulationEvent, log: List, port_stats: Dict, ship_stats: Dict):
        """到着イベントを処理"""
        ship = self.ship_manager.get_ship(event.ship_id)
        port = self.port_manager.get_port(event.port_id)
        
        if ship and port:
            # 統計情報を更新
            port_stats[event.port_id]['ships_handled'] += 1
            port_stats[event.port_id]['cargo_handled'] += event.details['cargo_volume']
            
            ship_stats[event.ship_id]['total_distance'] += event.details['travel_distance']
            ship_stats[event.ship_id]['cargo_delivered'] += event.details['cargo_volume']
            
            # 燃料消費量を計算
            fuel_consumed = (event.details['travel_distance'] / ship.speed) * ship.fuel_consumption
            ship_stats[event.ship_id]['fuel_consumed'] += fuel_consumed
            
            ship.status = "Available"
            ship.cargo = 0
            
            log.append({
                'timestamp': event.timestamp,
                'event': 'ARRIVAL',
                'ship_id': event.ship_id,
                'port_id': event.port_id,
                'cargo_volume': event.details['cargo_volume'],
                'fuel_consumed': fuel_consumed
            })
    
    def generate_summary(self, port_stats: Dict, ship_stats: Dict) -> Dict:
        """サマリーを生成"""
        total_cargo = sum(stats['cargo_handled'] for stats in port_stats.values())
        total_fuel = sum(stats['fuel_consumed'] for stats in ship_stats.values())
        total_distance = sum(stats['total_distance'] for stats in ship_stats.values())
        
        return {
            'total_cargo_handled': total_cargo,
            'total_fuel_consumed': total_fuel,
            'total_distance_traveled': total_distance,
            'average_fuel_efficiency': total_cargo / total_fuel if total_fuel > 0 else 0,
            'simulation_period': (self.end_time - self.start_time).days
        }
