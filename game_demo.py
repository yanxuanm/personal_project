#!/usr/bin/env python3
"""
Project Red Dust - 游戏玩法演示脚本

这是一个交互式演示，展示如何玩这个火星殖民地生存游戏。
通过API自动操作游戏，并解释每一步发生了什么。

请确保服务器正在运行：http://localhost:8000
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

def print_step(text):
    """打印步骤说明"""
    print(f"\n→ {text}")

def print_info(text):
    """打印信息"""
    print(f"  ℹ️  {text}")

def print_success(text):
    """打印成功信息"""
    print(f"  ✅ {text}")

def print_warning(text):
    """打印警告信息"""
    print(f"  ⚠️  {text}")

def get_state():
    """获取当前游戏状态"""
    try:
        response = requests.get(f"{BASE_URL}/state")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取状态失败: {e}")
        return None

def next_tick():
    """执行下一个tick"""
    try:
        response = requests.post(f"{BASE_URL}/next")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"执行tick失败: {e}")
        return None

def reset_simulation(seed=42, use_llm=False):
    """重置模拟"""
    try:
        params = {"seed": seed, "use_llm": use_llm}
        response = requests.post(f"{BASE_URL}/reset", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"重置模拟失败: {e}")
        return None

def rewind_to(tick):
    """时间旅行到指定tick"""
    try:
        response = requests.post(f"{BASE_URL}/rewind/{tick}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"时间旅行失败: {e}")
        return None

def print_resources(resources):
    """打印资源状态"""
    print("  资源状态:")
    for name, value in resources.items():
        if name == 'oxygen':
            symbol = '🫁'
        elif name == 'water':
            symbol = '💧'
        elif name == 'energy':
            symbol = '⚡'
        elif name == 'food':
            symbol = '🍖'
        else:
            symbol = '📊'
        
        # 判断资源是否危急
        if value < 100:
            status = "❗危急"
        elif value < 300:
            status = "⚠️ 警告"
        else:
            status = "✅正常"
        
        print(f"    {symbol} {name.upper()}: {value:.1f} ({status})")

def print_agents(agents):
    """打印船员状态"""
    print("  船员状态:")
    for name, agent in agents.items():
        status = "💚活着" if agent['is_alive'] else "💀死亡"
        health_icon = "❤️" if agent['health'] > 50 else "💔"
        mental_icon = "🧠" if agent['mental_state'] > 50 else "🤯"
        
        # 简化的角色说明
        roles = {
            'Commander Chen': '指挥官 - 理性领导者',
            'Engineer Tanaka': '工程师 - 技术专家',
            'Dr. Rodriguez': '医生 - 医疗专家',
            'Botanist Schmidt': '生物学家 - 植物学家',
            'Pilot Okafor': '飞行员 - 潜伏间谍'
        }
        role = roles.get(name, '船员')
        
        print(f"    👤 {name} ({role})")
        print(f"      {health_icon} 健康: {agent['health']:.1f}% | {mental_icon} 精神状态: {agent['mental_state']:.1f}%")
        print(f"      📍位置: {agent['location']} | {status}")

def print_logs(logs, count=3):
    """打印最近的日志"""
    if logs:
        print(f"  最近{count}条事件:")
        for log in logs[-count:]:
            # 简化日志显示
            if 'GAME OVER' in log:
                icon = '💀'
            elif 'CRITICAL' in log:
                icon = '🔥'
            elif 'DISASTER' in log:
                icon = '🌪️'
            elif 'RANDOM EVENT' in log:
                icon = '🎲'
            elif 'SABOTAGE' in log:
                icon = '🕵️'
            elif 'REPAIR' in log:
                icon = '🔧'
            elif 'WORK' in log:
                icon = '🛠️'
            elif 'RESEARCH' in log:
                icon = '🔬'
            elif 'TALK' in log:
                icon = '💬'
            elif 'EAT' in log:
                icon = '🍽️'
            elif 'REST' in log:
                icon = '😴'
            else:
                icon = '📝'
            
            # 提取tick和消息
            tick_match = log.find('[T')
            if tick_match != -1:
                tick_end = log.find(']', tick_match)
                tick = log[tick_match:tick_end+1]
                message = log[tick_end+2:]
            else:
                tick = ''
                message = log
            
            print(f"    {icon} {tick}: {message[:60]}...")

def demonstrate_gameplay():
    """演示游戏玩法"""
    
    print_header("项目红沙 - 火星殖民地生存游戏演示")
    print("游戏地址: http://localhost:8000/static/index.html")
    print("这个演示将通过API自动操作游戏，并解释每一步发生了什么。")
    time.sleep(2)
    
    # 第1部分：游戏介绍
    print_header("第1部分：游戏介绍")
    print_step("游戏概览")
    print_info("这是一个火星殖民地生存模拟游戏，具有以下特点：")
    print_info("1. 🪐 管理4种关键资源：氧气、水、能源、食物")
    print_info("2. 👥 5名船员各有不同的性格和秘密目标")
    print_info("3. ⏳ 确定性模拟：相同的种子产生相同的结果")
    print_info("4. 🔄 时间旅行：可以回到过去的任何时刻，创造新的时间线")
    print_info("5. 🎮 观察模式：你不能直接控制船员，但可以观察他们的决策")
    time.sleep(3)
    
    # 第2部分：重置游戏
    print_header("第2部分：开始新游戏")
    print_step("重置模拟到初始状态")
    print_info("使用种子42开始新的模拟（种子决定随机事件序列）")
    
    state = reset_simulation(seed=42, use_llm=False)
    if not state:
        print_warning("无法重置游戏，请检查服务器是否运行")
        return
    
    time.sleep(1)
    print_success("游戏已重置！")
    print_resources(state['resources'])
    print_agents(state['agents'])
    time.sleep(2)
    
    # 第3部分：运行几个tick，展示游戏进展
    print_header("第3部分：运行模拟 - 观察殖民地发展")
    print_step("执行第一个tick（游戏时间单位）")
    print_info("每个tick代表一段时间，期间：")
    print_info("- 船员根据性格和目标做出决策")
    print_info("- 资源被消耗（所有船员消耗氧气、水、食物）")
    print_info("- 系统生产资源（太阳能板产生能源等）")
    print_info("- 可能发生随机事件（设备故障等）")
    
    for i in range(1, 6):
        print_step(f"执行tick {i}")
        state = next_tick()
        if not state:
            print_warning("执行tick失败")
            break
        
        print(f"  当前tick: {state['tick']}")
        print_resources(state['resources'])
        
        # 打印船员行动（从日志中提取）
        if state['logs']:
            latest_log = state['logs'][-1]
            if ']: ' in latest_log:
                action = latest_log.split(']: ')[1]
                print(f"  最新行动: {action}")
        
        time.sleep(1)
    
    # 展示当前状态
    print_step("5个tick后的殖民地状态")
    print_resources(state['resources'])
    print_agents(state['agents'])
    
    # 检查是否有船员死亡
    alive_count = sum(1 for a in state['agents'].values() if a['is_alive'])
    if alive_count < 5:
        print_warning(f"有{5-alive_count}名船员死亡！")
    else:
        print_success("所有船员都还活着！")
    
    time.sleep(2)
    
    # 第4部分：时间旅行演示
    print_header("第4部分：时间旅行 - 改变历史")
    print_step("记录当前状态（tick 5）")
    tick5_resources = state['resources'].copy()
    tick5_alive = alive_count
    print_info(f"当前状态保存在记忆库中")
    time.sleep(1)
    
    # 继续运行到tick 10
    print_step("继续运行到tick 10")
    for i in range(6, 11):
        state = next_tick()
        if not state:
            break
        time.sleep(0.5)
    
    print_step("tick 10的状态")
    print_resources(state['resources'])
    print_agents(state['agents'])
    time.sleep(2)
    
    # 时间旅行回到tick 5
    print_step("时间旅行：回到tick 5")
    print_info("我们不喜欢这个时间线的发展，决定回到过去重新开始")
    print_info("时间旅行会：")
    print_info("1. 恢复游戏状态到tick 5的时刻")
    print_info("2. 删除tick 5之后的历史（创建新的时间线分支）")
    print_info("3. 恢复随机数生成器状态（保证确定性）")
    
    state = rewind_to(5)
    if not state:
        print_warning("时间旅行失败")
        return
    
    print_success(f"成功回到tick {state['tick']}！")
    print_resources(state['resources'])
    
    # 验证状态是否与之前记录的相同
    resources_match = True
    for name, value in tick5_resources.items():
        if abs(value - state['resources'].get(name, 0)) > 0.1:
            resources_match = False
            break
    
    if resources_match:
        print_success("状态完全恢复！时间旅行成功。")
    else:
        print_warning("状态不完全匹配，但时间旅行已完成")
    
    time.sleep(2)
    
    # 第5部分：不同的选择导致不同的结果
    print_header("第5部分：不同时间线的对比")
    print_step("在新的时间线中继续运行到tick 10")
    print_info("由于随机事件的确定性，前几个tick应该相同")
    print_info("但由于微小的差异（如船员决策时机），结果可能不同")
    
    for i in range(6, 11):
        state = next_tick()
        if not state:
            break
        time.sleep(0.5)
    
    print_step("新时间线中tick 10的状态")
    print_resources(state['resources'])
    alive_count = sum(1 for a in state['agents'].values() if a['is_alive'])
    print(f"  存活的船员: {alive_count}/5")
    
    # 比较两个时间线
    print_step("时间线比较")
    print_info("第一个时间线（原始）：tick 10的状态已丢失（被覆盖）")
    print_info("第二个时间线（当前）：展示了不同的发展路径")
    print_info("这就是时间旅行的核心：通过回到过去创造新的可能性")
    time.sleep(2)
    
    # 第6部分：游戏界面说明
    print_header("第6部分：Web界面使用指南")
    print_step("打开浏览器访问: http://localhost:8000/static/index.html")
    print_info("界面分为以下几个区域：")
    print_info("")
    print_info("1. 🖥️  顶部状态栏")
    print_info("   - 显示MARS_OS v1.0和当前tick")
    print_info("   - 闪烁的光标效果增加复古感")
    print_info("")
    print_info("2. 📊  资源监控面板")
    print_info("   - 4种资源（氧气、水、能源、食物）")
    print_info("   - 复古进度条和字符进度指示")
    print_info("   - 资源危急时会变红闪烁")
    print_info("")
    print_info("3. 👥  船员名单")
    print_info("   - 5名船员的通缉令式卡片")
    print_info("   - 显示健康、精神状态、位置")
    print_info("   - 船员死亡时显示'TERMINATED'红色印章")
    print_info("")
    print_info("4. 📜  系统日志")
    print_info("   - 终端风格的滚动日志")
    print_info("   - 新日志高亮显示")
    print_info("   - 不同事件类型有不同颜色")
    print_info("")
    print_info("5. ⏳  时间旅行控制")
    print_info("   - 滑动条选择要回到的tick")
    print_info("   - 执行时间旅行按钮")
    print_info("   - 警告：时间旅行会创建新的时间线分支")
    print_info("")
    print_info("6. 🎮  控制按钮")
    print_info("   - '执行tick': 推进一个游戏时间单位")
    print_info("   - '系统重启': 重置整个模拟")
    print_info("   - '自动扫描': 开启/关闭自动刷新")
    time.sleep(3)
    
    # 第7部分：游戏策略
    print_header("第7部分：游戏策略提示")
    print_step("如何玩这个游戏？")
    print_info("这是一个观察型游戏，你不能直接控制船员，但可以：")
    print_info("")
    print_info("1. 🎯 观察模式")
    print_info("   - 观察5名船员的性格如何影响他们的决策")
    print_info("   - 指挥官倾向于战略性行动")
    print_info("   - 工程师优先处理技术问题")
    print_info("   - 医生关心船员健康")
    print_info("   - 生物学家专注于植物实验")
    print_info("   - 飞行员（间谍）可能进行破坏")
    print_info("")
    print_info("2. ⚖️  资源管理")
    print_info("   - 密切监控资源水平")
    print_info("   - 资源低于100时进入危急状态")
    print_info("   - 目标是让殖民地尽可能长久生存")
    print_info("")
    print_info("3. 🔄  时间旅行策略")
    print_info("   - 当殖民地发展不理想时，回到过去")
    print_info("   - 实验不同的时间线分支")
    print_info("   - 寻找最佳的发展路径")
    print_info("")
    print_info("4. 🎲  随机事件")
    print_info("   - 太阳能板故障、系统损坏等随机事件")
    print_info("   - 使用相同种子可以重现相同的事件序列")
    print_info("   - 尝试不同种子体验不同的故事")
    time.sleep(3)
    
    # 第8部分：高级功能
    print_header("第8部分：高级功能")
    print_step("LLM模式（人工智能决策）")
    print_info("游戏支持使用DeepSeek API让船员进行AI决策：")
    print_info("1. 需要有效的DeepSeek API密钥（已配置）")
    print_info("2. 在重置模拟时选择use_llm=true")
    print_info("3. 船员将使用AI模型进行更智能（但非确定性）的决策")
    print_info("4. AI决策会消耗API额度，但更真实有趣")
    
    print_step("确定性 vs 非确定性")
    print_info("两种游戏模式：")
    print_info("- 模拟模式（默认）：完全确定性，适合时间旅行实验")
    print_info("- LLM模式：使用AI决策，更真实但非确定性")
    print_info("提示：使用确定性模式进行时间旅行实验，使用LLM模式体验故事")
    time.sleep(2)
    
    print_header("演示结束")
    print_success("游戏演示完成！")
    print("")
    print("接下来你可以：")
    print("1. 🌐 打开浏览器访问 http://localhost:8000/static/index.html")
    print("2. 🎮 点击'执行tick'按钮推进游戏")
    print("3. 🔍 观察船员的行为和资源变化")
    print("4. ⏳ 尝试时间旅行功能")
    print("5. 🔄 使用不同种子开始新游戏")
    print("6. 🤖 实验LLM模式（需要API密钥）")
    print("")
    print("游戏服务器仍在运行。要停止服务器，在终端按Ctrl+C。")
    print("")

if __name__ == "__main__":
    try:
        demonstrate_gameplay()
    except KeyboardInterrupt:
        print("\n\n演示被中断。游戏服务器仍在运行。")
    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        print("请确保服务器正在运行：http://localhost:8000")