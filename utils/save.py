import json
import os
import time
import shutil

class SaveSystem:
    def __init__(self, save_dir="./save"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def _prepare_for_json(self, obj):
        """
        [核心逻辑] 递归清洗数据。
        移除无法序列化的对象（如 console, init 等），只保留纯数据。
        """
        if isinstance(obj, dict):
            # 过滤掉这些运行时对象，只存数据
            ignore_keys = ['console', 'init', 'event_manager', 'loader', '_RAW_STATE']
            return {k: self._prepare_for_json(v) for k, v in obj.items() if k not in ignore_keys}
        elif isinstance(obj, list):
            return [self._prepare_for_json(i) for i in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        # 其他类型（如 datetime）转字符串
        return str(obj)

    def get_save_info(self, slot_id):
        """获取存档槽位的元信息（用于在菜单显示）"""
        file_path = os.path.join(self.save_dir, f"save_{slot_id}.json")
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('_metadata', {})
        except Exception:
            return {"error": "损坏的存档"}

    def save_game(self, state_dict, slot_id):
        """保存游戏"""
        file_path = os.path.join(self.save_dir, f"save_{slot_id}.json")
        
        # 1. 预处理数据
        try:
            save_data = self._prepare_for_json(state_dict)
            
            # [修复] 健壮的元数据提取
            # 使用 (X or {}) 的技巧，防止 X 为 None
            master_node = state_dict.get('master') or {}
            chara_node = state_dict.get('chara') or {}
            session_node = state_dict.get('session') or {}
            
            master_name = master_node.get('name', 'Master')
            # 兼容 target 可能没有名字的情况
            target_name = chara_node.get('name', 'None') 
            location = session_node.get('location', '未知')
            date_str = time.strftime('%Y-%m-%d %H:%M:%S')
            
            save_data['_metadata'] = {
                'save_time': date_str,
                'location': location,
                'summary': f"{master_name} & {target_name} @ {location}",
                'version': '1.0'
            }

            # 3. 写入文件 (先写临时文件再重命名，防止写入中断导致坏档)
            temp_path = file_path + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            os.rename(temp_path, file_path)
            
            return True
        except Exception as e:
            print(f"存档失败: {e}")
            return False

    def load_game(self, slot_id):
        """读取存档数据"""
        file_path = os.path.join(self.save_dir, f"save_{slot_id}.json")
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读档失败: {e}")
            return None