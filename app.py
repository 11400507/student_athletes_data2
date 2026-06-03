import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 設定頁面與標題
st.set_page_config(page_title="學生運動員調查數據儀表板", page_icon="📊", layout="wide")
st.title("📊 國科會學生運動員調查資料分析")

# 2. 讀取資料並進行編碼轉換
@st.cache_data
def load_data():
    df = pd.read_csv("student_athletes_data.csv")
    
    # 將整份資料表中的空白值 (NaN) 全部補為 99
    df = df.fillna(99)
    
    # 依據 Codebook 轉換運動項目 (v1)
    sport_mapping = {
        1: '籃球', 2: '足球', 3: '排球', 4: '羽球', 5: '桌球', 
        6: '網球', 7: '棒球', 8: '木球', 9: '合球', 10: '軟式網球',
        11: '田徑', 12: '游泳', 13: '體操', 14: '柔道', 15: '擊劍',
        16: '射箭', 17: '舉重', 18: '射擊', 19: '拳擊', 20: '角力',
        21: '划船', 22: '輕艇', 23: '卡巴迪', 24: '劍道', 25: '跆拳道',
        26: '空手道', 27: '自由車', 28: '高爾夫', 29: '其他'
    }
    df['運動項目'] = df['v1'].map(sport_mapping)
    return df

df = load_data()

# 3. --- 左側側邊欄 (Sidebar) 互動控制中心 ---
st.sidebar.header("⚙️ 儀表板控制中心")

# 控制項 A：運動項目多選器
st.sidebar.subheader("📌 1. 篩選資料範圍")
all_sports = df['運動項目'].dropna().unique().tolist()
default_sports = [s for s in ['體操', '田徑', '游泳', '籃球', '羽球'] if s in all_sports]
if not default_sports:
    default_sports = all_sports[:5]

selected_sports = st.sidebar.multiselect(
    "選擇運動項目（全域連動）：",
    options=all_sports,
    default=default_sports
)

st.sidebar.divider()

# 控制項 B：逐題分析多選選單 (主要連動分頁二)
st.sidebar.subheader("📚 2. 選擇分析題項 (可多選)")
exclude_cols = ['運動項目']
available_cols = [col for col in df.columns if col not in exclude_cols]

default_q = ['v2_1'] if 'v2_1' in available_cols else [available_cols[0]]

selected_qs = st.sidebar.multiselect(
    "請選擇問卷題號（連動分頁二）：",
    options=available_cols,
    default=default_q
)

st.sidebar.divider()

# 控制項 C：圖表類型與視覺設定
st.sidebar.subheader("🎨 3. 視覺化圖表設定")
chart_type = st.sidebar.selectbox(
    "為下方分析選擇最適合的圖表類型：",
    ["直立長條圖 (Bar)", "水平長條圖 (Horizontal Bar)", "圓餅圖 (Pie)", "甜甜圈圖 (Donut)", "板塊樹狀圖 (Treemap)"]
)

color_theme = st.sidebar.selectbox(
    "選擇全域圖表配色主題：",
    ["Set2 (柔和)", "Pastel (粉彩)", "Plasma (高對比漸層)", "Viridis (專業漸層)", "Plotly (經典藍)"]
)

st.sidebar.divider()

# 控制項 D：旭日圖專屬多層級設定
st.sidebar.subheader("🎯 4. 旭日圖層級設定")
st.sidebar.markdown("可以自由選擇多個題目組合，依序**由內向外**層層發散堆疊。")

sunburst_options = ['運動項目'] + available_cols
default_sunburst = [s for s in ['v67_1', 'v2_1', '運動項目'] if s in sunburst_options]
if not default_sunburst:
    default_sunburst = sunburst_options[:3]

sunburst_paths = st.sidebar.multiselect(
    "自訂旭日圖架構（層級由內向外）：",
    options=sunburst_options,
    default=default_sunburst
)

# 配色字典對應
color_dict = {
    "Set2 (柔和)": px.colors.qualitative.Set2,
    "Pastel (粉彩)": px.colors.qualitative.Pastel,
    "Plasma (高對比漸層)": px.colors.sequential.Plasma,
    "Viridis (專業漸層)": px.colors.sequential.Viridis,
    "Plotly (經典藍)": px.colors.qualitative.Plotly
}

# 核心過濾資料集
filtered_df = df[df['運動項目'].isin(selected_sports)]

if filtered_df.empty:
    st.warning("⚠️ 請從左側選單至少選擇一項運動項目！")
    st.stop()


# 4. --- 右側主畫面：建立分頁 (Tabs) ---
tab1, tab2, tab3 = st.tabs(["🌟 核心指標總覽", "📊 自選題項動態探索", "📋 全題項完整報告"])

# ==========================================
# Tab 1: 核心指標總覽
# ==========================================
with tab1:
    sport_counts = filtered_df['運動項目'].value_counts().reset_index()
    sport_counts.columns = ['運動項目', '樣本數']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏵️ 極座標玫瑰圖 (各運動項目人數)")
        fig_rose = px.bar_polar(
            sport_counts, r='樣本數', theta='運動項目', color='運動項目',
            color_discrete_sequence=color_dict[color_theme]
        )
        fig_rose.update_layout(
            polar=dict(radialaxis=dict(showticklabels=False)),
            showlegend=False
        )
        st.plotly_chart(fig_rose, use_container_width=True, key="tab1_rose_chart")

    with col2:
        st.subheader("☀️ 多層級互動旭日圖")
        
        if sunburst_paths:
            df_sunburst = filtered_df.copy()
            
            for path_col in sunburst_paths:
                df_sunburst[path_col] = df_sunburst[path_col].astype(str).str.replace('.0', '', regex=False)
                df_sunburst[path_col] = df_sunburst[path_col].replace({'99': '99 (不適用/未填)'})
                
                if path_col == 'v67_1':
                    df_sunburst[path_col] = df_sunburst[path_col].replace({'1': '有家庭資助', '0': '無家庭資助'})
                elif path_col == 'v2_1':
                    df_sunburst[path_col] = df_sunburst[path_col].replace({'1': '臺灣人', '0': '非臺灣人'})
            
            fig_sunburst = px.sunburst(
                df_sunburst, 
                path=sunburst_paths, 
                color=sunburst_paths[0], 
                color_discrete_sequence=color_dict[color_theme]
            )
            fig_sunburst.update_traces(textinfo='label+percent parent')
            st.plotly_chart(fig_sunburst, use_container_width=True, key="tab1_sunburst_chart")
        else:
            st.info("💡 請在左側側邊欄「🎯 4. 旭日圖層級設定」勾選題目，即可動態生成多層螺旋圖。")

# ==========================================
# Tab 2: 自選題項動態探索 (可多選比較)
# ==========================================
with tab2:
    st.header("🔍 自選題項描述統計比較")
    
    if not selected_qs:
        st.info("💡 請從左側的「📚 2. 選擇分析題項」選擇至少一個題目來進行分析。")
    else:
        st.markdown(f"目前共選擇了 **{len(selected_qs)}** 個題項。")
        
        for q in selected_qs:
            st.subheader(f"📌 題項 {q} 描述性統計")
            
            q_counts = filtered_df[q].value_counts().reset_index()
            q_counts.columns = ['選項代碼 / 數值', '次數']
            
            q_counts['選項代碼 / 數值'] = q_counts['選項代碼 / 數值'].astype(str)
            q_counts['選項代碼 / 數值'] = q_counts['選項代碼 / 數值'].str.replace('.0', '', regex=False)
            q_counts['選項代碼 / 數值'] = q_counts['選項代碼 / 數值'].replace({'99': '99 (不適用/未填)'})
            q_counts = q_counts.sort_values(by='選項代碼 / 數值')
            
            if chart_type == "直立長條圖 (Bar)":
                fig_q = px.bar(q_counts, x='選項代碼 / 數值', y='次數', text='次數', color='選項代碼 / 數值', color_discrete_sequence=color_dict[color_theme])
                fig_q.update_traces(textposition='outside')
                fig_q.update_layout(xaxis_type='category', showlegend=False)
            elif chart_type == "水平長條圖 (Horizontal Bar)":
                q_counts = q_counts.sort_values(by='次數', ascending=True)
                fig_q = px.bar(q_counts, y='選項代碼 / 數值', x='次數', text='次數', orientation='h', color='選項代碼 / 數值', color_discrete_sequence=color_dict[color_theme])
                fig_q.update_traces(textposition='outside')
                fig_q.update_layout(yaxis_type='category', showlegend=False)
            elif chart_type in ["圓餅圖 (Pie)", "甜甜圈圖 (Donut)"]:
                fig_q = px.pie(q_counts, names='選項代碼 / 數值', values='次數', hole=(0.4 if chart_type == "甜甜圈圖 (Donut)" else 0), color_discrete_sequence=color_dict[color_theme])
                fig_q.update_traces(textinfo='percent+label')
            elif chart_type == "板塊樹狀圖 (Treemap)":
                fig_q = px.treemap(q_counts, path=['選項代碼 / 數值'], values='次數', color='次數', color_continuous_scale=color_dict[color_theme])
                fig_q.update_traces(textinfo='label+value+percent entry')

            st.plotly_chart(fig_q, use_container_width=True, key=f"tab2_chart_{q}")
            
            with st.expander(f"📄 查看 {q} 數據次數分配表"):
                st.dataframe(q_counts, use_container_width=True)
            st.divider()

# ==========================================
# Tab 3: 全題項完整報告 (照順序一整排列出)
# ==========================================
with tab3:
    st.header("📋 全題項完整統計報告")
    st.markdown(f"此頁面會自動依序排列問卷中的所有欄位（共 **{len(available_cols)}** 題），並即時連動左側的「運動項目篩選」與「視覺化設定」。")
    
    for q in available_cols:
        st.subheader(f"📊 題項 {q} 描述性統計報告")
        
        q_counts_all = filtered_df[q].value_counts().reset_index()
        q_counts_all.columns = ['選項代碼 / 數值', '次數']
        
        q_counts_all['選項代碼 / 數值'] = q_counts_all['選項代碼 / 數值'].astype(str)
        q_counts_all['選項代碼 / 數值'] = q_counts_all['選項代碼 / 數值'].str.replace('.0', '', regex=False)
        q_counts_all['選項代碼 / 數值'] = q_counts_all['選項代碼 / 數值'].replace({'99': '99 (不適用/未填)'})
        q_counts_all = q_counts_all.sort_values(by='選項代碼 / 數值')
        
        if chart_type == "直立長條圖 (Bar)":
            fig_all = px.bar(q_counts_all, x='選項代碼 / 數值', y='次數', text='次數', color='選項代碼 / 數值', color_discrete_sequence=color_dict[color_theme])
            fig_all.update_traces(textposition='outside')
            fig_all.update_layout(xaxis_type='category', showlegend=False)
        elif chart_type == "水平長條圖 (Horizontal Bar)":
            q_counts_all = q_counts_all.sort_values(by='次數', ascending=True)
            fig_all = px.bar(q_counts_all, y='選項代碼 / 數值', x='次數', text='次數', orientation='h', color='選項代碼 / 數值', color_discrete_sequence=color_dict[color_theme])
            fig_all.update_traces(textposition='outside')
            fig_all.update_layout(yaxis_type='category', showlegend=False)
        elif chart_type in ["圓餅圖 (Pie)", "甜甜圈圖 (Donut)"]:
            fig_all = px.pie(q_counts_all, names='選項代碼 / 數值', values='次數', hole=(0.4 if chart_type == "甜甜圈圖 (Donut)" else 0), color_discrete_sequence=color_dict[color_theme])
            fig_all.update_traces(textinfo='percent+label')
        elif chart_type == "板塊樹狀圖 (Treemap)":
            fig_all = px.treemap(q_counts_all, path=['選項代碼 / 數值'], values='次數', color='次數', color_continuous_scale=color_dict[color_theme])
            fig_all.update_traces(textinfo='label+value+percent entry')
            
        st.plotly_chart(fig_all, use_container_width=True, key=f"tab3_chart_{q}")
        
        with st.expander(f"📄 查看 {q} 數據次數分配表"):
            st.dataframe(q_counts_all, use_container_width=True)
            
        st.divider() 

    with st.expander("📄 查看當前篩選條件下的完整原始資料表"):
        st.dataframe(filtered_df)