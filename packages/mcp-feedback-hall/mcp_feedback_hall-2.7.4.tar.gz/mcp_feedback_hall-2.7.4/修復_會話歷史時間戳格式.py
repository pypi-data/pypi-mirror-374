# 生成時間：2025-09-07 06:23:26
# 功能描述：修復 session_history.json 中 created_at 格式不一致問題

import json
import time
from pathlib import Path
import shutil
from datetime import datetime

def normalize_timestamp_to_milliseconds(timestamp):
    """
    統一時間戳格式為毫秒級整數
    
    Args:
        timestamp: 可能是秒級浮點數或毫秒級整數
    
    Returns:
        毫秒級整數時間戳
    """
    if isinstance(timestamp, (int, float)):
        if timestamp > 1e12:  # 已經是毫秒級
            return int(timestamp)
        else:  # 秒級，需要轉換
            return int(timestamp * 1000)
    return timestamp

def fix_session_history_timestamps():
    """修復會話歷史中的時間戳格式問題"""
    
    # 設定檔案路徑
    config_dir = Path.home() / ".config" / "mcp-feedback-hall"
    history_file = config_dir / "session_history.json"
    backup_file = config_dir / f"session_history_backup_{int(time.time())}.json"
    
    print(f"🔍 檢查歷史檔案：{history_file}")
    
    if not history_file.exists():
        print("❌ 歷史檔案不存在")
        return False
    
    try:
        # 備份原檔案
        shutil.copy2(history_file, backup_file)
        print(f"✅ 已備份原檔案到：{backup_file}")
        
        # 讀取現有資料
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        sessions = data.get("sessions", [])
        print(f"📊 發現 {len(sessions)} 個會話記錄")
        
        # 統計修復前的格式
        format_stats = {"milliseconds": 0, "seconds_float": 0, "invalid": 0}
        
        # 修復每個會話的時間戳
        fixed_count = 0
        for i, session in enumerate(sessions):
            session_id = session.get("session_id", f"session_{i}")
            
            # 檢查 created_at
            if "created_at" in session:
                original_timestamp = session["created_at"]
                
                # 統計原格式
                if isinstance(original_timestamp, (int, float)):
                    if original_timestamp > 1e12:
                        format_stats["milliseconds"] += 1
                    else:
                        format_stats["seconds_float"] += 1
                else:
                    format_stats["invalid"] += 1
                
                # 修復格式
                fixed_timestamp = normalize_timestamp_to_milliseconds(original_timestamp)
                
                if fixed_timestamp != original_timestamp:
                    print(f"🔧 修復會話 {session_id[:8]}... 時間戳：{original_timestamp} → {fixed_timestamp}")
                    session["created_at"] = fixed_timestamp
                    fixed_count += 1
            
            # 同樣修復 last_activity
            if "last_activity" in session:
                original_timestamp = session["last_activity"]
                fixed_timestamp = normalize_timestamp_to_milliseconds(original_timestamp)
                if fixed_timestamp != original_timestamp:
                    session["last_activity"] = fixed_timestamp
            
            # 修復 user_messages 中的 timestamp
            if "user_messages" in session:
                for msg in session["user_messages"]:
                    if "timestamp" in msg:
                        original_timestamp = msg["timestamp"]
                        fixed_timestamp = normalize_timestamp_to_milliseconds(original_timestamp)
                        if fixed_timestamp != original_timestamp:
                            msg["timestamp"] = fixed_timestamp
        
        # 修復根級別的時間戳
        if "lastCleanup" in data:
            data["lastCleanup"] = normalize_timestamp_to_milliseconds(data["lastCleanup"])
        
        if "savedAt" in data:
            data["savedAt"] = normalize_timestamp_to_milliseconds(data["savedAt"])
        else:
            data["savedAt"] = int(time.time() * 1000)
        
        # 重新排序會話（按修復後的 created_at）
        sessions.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        
        # 保存修復後的檔案
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📈 **修復統計**：")
        print(f"   ✅ 修復的會話數：{fixed_count}")
        print(f"   📊 原格式統計：毫秒級 {format_stats['milliseconds']} 個，秒級 {format_stats['seconds_float']} 個，無效 {format_stats['invalid']} 個")
        print(f"   💾 修復後檔案：{history_file}")
        print(f"   🔄 備份檔案：{backup_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 修復過程發生錯誤：{e}")
        # 如果出錯，恢復備份
        if backup_file.exists():
            shutil.copy2(backup_file, history_file)
            print(f"🔄 已恢復原檔案")
        return False

def verify_fix():
    """驗證修復結果"""
    config_dir = Path.home() / ".config" / "mcp-feedback-hall"
    history_file = config_dir / "session_history.json"
    
    if not history_file.exists():
        print("❌ 歷史檔案不存在")
        return False
    
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        sessions = data.get("sessions", [])
        print(f"\n🔍 **驗證結果**：")
        print(f"   📋 總會話數：{len(sessions)}")
        
        # 檢查時間戳格式
        all_good = True
        for i, session in enumerate(sessions):
            session_id = session.get("session_id", f"session_{i}")
            created_at = session.get("created_at")
            
            if created_at:
                if not isinstance(created_at, int) or created_at <= 1e12:
                    print(f"   ⚠️ 會話 {session_id[:8]}... 時間戳格式仍有問題：{created_at}")
                    all_good = False
                else:
                    # 轉換為人類可讀時間
                    readable_time = datetime.fromtimestamp(created_at / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    print(f"   ✅ 會話 {session_id[:8]}... 時間戳正常：{readable_time}")
        
        if all_good:
            print(f"   🎉 所有時間戳格式都已修復！")
        
        return all_good
        
    except Exception as e:
        print(f"❌ 驗證過程發生錯誤：{e}")
        return False

if __name__ == "__main__":
    print("🚀 開始修復會話歷史時間戳格式...")
    
    if fix_session_history_timestamps():
        print("\n✅ 修復完成，開始驗證...")
        verify_fix()
        print("\n🔗 修復完成後，請重新啟動 mcp-feedback-hall 服務以使變更生效")
        print("💡 建議在 127.0.0.1:9877 檢查會話歷史是否正常顯示")
    else:
        print("\n❌ 修復失敗，請檢查錯誤訊息")

