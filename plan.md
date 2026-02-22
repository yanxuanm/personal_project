# Project Red Dust - 开发计划

> 最后更新: 2026-02-22

## 进度总览

- [ ] Agent 能力差异
- [ ] 隐藏目标系统
- [ ] 资源危机事件
- [ ] 随机事件库
- [ ] 天气系统
- [ ] 经验值/升级系统
- [ ] 装备系统
- [ ] 科技树
- [ ] 关系系统
- [ ] 秘密联盟
- [ ] 叛变/选举系统
- [ ] 日常挑战
- [ ] 成就系统
- [ ] 多结局

---

## 1. Agent 能力差异 (Agent Specialization)

**描述**: 每个 agent 有独特技能，影响行动效率和结果

**子任务**:
- [x] 1.1 在 schema 中添加 agent specialization 字段
- [x] 1.2 定义技能类型: ENGINEER, SCIENTIST, EXPLORER, MEDIC, PILOT, COMMANDER
- [x] 1.3 不同技能影响资源获取/维修/探索效率
- [x] 1.4 UI 显示 agent 特长图标

**状态**: ✅ 完成

---

## 2. 隐藏目标系统 (Secret Objectives)

**描述**: 每个 agent 有只有自己知道的目标

**子任务**:
- [x] 2.1 添加 SecretObjective 模型
- [x] 2.2 目标类型: BETRAY_LOVER, STEAL_RESOURCES, SABOTAGE, BECOME_LEADER, SURVIVE_SILENTLY, PROTECT_SOMEONE
- [x] 2.3 目标完成条件检测
- [x] 2.4 完成/失败时触发事件

**状态**: ✅ 完成

---

## 3. 资源危机事件 (Resource Crisis)

**描述**: 随机触发的资源枯竭事件，需要玩家做决策

**子任务**:
- [ ] 3.1 定义危机类型: OXYGEN_CRISIS, WATER_CRISIS, ENERGY_CRISIS, FOOD_CRISIS
- [ ] 3.2 危机触发条件 (资源 < 阈值)
- [ ] 3.3 决策选项 (牺牲/救援/冒险)
- [ ] 3.4 后果计算

---

## 4. 随机事件库 (Random Events)

**描述**: 丰富的随机事件系统

**子任务**:
- [ ] 4.1 创建事件定义文件
- [ ] 4.2 事件类型: METEOR, ALIEN_DISCOVERY, EQUIPMENT_FAILURE, SUPPLY_DROP, SOLAR_STORM, DUST_STORM, DISEASE_OUTBREAK
- [ ] 4.3 事件概率配置
- [ ] 4.4 事件持续时间效果

---

## 5. 天气系统 (Weather System)

**描述**: 火星天气影响游戏

**子任务**:
- [ ] 5.1 天气类型: CLEAR, DUST_STORM, SOLAR_STORM, COLD_WAVE
- [ ] 5.2 天气对资源的影响 (沙尘暴 -太阳能, 太阳风暴 -通信)
- [ ] 5.3 天气预测/预警
- [ ] 5.4 UI 显示天气

---

## 6. 经验值/升级系统 (XP & Leveling)

**描述**: Agent 通过行动获得经验值和升级

**子任务**:
- [ ] 6.1 添加 XP 和等级字段
- [ ] 6.2 XP 获得规则 (完成任务/发现资源/救援)
- [ ] 6.3 升级属性奖励
- [ ] 6.4 UI 显示等级

---

## 7. 装备系统 (Equipment)

**描述**: 发现和升级设备

**子任务**:
- [ ] 7.1 设备类型: SOLAR_PANEL, OXYGEN_GENERATOR, WATER_PURIFIER, HABITAT, ROVER
- [ ] 7.2 设备等级 (T1-T5)
- [ ] 7.3 设备获得事件
- [ ] 7.4 设备效果计算

---

## 8. 科技树 (Tech Tree)

**描述**: 解锁新技术

**子任务**:
- [ ] 8.1 科技定义: ADVANCED_SOLAR, AI_AUTOMATION, HYDROPONICS, WATER_RECYCLING, MEDICAL_BAY
- [ ] 8.2 解锁条件
- [ ] 8.3 科技效果
- [ ] 8.4 UI 科技树展示

---

## 9. 关系系统 (Relationship System)

**描述**: Agent 之间的关系影响合作

**子任务**:
- [ ] 9.1 关系值 (-100 到 +100)
- [ ] 9.2 关系变化规则
- [ ] 9.3 关系影响行动 (喜欢 → 帮忙, 讨厌 → 阻挠)
- [ ] 9.4 UI 关系显示

---

## 10. 秘密联盟 (Secret Alliance)

**描述**: 两个 agent 私下结盟

**子任务**:
- [ ] 10.1 联盟建立条件
- [ ] 10.2 联盟效果 (资源共享, 互相保护)
- [ ] 10.3 联盟被发现的可能性
- [ ] 10.4 联盟背叛后果

---

## 11. 叛变/选举系统 (Mutiny/Voting)

**描述**: 团队领导力危机

**子任务**:
- [ ] 11.1 叛变触发条件 (低士气 + 低资源)
- [ ] 11.2 投票系统 (选新指挥官)
- [ ] 11.3 叛变后果 (资源损失, 人员伤亡)
- [ ] 11.4 领导者能力

---

## 12. 日常挑战 (Daily Challenges)

**描述**: 每日目标系统

**子任务**:
- [ ] 12.1 挑战类型: SURVIVE_X_DAYS, FIND_X_RESOURCES, COMPLETE_X_MISSIONS
- [ ] 12.2 随机生成每日挑战
- [ ] 12.3 奖励计算
- [ ] 12.4 UI 挑战显示

---

## 13. 成就系统 (Achievements)

**描述**: 解锁成就徽章

**子任务**:
- [ ] 13.1 成就定义: FIRST_COLONY, SURVIVOR, EXPLORER, SCIENTIST, LEADER, etc.
- [ ] 13.2 成就检测
- [ ] 13.3 成就奖励
- [ ] 13.4 UI 成就展示

---

## 14. 多结局 (Multiple Endings)

**描述**: 不同结局

**子任务**:
- [ ] 14.1 结局类型: COLONY_SUCCESSFUL, ALL_DEAD, EVACUATED, MUTINY, ALIEN_ALLY, ISOLATED
- [ ] 14.2 结局触发条件
- [ ] 14.3 结局结算画面
- [ ] 14.4 评分系统

---

## 开发流程

1. 每个功能用 OpenCode 实现
2. 本地 pytest 测试
3. MCP E2E 测试 (Chrome DevTools)
4. Push 到 GitHub，检查 CI
5. 更新 plan.md，标记完成的任务
