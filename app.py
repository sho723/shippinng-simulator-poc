import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from src.simulator_engine import ShippingSimulator, Ship, Port, Berth

# ページ設定
st.set_page_config(
    page_title="配船シミュレーター POC",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0066CC;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .simulator-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #0066CC;
        margin: 1rem 0;
    }
    .success-banner {
        background: linear-gradient(90deg, #00C851, #007E33);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """セッション状態の初期化"""
    if 'simulator' not in st.session_state:
        st.session_state.simulator = ShippingSimulator()
        
    if 'ships' not in st.session_state:
        st.session_state.ships = []
        
    if 'ports' not in st.session_state:
        st.session_state.ports = []
        
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = {}
        
    if 'simulation_history' not in st.session_state:
        st.session_state.simulation_history = []

def load_sample_data():
    """サンプルデータの読み込み"""
    try:
        # サンプル船舶データ
        sample_ships = [
            Ship("SIM001", "Pacific Explorer", 280, 38, 12, "container", 
                 (35.1, 139.8), datetime.now() + timedelta(hours=6), 5),
            Ship("SIM002", "Ocean Guardian", 220, 32, 10, "bulk", 
                 (34.7, 135.3), datetime.now() + timedelta(hours=10), 4),
            Ship("SIM003", "Sea Pioneer", 320, 42, 14, "container", 
                 (34.9, 135.1), datetime.now() + timedelta(hours=4), 5),
            Ship("SIM004", "Blue Horizon", 180, 28, 8, "general", 
                 (35.2, 140.1), datetime.now() + timedelta(hours=15), 3),
            Ship("SIM005", "Maritime Star", 250, 35, 11, "tanker", 
                 (34.6, 135.4), datetime.now() + timedelta(hours=8), 4)
        ]
        
        # サンプル港湾データ
        berths_tokyo = [
            Berth("TKY_CT1", "TKY", "コンテナターミナル1", 320, 45, 16, 
                  ["container"], ["gantry_crane", "reefer", "lighting"], 12000),
            Berth("TKY_CT2", "TKY", "コンテナターミナル2", 300, 40, 15, 
                  ["container"], ["gantry_crane", "reefer"], 10000),
            Berth("TKY_GP1", "TKY", "汎用バース1", 250, 35, 12, 
                  ["general", "bulk"], ["mobile_crane", "conveyor"], 6000)
        ]
        
        berths_osaka = [
            Berth("OSA_CT1", "OSA", "大阪コンテナターミナル", 280, 38, 14, 
                  ["container"], ["gantry_crane", "reefer"], 9000),
            Berth("OSA_BK1", "OSA", "バルクターミナル", 200, 30, 10, 
                  ["bulk"], ["conveyor", "hopper"], 5000)
        ]
        
        port_tokyo = Port("TKY", "東京港", (35.6162, 139.7422), berths_tokyo, {}, {})
        port_osaka = Port("OSA", "大阪港", (34.6518, 135.5063), berths_osaka, {}, {})
        
        return sample_ships, [port_tokyo, port_osaka]
    except Exception as e:
        st.error(f"サンプルデータの読み込みエラー: {e}")
        return [], []

def main():
    """メインアプリケーション"""
    initialize_session_state()
    
    # ヘッダー
    st.markdown('<h1 class="main-header">⚓ 配船シミュレーター POC</h1>', 
                unsafe_allow_html=True)
    
    # サイドバー
    with st.sidebar:
        st.header("🎛️ シミュレーター制御")
        
        # サンプルデータ読み込みボタン
        if st.button("📋 サンプルデータ読み込み", type="primary", use_container_width=True):
            ships, ports = load_sample_data()
            st.session_state.ships = ships
            st.session_state.ports = ports
            
            # シミュレーターにデータを追加
            st.session_state.simulator = ShippingSimulator()
            for ship in ships:
                st.session_state.simulator.add_ship(ship)
            for port in ports:
                st.session_state.simulator.add_port(port)
                
            st.success("✅ サンプルデータを読み込みました!")
            st.rerun()
        
        # 統計情報
        st.markdown("### 📊 現在の状況")
        
        col1, col2 = st.columns(2)
        with col1:
            ship_count = len(st.session_state.ships)
            st.metric("🚢 船舶", ship_count, delta=None)
        with col2:
            port_count = len(st.session_state.ports)
            st.metric("🏭 港湾", port_count, delta=None)
        
        # 追加統計
        if st.session_state.ships:
            total_berths = sum(len(p.berths) for p in st.session_state.ports)
            st.metric("⚓ 総バース数", total_berths)
            
            avg_priority = np.mean([s.priority for s in st.session_state.ships])
            st.metric("📈 平均優先度", f"{avg_priority:.1f}")
        
        # シミュレーション履歴
        if st.session_state.simulation_history:
            st.markdown("### 📝 実行履歴")
            st.write(f"実行回数: {len(st.session_state.simulation_history)}")
            
            if st.button("🗑️ 履歴クリア"):
                st.session_state.simulation_history = []
                st.rerun()
    
    # メインコンテンツ
    if not st.session_state.ships or not st.session_state.ports:
        st.markdown("""
        <div class="simulator-card">
            <h3>🚀 シミュレーター開始手順</h3>
            <ol>
                <li>👈 サイドバーの「サンプルデータ読み込み」ボタンをクリック</li>
                <li>📊 データが読み込まれたら各タブでシミュレーションを実行</li>
                <li>📈 結果を分析して最適解を確認</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # タブ構成
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 クイックシミュレーション", 
        "📊 詳細ダッシュボード", 
        "⚙️ 設定管理", 
        "📈 分析レポート"
    ])
    
    with tab1:
        show_quick_simulation_tab()
    
    with tab2:
        show_detailed_dashboard_tab()
        
    with tab3:
        show_settings_management_tab()
        
    with tab4:
        show_analysis_report_tab()

def show_quick_simulation_tab():
    """クイックシミュレーションタブ"""
    st.header("🎯 クイックシミュレーション")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="simulator-card">', unsafe_allow_html=True)
        st.subheader("⚙️ シミュレーション設定")
        
        # 船舶選択
        ship_options = [f"{ship.name} ({ship.id})" for ship in st.session_state.ships]
        selected_ships = st.multiselect(
            "🚢 対象船舶を選択:",
            ship_options,
            default=ship_options[:3] if len(ship_options) >= 3 else ship_options
        )
        
        # シミュレーションパラメータ
        st.markdown("**最適化設定**")
        optimization_method = st.selectbox(
            "最適化手法:",
            ["cost_optimization", "time_optimization", "balanced"]
        )
        
        consider_weather = st.checkbox("気象条件を考慮", value=True)
        consider_congestion = st.checkbox("港湾混雑を考慮", value=True)
        
        # 実行ボタン
        if st.button("🚀 シミュレーション実行", type="primary", use_container_width=True):
            if selected_ships:
                with st.spinner("🔄 最適配船を計算中..."):
                    # 選択された船舶を取得
                    selected_ship_ids = [name.split("(")[1].rstrip(")") 
                                       for name in selected_ships]
                    ships_to_simulate = [s for s in st.session_state.ships 
                                       if s.id in selected_ship_ids]
                    
                    # シミュレーション実行
                    result = st.session_state.simulator.run_optimization(
                        ships_to_simulate,
                        method=optimization_method,
                        weather=consider_weather,
                        congestion=consider_congestion
                    )
                    
                    st.session_state.simulation_results = result
                    
                    # 履歴に追加
                    st.session_state.simulation_history.append({
                        'timestamp': datetime.now(),
                        'ships_count': len(ships_to_simulate),
                        'method': optimization_method,
                        'total_cost': result.get('total_cost', 0) if result else 0
                    })
                
                st.markdown('<div class="success-banner">✅ シミュレーション完了!</div>', 
                           unsafe_allow_html=True)
            else:
                st.warning("⚠️ 船舶を選択してください")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("📋 シミュレーション結果")
        
        if st.session_state.simulation_results:
            results = st.session_state.simulation_results
            
            # サマリーメトリクス
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.metric("配船完了", f"{results.get('successful_allocations', 0)}隻")
            with col_b:
                st.metric("総費用", f"¥{results.get('total_cost', 0):,.0f}")
            with col_c:
                st.metric("平均待機時間", f"{results.get('avg_waiting_time', 0):.1f}h")
            with col_d:
                efficiency = results.get('efficiency_score', 0) * 100
                st.metric("効率スコア", f"{efficiency:.1f}%")
            
            # 詳細結果
            if 'allocations' in results:
                st.markdown("**📊 配船詳細結果**")
                
                for ship_id, allocation in results['allocations'].items():
                    with st.expander(f"🚢 {ship_id} の配船結果", expanded=True):
                        col_x, col_y, col_z = st.columns(3)
                        
                        with col_x:
                            st.write(f"**配船先:** {allocation['port_name']}")
                            st.write(f"**バース:** {allocation['berth_name']}")
                        
                        with col_y:
                            st.write(f"**入港時刻:** {allocation['arrival_time']}")
                            st.write(f"**作業完了:** {allocation['completion_time']}")
                        
                        with col_z:
                            st.write(f"**総費用:** ¥{allocation['total_cost']:,.0f}")
                            st.write(f"**待機時間:** {allocation['waiting_time']:.1f}h")
                        
                        # 費用内訳の可視化
                        costs = allocation.get('cost_breakdown', {})
                        if costs:
                            fig_costs = px.pie(
                                values=list(costs.values()),
                                names=list(costs.keys()),
                                title=f"{ship_id} 費用内訳"
                            )
                            st.plotly_chart(fig_costs, use_container_width=True)
        else:
            st.info("📝 シミュレーションを実行すると結果がここに表示されます")

def show_detailed_dashboard_tab():
    """詳細ダッシュボードタブ"""
    st.header("📊 詳細ダッシュボード")
    
    # KPIメトリクス行
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("総登録船舶", len(st.session_state.ships), 
                 delta=len(st.session_state.ships)-3 if len(st.session_state.ships) > 3 else None)
    
    with col2:
        total_berths = sum(len(p.berths) for p in st.session_state.ports)
        st.metric("利用可能バース", total_berths)
    
    with col3:
        if st.session_state.simulation_results:
            success_rate = st.session_state.simulation_results.get('success_rate', 0) * 100
            st.metric("配船成功率", f"{success_rate:.1f}%")
    
    with col4:
        avg_priority = np.mean([s.priority for s in st.session_state.ships]) if st.session_state.ships else 0
        st.metric("平均優先度", f"{avg_priority:.1f}")
    
    with col5:
        simulation_count = len(st.session_state.simulation_history)
        st.metric("実行回数", simulation_count)
    
    # グラフエリア
    if st.session_state.ships:
        col1, col2 = st.columns(2)
        
        with col1:
            # 船舶の貨物種別分布
            cargo_types = [ship.cargo_type for ship in st.session_state.ships]
            cargo_counts = pd.Series(cargo_types).value_counts()
            
            fig_pie = px.pie(
                values=cargo_counts.values, 
                names=cargo_counts.index,
                title="🚢 貨物種別分布",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 船舶サイズと優先度の散布図
            ship_data = pd.DataFrame([
                {
                    'name': s.name, 
                    'length': s.length, 
                    'width': s.width, 
                    'priority': s.priority,
                    'cargo_type': s.cargo_type
                }
                for s in st.session_state.ships
            ])
            
            fig_scatter = px.scatter(
                ship_data, 
                x='length', 
                y='width', 
                size='priority',
                color='cargo_type',
                hover_name='name',
                title="📏 船舶サイズ分布",
                labels={'length': '船長(m)', 'width': '船幅(m)'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 時系列分析
        if st.session_state.simulation_history:
            st.markdown("### 📈 シミュレーション履歴分析")
            
            history_df = pd.DataFrame(st.session_state.simulation_history)
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                fig_timeline = px.line(
                    history_df, 
                    x='timestamp', 
                    y='total_cost',
                    title="💰 総費用推移",
                    markers=True
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            with col_b:
                fig_ships = px.bar(
                    history_df, 
                    x='timestamp', 
                    y='ships_count',
                    title="🚢 処理船舶数推移"
                )
                st.plotly_chart(fig_ships, use_container_width=True)

def show_settings_management_tab():
    """設定管理タブ"""
    st.header("⚙️ 設定管理")
    
    tab_ships, tab_ports, tab_config = st.tabs(["🚢 船舶管理", "🏭 港湾管理", "⚙️ システム設定"])
    
    with tab_ships:
        st.subheader("🚢 船舶データ管理")
        
        # 新規船舶登録
        with st.expander("➕ 新規船舶登録", expanded=False):
            with st.form("ship_registration_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    ship_id = st.text_input("船舶ID*")
                    ship_name = st.text_input("船名*")
                    cargo_type = st.selectbox("貨物種別", 
                                            ["container", "bulk", "general", "tanker", "roro"])
                
                with col2:
                    length = st.number_input("船長(m)", min_value=50.0, max_value=400.0, value=200.0)
                    width = st.number_input("船幅(m)", min_value=10.0, max_value=60.0, value=30.0)
                    draft = st.number_input("喫水(m)", min_value=5.0, max_value=20.0, value=10.0)
                
                with col3:
                    priority = st.slider("優先度", 1, 5, 3)
                    eta = st.datetime_input("到着予定時刻", datetime.now() + timedelta(hours=12))
                    lat = st.number_input("現在位置(緯度)", value=35.0)
                    lon = st.number_input("現在位置(経度)", value=140.0)
                
                if st.form_submit_button("🚢 船舶登録", type="primary"):
                    if ship_id and ship_name:
                        new_ship = Ship(
                            ship_id, ship_name, length, width, draft, cargo_type,
                            (lat, lon), eta, priority
                        )
                        
                        st.session_state.ships.append(new_ship)
                        st.session_state.simulator.add_ship(new_ship)
                        st.success(f"✅ 船舶 {ship_name} を登録しました!")
                        st.rerun()
                    else:
                        st.error("❌ 船舶IDと船名は必須です")
        
        # 登録済み船舶一覧
        if st.session_state.ships:
            st.subheader("📋 登録済み船舶一覧")
            
            ships_df = pd.DataFrame([
                {
                    'ID': s.id,
                    '船名': s.name,
                    '船長(m)': s.length,
                    '船幅(m)': s.width,
                    '喫水(m)': s.draft,
                    '貨物種別': s.cargo_type,
                    '優先度': s.priority,
                    'ETA': s.eta.strftime("%m/%d %H:%M")
                }
                for s in st.session_state.ships
            ])
            
            # データフレーム表示（編集可能）
            edited_ships = st.data_editor(
                ships_df,
                use_container_width=True,
                num_rows="dynamic"
            )
            
            # CSV出力
            csv = ships_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 船舶データCSV出力",
                data=csv,
                file_name=f"ships_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with tab_ports:
        st.subheader("🏭 港湾・バース管理")
        
        if st.session_state.ports:
            for port in st.session_state.ports:
                with st.expander(f"🏭 {port.name} ({port.id})", expanded=False):
                    st.write(f"**位置:** {port.location}")
                    st.write(f"**バース数:** {len(port.berths)}")
                    
                    # バース詳細
                    berth_data = []
                    for berth in port.berths:
                        berth_data.append({
                            'バースID': berth.id,
                            'バース名': berth.name,
                            '長さ(m)': berth.length,
                            '幅(m)': berth.width,
                            '最大喫水(m)': berth.max_draft,
                            '対応貨物': ', '.join(berth.cargo_types),
                            '時間単価(¥)': f"¥{berth.hourly_cost:,}"
                        })
                    
                    if berth_data:
                        berths_df = pd.DataFrame(berth_data)
                        st.dataframe(berths_df, use_container_width=True)
    
    with tab_config:
        st.subheader("⚙️ システム設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎛️ シミュレーション設定**")
            
            max_iterations = st.number_input("最大反復回数", 
                                           min_value=100, max_value=10000, value=1000)
            convergence_threshold = st.number_input("収束閾値", 
                                                  min_value=0.001, max_value=0.1, value=0.01)
            weather_factor = st.slider("気象影響係数", 0.0, 2.0, 1.0)
        
        with col2:
            st.markdown("**💰 コスト設定**")
            
            fuel_cost_rate = st.number_input("燃料費レート(¥/NM)", value=1000.0)
            waiting_cost_rate = st.number_input("待機費レート(¥/h)", value=5000.0)
            delay_penalty_rate = st.number_input("遅延ペナルティ(¥/h)", value=10000.0)
        
        if st.button("💾 設定保存", type="primary"):
            # 設定をセッション状態に保存
            st.session_state.simulation_config = {
                'max_iterations': max_iterations,
                'convergence_threshold': convergence_threshold,
                'weather_factor': weather_factor,
                'fuel_cost_rate': fuel_cost_rate,
                'waiting_cost_rate': waiting_cost_rate,
                'delay_penalty_rate': delay_penalty_rate
            }
            st.success("✅ 設定を保存しました!")

def show_analysis_report_tab():
    """分析レポートタブ"""
    st.header("📈 分析レポート")
    
    if not st.session_state.simulation_results:
        st.info("📊 シミュレーション実行後にレポートが表示されます")
        return
    
    results = st.session_state.simulation_results
    
    # レポートサマリー
    st.markdown("## 📋 実行サマリー")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("処理船舶数", results.get('total_ships', 0))
    with col2:
        st.metric("配船成功数", results.get('successful_allocations', 0))
    with col3:
        success_rate = results.get('success_rate', 0) * 100
        st.metric("成功率", f"{success_rate:.1f}%")
    with col4:
        st.metric("総費用", f"¥{results.get('total_cost', 0):,.0f}")
    
    # 詳細分析グラフ
    if 'allocations' in results and results['allocations']:
        st.markdown("## 📊 詳細分析")
        
        # データ準備
        allocation_data = []
        for ship_id, alloc in results['allocations'].items():
            allocation_data.append({
                'ship_id': ship_id,
                'port': alloc['port_name'],
                'berth': alloc['berth_name'],
                'total_cost': alloc['total_cost'],
                'waiting_time': alloc['waiting_time'],
                'processing_time': alloc.get('processing_time', 0)
            })
        
        df = pd.DataFrame(allocation_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 港湾別費用分析
            port_costs = df.groupby('port')['total_cost'].sum().reset_index()
            fig_port_costs = px.bar(
                port_costs, 
                x='port', 
                y='total_cost',
                title="🏭 港湾別総費用",
                labels={'total_cost': '総費用(¥)', 'port': '港湾'}
            )
            st.plotly_chart(fig_port_costs, use_container_width=True)
        
        with col2:
            # 待機時間分析
            fig_waiting = px.box(
                df, 
                x='port', 
                y='waiting_time',
                title="⏰ 港湾別待機時間分布",
                labels={'waiting_time': '待機時間(h)', 'port': '港湾'}
            )
            st.plotly_chart(fig_waiting, use_container_width=True)
        
        # 詳細データテーブル
        st.markdown("## 📋 詳細データ")
        st.dataframe(df, use_container_width=True)
        
        # レポート出力
        col_a, col_b = st.columns(2)
        
        with col_a:
            csv_report = df.to_csv()
