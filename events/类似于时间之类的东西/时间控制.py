"""
时间控制事件模块
实现Pera幻想FOD中的时间服务器功能
所有时间操作统一通过此事件接口调用
"""

import re
from typing import Dict, Any, Optional, Tuple


class TimeManager:
    """时间管理器类 - 负责所有时间操作和计算"""
    
    def __init__(self, time_csv_data: Dict[str, str]):
        """
        初始化时间管理器
        
        Args:
            time_csv_data: 从time.csv读取的配置数据
        """
        # 解析时间单位配置
        self.parse_time_config(time_csv_data)
        
        # 解析节日配置
        self.parse_festival_config(time_csv_data)
        
        # 当前时间状态（初始化为默认值）
        self.current_time = {
            'YEAR': 1,
            'MONTH': 1,
            'DAY': 1,
            'HOUR': 0,
            'MINUTE': 0,
            'WEEKDAY': 1,  # 星期一
            'TOTAL_MINUTES': 0,
            'CURRENT_FESTIVAL': None
        }
        
        # 初始化时检查节日
        self._check_festival()
        
    def parse_time_config(self, csv_data: Dict[str, str]):
        """
        解析时间单位配置
        
        从time.csv中读取年、月、日、时的标准定义
        """
        # 默认值（按照文档说明）
        defaults = {
            'YEAR': 12,    # 一年12月
            'MONTH': 30,   # 一月30日
            'DAY': 24,     # 一日24时
            'HOUR': 60     # 一时60分
        }
        
        # 从CSV读取配置，如果读取失败则使用默认值
        try:
            self.units_per_year = int(csv_data.get('年', defaults['YEAR']))
            self.days_per_month = int(csv_data.get('月', defaults['MONTH']))
            self.hours_per_day = int(csv_data.get('日', defaults['DAY']))
            self.minutes_per_hour = int(csv_data.get('时', defaults['HOUR']))
        except (ValueError, TypeError):
            # 如果解析失败，使用默认值
            self.units_per_year = defaults['YEAR']
            self.days_per_month = defaults['MONTH']
            self.hours_per_day = defaults['DAY']
            self.minutes_per_hour = defaults['HOUR']
    
    def parse_festival_config(self, csv_data: Dict[str, str]):
        """
        解析节日配置
        
        支持格式：
        - 新年[月:1|日:1]
        - ex,[月:{1:30-2:28}|日:{1(月):1(日):新年}]
        """
        self.festivals = {}  # 格式: {(月, 日): "节日名"}
        
        festival_str = csv_data.get('节日', '')
        if not festival_str:
            return
        
        # 匹配基本节日格式：节日名[月:xx|日:xx]
        basic_pattern = r'([^\[]+)\[月:(\d+)\|日:(\d+)\]'
        matches = re.findall(basic_pattern, festival_str)
        
        for festival_name, month, day in matches:
            try:
                m = int(month)
                d = int(day)
                self.festivals[(m, d)] = festival_name.strip()
            except ValueError:
                continue
        
        # 匹配扩展格式（如果存在）
        # ex,[月:{1:xx-2:xx}|日:{1(月):1(日):xx节}]
        if 'ex,[' in festival_str:
            self._parse_extended_festivals(festival_str)
    
    def _parse_extended_festivals(self, ex_str: str):
        """解析扩展格式的节日配置"""
        # 这里可以扩展支持更复杂的节日格式
        # 目前先支持基本格式
        pass
    
    def add_time(self, years: int = 0, months: int = 0, days: int = 0, 
                 hours: int = 0, minutes: int = 0) -> Dict[str, Any]:
        """
        增加时间（支持多单位组合）
        
        Args:
            years: 增加的年数
            months: 增加的月数
            days: 增加的天数
            hours: 增加的小时数
            minutes: 增加的分钟数
        
        Returns:
            更新后的时间状态
        """
        # 先将所有时间转换为总分钟数
        total_minutes_added = 0
        
        total_minutes_added += minutes
        total_minutes_added += hours * self.minutes_per_hour
        total_minutes_added += days * self.minutes_per_hour * self.hours_per_day
        total_minutes_added += months * self.days_per_month * self.hours_per_day * self.minutes_per_hour
        total_minutes_added += years * self.units_per_year * self.days_per_month * self.hours_per_day * self.minutes_per_hour
        
        # 更新总分钟数
        self.current_time['TOTAL_MINUTES'] += total_minutes_added
        
        # 重新计算各个时间单位
        self._recalculate_from_total_minutes()
        
        # 检查节日
        self._check_festival()
        
        return self.current_time.copy()
    
    def _recalculate_from_total_minutes(self):
        """从总分钟数重新计算年、月、日、时、分"""
        total = self.current_time['TOTAL_MINUTES']
        
        # 计算年
        minutes_per_year = (self.units_per_year * self.days_per_month * 
                           self.hours_per_day * self.minutes_per_hour)
        years = total // minutes_per_year
        remaining_minutes = total % minutes_per_year
        
        # 计算月
        minutes_per_month = self.days_per_month * self.hours_per_day * self.minutes_per_hour
        months = remaining_minutes // minutes_per_month
        remaining_minutes = remaining_minutes % minutes_per_month
        
        # 计算日
        minutes_per_day = self.hours_per_day * self.minutes_per_hour
        days = remaining_minutes // minutes_per_day
        remaining_minutes = remaining_minutes % minutes_per_day
        
        # 计算时
        hours = remaining_minutes // self.minutes_per_hour
        minutes = remaining_minutes % self.minutes_per_hour
        
        # 更新时间状态（注意：年和月需要+1，因为游戏时间从1开始）
        self.current_time['YEAR'] = years + 1
        self.current_time['MONTH'] = months + 1
        self.current_time['DAY'] = days + 1
        self.current_time['HOUR'] = hours
        self.current_time['MINUTE'] = minutes
        
        # 计算星期（假设每年第1天是星期一）
        total_days = years * self.units_per_year * self.days_per_month + \
                    months * self.days_per_month + days
        self.current_time['WEEKDAY'] = (total_days % 7) + 1  # 1-7表示周一到周日
    
    def _check_festival(self):
        """检查当前日期是否是节日"""
        month = self.current_time['MONTH']
        day = self.current_time['DAY']
        
        festival = self.festivals.get((month, day))
        self.current_time['CURRENT_FESTIVAL'] = festival
    
    def get_time_info(self, format_type: str = 'standard') -> Any:
        """
        获取时间信息
        
        Args:
            format_type: 返回格式类型
                - 'standard': 标准字典格式
                - 'string': 格式化字符串（如：第1年 1月1日 0时0分）
                - 'compact': 紧凑格式（如：1-1-0-0）
                - 'weekday': 仅返回星期几
                - 'festival': 仅返回节日信息
        
        Returns:
            根据format_type返回对应格式的数据
        """
        if format_type == 'standard':
            return self.current_time.copy()
        
        elif format_type == 'string':
            return (f"第{self.current_time['YEAR']}年 "
                   f"{self.current_time['MONTH']}月{self.current_time['DAY']}日 "
                   f"{self.current_time['HOUR']}时{self.current_time['MINUTE']}分 "
                   f"星期{self._weekday_to_chinese(self.current_time['WEEKDAY'])}")
        
        elif format_type == 'compact':
            return (f"{self.current_time['YEAR']}-"
                   f"{self.current_time['MONTH']}-"
                   f"{self.current_time['DAY']}-"
                   f"{self.current_time['HOUR']}-"
                   f"{self.current_time['MINUTE']}")
        
        elif format_type == 'weekday':
            return self._weekday_to_chinese(self.current_time['WEEKDAY'])
        
        elif format_type == 'festival':
            festival = self.current_time['CURRENT_FESTIVAL']
            if festival:
                return f"今天是{festival}！"
            else:
                return "今天没有特殊节日"
        
        else:
            return self.current_time.copy()
    
    def _weekday_to_chinese(self, weekday: int) -> str:
        """将数字星期转换为中文"""
        weekdays = {
            1: '一', 2: '二', 3: '三', 4: '四', 
            5: '五', 6: '六', 7: '日'
        }
        return weekdays.get(weekday, '一')
    
    def set_time(self, year: Optional[int] = None, month: Optional[int] = None,
                 day: Optional[int] = None, hour: Optional[int] = None,
                 minute: Optional[int] = None) -> Dict[str, Any]:
        """
        设置时间到指定值
        
        Args:
            year: 设置的年份
            month: 设置的月份
            day: 设置的日期
            hour: 设置的小时
            minute: 设置的分钟
        
        Returns:
            更新后的时间状态
        """
        if year is not None and year > 0:
            self.current_time['YEAR'] = year
        if month is not None and 1 <= month <= self.units_per_year:
            self.current_time['MONTH'] = month
        if day is not None and 1 <= day <= self.days_per_month:
            self.current_time['DAY'] = day
        if hour is not None and 0 <= hour < self.hours_per_day:
            self.current_time['HOUR'] = hour
        if minute is not None and 0 <= minute < self.minutes_per_hour:
            self.current_time['MINUTE'] = minute
        
        # 重新计算总分钟数
        self._update_total_minutes()
        
        # 检查节日
        self._check_festival()
        
        return self.current_time.copy()
    
    def _update_total_minutes(self):
        """根据当前时间更新总分钟数"""
        years = self.current_time['YEAR'] - 1
        months = self.current_time['MONTH'] - 1
        days = self.current_time['DAY'] - 1
        hours = self.current_time['HOUR']
        minutes = self.current_time['MINUTE']
        
        total = 0
        total += minutes
        total += hours * self.minutes_per_hour
        total += days * self.hours_per_day * self.minutes_per_hour
        total += months * self.days_per_month * self.hours_per_day * self.minutes_per_hour
        total += years * self.units_per_year * self.days_per_month * self.hours_per_day * self.minutes_per_hour
        
        self.current_time['TOTAL_MINUTES'] = total
    
    def get_current_minutes(self) -> int:
        """获取从游戏开始到现在的总分钟数"""
        return self.current_time['TOTAL_MINUTES']
    
    def to_save_data(self) -> Dict[str, Any]:
        """
        生成可存档的数据
        
        Returns:
            可序列化的时间数据字典
        """
        return {
            'year': self.current_time['YEAR'],
            'month': self.current_time['MONTH'],
            'day': self.current_time['DAY'],
            'hour': self.current_time['HOUR'],
            'minute': self.current_time['MINUTE'],
            'weekday': self.current_time['WEEKDAY'],
            'total_minutes': self.current_time['TOTAL_MINUTES'],
            'current_festival': self.current_time['CURRENT_FESTIVAL']
        }
    
    def load_from_save_data(self, save_data: Dict[str, Any]):
        """
        从存档数据加载时间状态
        
        Args:
            save_data: 存档中的时间数据
        """
        self.current_time['YEAR'] = save_data.get('year', 1)
        self.current_time['MONTH'] = save_data.get('month', 1)
        self.current_time['DAY'] = save_data.get('day', 1)
        self.current_time['HOUR'] = save_data.get('hour', 0)
        self.current_time['MINUTE'] = save_data.get('minute', 0)
        self.current_time['WEEKDAY'] = save_data.get('weekday', 1)
        self.current_time['TOTAL_MINUTES'] = save_data.get('total_minutes', 0)
        self.current_time['CURRENT_FESTIVAL'] = save_data.get('current_festival', None)


# 全局时间管理器实例（在初始化时创建）
_time_manager_instance: Optional[TimeManager] = None


def _get_or_init_time_manager(this) -> TimeManager:
    """
    获取或初始化时间管理器实例
    
    Args:
        this: 事件上下文对象
    
    Returns:
        TimeManager实例
    """
    global _time_manager_instance
    
    if _time_manager_instance is None:
        # 从init中获取time.csv数据
        time_data = this.console.init.global_key.get('time', {})
        
        # 如果数据为空，使用默认配置
        if not time_data:
            time_data = {
                '年': '12',
                '月': '30',
                '日': '24',
                '时': '60',
                '节日': '新年[月:1|日:1]'
            }
        
        _time_manager_instance = TimeManager(time_data)
    
    return _time_manager_instance


def event_time_control(this, operation: str, **kwargs):
    """
    时间控制事件 - 统一的时间操作接口
    
    Trigger ID: time_control
    
    支持的操作:
        - 'add': 增加时间
        - 'get': 获取时间信息
        - 'set': 设置时间
        - 'init': 初始化时间系统
        - 'sync_to_global': 同步时间到全局变量
        - 'load_from_global': 从全局变量加载时间
    
    Args:
        this: 事件上下文对象
        operation: 操作类型
        **kwargs: 操作参数
    
    Returns:
        操作结果（根据操作类型返回不同数据）
    """
    # 获取时间管理器实例
    time_manager = _get_or_init_time_manager(this)
    
    # 根据操作类型执行对应逻辑
    if operation == 'add':
        # 增加时间
        # 参数: years, months, days, hours, minutes
        years = kwargs.get('years', 0)
        months = kwargs.get('months', 0)
        days = kwargs.get('days', 0)
        hours = kwargs.get('hours', 0)
        minutes = kwargs.get('minutes', 0)
        
        result = time_manager.add_time(years, months, days, hours, minutes)
        
        # 同步到全局变量
        _sync_to_global(this, time_manager)
        
        return result
    
    elif operation == 'get':
        # 获取时间信息
        # 参数: format_type ('standard', 'string', 'compact', 'weekday', 'festival')
        format_type = kwargs.get('format_type', 'standard')
        result = time_manager.get_time_info(format_type)
        
        return result
    
    elif operation == 'set':
        # 设置时间
        # 参数: year, month, day, hour, minute
        result = time_manager.set_time(
            year=kwargs.get('year'),
            month=kwargs.get('month'),
            day=kwargs.get('day'),
            hour=kwargs.get('hour'),
            minute=kwargs.get('minute')
        )
        
        # 同步到全局变量
        _sync_to_global(this, time_manager)
        
        return result
    
    elif operation == 'init':
        # 初始化时间系统（重新加载配置）
        global _time_manager_instance
        _time_manager_instance = None
        
        # 获取新实例
        time_manager = _get_or_init_time_manager(this)
        
        # 同步到全局变量
        _sync_to_global(this, time_manager)
        
        return {'status': 'initialized', 'current_time': time_manager.get_time_info('standard')}
    
    elif operation == 'sync_to_global':
        # 同步时间到全局变量
        _sync_to_global(this, time_manager)
        return {'status': 'synced'}
    
    elif operation == 'load_from_global':
        # 从全局变量加载时间
        _load_from_global(this, time_manager)
        return {'status': 'loaded', 'current_time': time_manager.get_time_info('standard')}
    
    elif operation == 'get_minutes':
        # 获取总分钟数
        return time_manager.get_current_minutes()
    
    else:
        # 未知操作
        return {'error': f'Unknown operation: {operation}'}


def _sync_to_global(this, time_manager: TimeManager):
    """
    同步时间管理器的时间到全局变量
    
    Args:
        this: 事件上下文对象
        time_manager: 时间管理器实例
    """
    # 获取全局System字典
    system_key = this.console.init.global_key.setdefault('System', {})
    
    # 更新时间数据
    system_key['YEAR'] = time_manager.current_time['YEAR']
    system_key['MONTH'] = time_manager.current_time['MONTH']
    system_key['DAY'] = time_manager.current_time['DAY']
    system_key['HOUR'] = time_manager.current_time['HOUR']
    system_key['MINUTE'] = time_manager.current_time['MINUTE']
    system_key['WEEKDAY'] = time_manager.current_time['WEEKDAY']
    system_key['TOTAL_MINUTES'] = time_manager.current_time['TOTAL_MINUTES']
    system_key['CURRENT_FESTIVAL'] = time_manager.current_time['CURRENT_FESTIVAL']


def _load_from_global(this, time_manager: TimeManager):
    """
    从全局变量加载时间到时间管理器
    
    Args:
        this: 事件上下文对象
        time_manager: 时间管理器实例
    """
    system_key = this.console.init.global_key.get('System', {})
    
    # 构建存档数据格式
    save_data = {
        'year': system_key.get('YEAR', 1),
        'month': system_key.get('MONTH', 1),
        'day': system_key.get('DAY', 1),
        'hour': system_key.get('HOUR', 0),
        'minute': system_key.get('MINUTE', 0),
        'weekday': system_key.get('WEEKDAY', 1),
        'total_minutes': system_key.get('TOTAL_MINUTES', 0),
        'current_festival': system_key.get('CURRENT_FESTIVAL', None)
    }
    
    # 加载数据
    time_manager.load_from_save_data(save_data)


# 注册事件触发器
event_time_control.event_trigger = "time_control"
