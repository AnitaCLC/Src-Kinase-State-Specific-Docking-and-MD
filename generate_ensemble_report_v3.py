import os
import glob
import pandas as pd
import numpy as np
import logging

# 設定 RDKit 的 log 層級，隱藏 Warning
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    from rdkit import RDLogger
    RDLogger.DisableLog('rdApp.*')  # 關閉所有 RDKit 警告訊息
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False
    print("⚠️ 警告: 未安裝 rdkit。將嘗試從 SDF 標籤讀取分子量。如果表格內分子量為空，請考慮安裝 rdkit (conda install -c conda-forge rdkit)")

BASE_DIR = "/home/anita/src_kinase_docking"
RESULTS_DIR = os.path.join(BASE_DIR, "docking_results")
OUTPUT_EXCEL = os.path.join(BASE_DIR, "Ensemble_Docking_State_Specific_Report_Detailed.xlsx")

def parse_sdf_data(sdf_path):
    """從 GNINA SDF 檔中提取 Vina Affinity, CNN Score, CNN Affinity 與分子量"""
    data = {'minimizedAffinity': np.nan, 'CNNscore': np.nan, 'CNNaffinity': np.nan, 'MW': np.nan}
    try:
        # 1. 讀取分數標籤
        with open(sdf_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "<minimizedAffinity>" in line:
                    data['minimizedAffinity'] = float(lines[i+1].strip())
                elif "<CNNscore>" in line:
                    data['CNNscore'] = float(lines[i+1].strip())
                elif "<CNNaffinity>" in line:
                    data['CNNaffinity'] = float(lines[i+1].strip())
                # 若藥物庫自帶分子量標籤
                elif "<MW>" in line or "<Molecular_Weight>" in line or "<EXACT_MASS>" in line: 
                    try:
                        data['MW'] = float(lines[i+1].strip())
                    except:
                        pass
                        
        # 2. 如果沒有 MW 標籤且有安裝 RDKit，直接從 SDF 結構計算真實分子量
        if pd.isna(data['MW']) and HAS_RDKIT:
            try:
                suppl = Chem.SDMolSupplier(sdf_path)
                mol = suppl[0]
                if mol is not None:
                    data['MW'] = Descriptors.MolWt(mol)
            except:
                pass
    except Exception as e:
        pass
    return data

print("🔍 正在掃描已完成的快照資料夾...")
result_dirs = sorted(glob.glob(os.path.join(RESULTS_DIR, "3_GNINA_Results_*")))

# 定義要分類的 4 種狀態
states = ['double', 'pY419', 'pY530', 'unpho']
records = []

for r_dir in result_dirs:
    snapshot_full_name = os.path.basename(r_dir).replace("3_GNINA_Results_snapshot_", "")
    
    # 判斷資料夾屬於哪個狀態
    current_state = "unknown"
    for s in states:
        if s in snapshot_full_name:
            current_state = s
            break
            
    sdf_files = glob.glob(os.path.join(r_dir, "*_docked.sdf"))
    
    if len(sdf_files) < 3000:
        print(f"⏩ 跳過尚未完成的快照: {snapshot_full_name} (目前 {len(sdf_files)} 個檔案)")
        continue
        
    print(f"📊 正在處理快照: {snapshot_full_name} ({current_state} 態, {len(sdf_files)} 個檔案)...")
    
    for sdf_file in sdf_files:
        drug_name = os.path.basename(sdf_file).replace("_docked.sdf", "")
        metrics = parse_sdf_data(sdf_file)
        
        records.append({
            'Drug_Name': drug_name,
            'State': current_state,
            'Snapshot': snapshot_full_name,
            'Vina_Affinity': metrics['minimizedAffinity'],
            'CNN_Score': metrics['CNNscore'],
            'CNN_Affinity': metrics['CNNaffinity'],
            'MW': metrics['MW']
        })

if not records:
    print("⚠️ 目前尚未有快照達到完工門檻 (2000+ 檔案)。")
    exit()

# 轉換為 DataFrame
df_all = pd.DataFrame(records)

# 嚴格過濾：只保留符合「激酶小分子抑制劑」特徵的配體
# 排除金屬離子/碎片 (MW < 150) 以及巨集分子 (MW > 1000)
df_all = df_all[(df_all['MW'] >= 150) & (df_all['MW'] <= 1000)].copy()

print("\n📝 正在計算各狀態的分數並進行排名 (以 CNN Score 為主)...")

# 匯出至 Excel
with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
    for state in states:
        df_state = df_all[df_all['State'] == state].copy()
        if df_state.empty:
            continue
            
        # 1. 取得該狀態下的所有快照名稱 (例如 80000ps, 85000ps...)
        snapshots_in_state = sorted(df_state['Snapshot'].unique())
        
        # 2. 為了將快照分數攤平為欄位，我們使用 pivot
        #    我們先做一個包含平均值的 summary table
        summary = df_state.groupby('Drug_Name').agg({
            'CNN_Score': 'mean',
            'Vina_Affinity': 'mean',
            'CNN_Affinity': 'mean',
            'MW': 'first'
        }).reset_index()
        
        # 3. 使用 pivot 展開每個 frame 的 CNN Affinity
        pivot_affinity = df_state.pivot(index='Drug_Name', columns='Snapshot', values='CNN_Affinity').reset_index()
        
        # 重新命名 pivot 後的欄位，加上後綴以明確標示
        rename_dict = {snap: f"{snap} (CNN Affinity)" for snap in snapshots_in_state}
        pivot_affinity.rename(columns=rename_dict, inplace=True)
        
        # 4. 合併 summary 與展開的 frame 分數
        final_df = pd.merge(summary, pivot_affinity, on='Drug_Name', how='left')
        
        # 5. 依據 CNN Score 遞減排序
        final_df_sorted = final_df.sort_values(by='CNN_Score', ascending=False)
        
        # 6. 整理最終輸出的欄位順序與名稱
        # 固定欄位
        base_cols = ['Drug_Name', 'CNN_Score', 'Vina_Affinity', 'CNN_Affinity', 'MW']
        # 動態展開的 frame 欄位
        frame_cols = [f"{snap} (CNN Affinity)" for snap in snapshots_in_state]
        
        final_df_sorted = final_df_sorted[base_cols + frame_cols]
        
        # 替換基礎欄位名稱
        rename_base = {
            'Drug_Name': '藥物名稱',
            'CNN_Score': 'CNN Score (平均)',
            'Vina_Affinity': 'Vina Affinity (平均)',
            'CNN_Affinity': 'CNN Affinity (平均)',
            'MW': '分子量 (MW)'
        }
        final_df_sorted.rename(columns=rename_base, inplace=True)
        
        # 將狀態寫入各自的 Excel 分頁
        sheet_name = f'{state} 排名'
        final_df_sorted.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"  - 已生成分頁: {sheet_name}")

print(f"\n🎉 成功匯出多狀態分類對接報表 (含詳細 Frame 分數): {OUTPUT_EXCEL}")