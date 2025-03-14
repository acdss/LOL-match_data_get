import json
import os

# 定义准则层
criteria = ["伤害", "强韧", "功能", "机动", "控制"]

# 定义协同效应类型
synergy_types = {
    "控制链": ["击飞", "眩晕", "减速", "恐惧", "魅惑", "定身", "凝滞", "沉默", "击退", "缚地", "禁锢","压制"],
    "伤害叠加": ["物理", "魔法", "真实伤害"],
    "功能互补": ["治疗", "护盾", "群体控制"],
    "机动性协同": ["突进", "位移"]
}

# 定义极地大乱斗特定因素
aram_factors = {
    "团战能力": ["范围伤害", "群体控制", "高爆发"],
    "地图适应性": ["狭窄地形", "视野控制"],
    "资源管理": ["低蓝耗", "法力回复"],
    "自保能力": ["免疫", "减伤", "位移","隐身","伪装","潜行"],
    "反制能力": ["沉默", "打断"]
}

# 定义英雄数据路径
base_path = r"C:\Users\Enderman\Downloads\dragontail-15.5.1\15.5.1\data\zh_CN\champion"



# 定义一个函数来获取英雄的平衡调整信息
def get_balance_adjustments(champion_name):
    # 根据英雄名称返回相应的平衡调整信息
    balance_adjustments = {
        "辛德拉": {"伤害": 1.05, "技能急速": 5},
        "薇恩": {"伤害": 1.05, "承受伤害": 0.95},
        "亚托克斯": {"伤害": 1.05},
        "雷恩加尔": {"伤害": 1.05,"承受伤害": 0.92, "技能急速": 5,"韧性": 20},
        "沃利贝尔": {"承受伤害": 1.1},
        "卡特琳娜": {"技能急速": 10,"韧性": 20},
        "菲兹": {"伤害": 1.05, "承受伤害": 0.95},
        "韦鲁斯": {"伤害": 0.98, "承受伤害": 1.05},
        "薇古丝": {"伤害": 0.95},
        "斯莫德": {"承受伤害": 1.02,"技能急速": -10},
        "艾翁": {"伤害": 0.95, "护盾效果": 0.8},
        "黑默丁格": {"伤害": 0.9, "承受伤害": 1.1},
        "艾瑞莉娅": {"技能急速": 20},
        "赵信": {"伤害": 0.95},
        "吉格斯": {"伤害": 0.87, "承受伤害": 1.2, "技能急速": -20},
        "艾尼维亚": {"伤害": 1.05},
        "丽桑卓": {"伤害": 0.95,"承受伤害": 1.05},
        "尼菈": {"伤害": 0.97},
        "古拉加斯": {"承受伤害": 0.95},
        "金克丝": {"伤害": 0.9, "承受伤害": 1.05},
        "纳亚菲利": {"伤害": 1.1,"技能急速": 10},
        "克烈": {"伤害": 1.05},
        "泰隆": {"承受伤害": 0.95, "韧性": 20},
        "盖伦": { "承受伤害": 0.95},
        "奎因": {"伤害": 1.1, "承受伤害": 0.9, "韧性": 20},
        "赛娜": {"伤害": 0.97},
        "莫甘娜": {"伤害": 0.95, "承受伤害": 1.1},
        "萨科": {"伤害": 1.05},
        "锐雯": {"伤害": 1.05, "承受伤害": 0.92},
        "迦娜": {"伤害": 0.95, "承受伤害": 1.05, "治疗效果": 0.9, "护盾效果": 0.95},
        "永恩": {"伤害": 1.05, "承受伤害": 0.97,"攻速收益":1.025},
        "瑞兹": {"伤害": 1.05, "承受伤害": 0.95},
        "布兰德": {"伤害": 0.9, "承受伤害": 1.05, "技能急速": -10},
        "卡莉斯塔": {"伤害": 1.1, "承受伤害": 0.9},
        "拉克丝": {"伤害": 0.85, "承受伤害": 1.1,"护盾效果": 0.8},
        "乐芙兰": {"伤害": 1.1, "承受伤害": 0.9, "技能急速": 20},
        "俄洛伊": {"伤害": 0.95, "承受伤害": 1.05, "治疗效果": 0.8},
        "莉莉娅": {"伤害": 0.95, "承受伤害": 1.05},
        "艾希": {"伤害": 1.05},
        "普朗克": {"伤害": 1.05},
        "安妮": {"伤害": 0.95, "承受伤害": 1.05,"护盾效果": 0.9},
        "塔姆": {"承受伤害": 1.05},
        "娜美": {"伤害": 0.95, "承受伤害": 1.05},
        "洛": {"承受伤害": 1.05},
        "雷克顿": {"治疗效果": 1.05},
        "锤石": {"承受伤害": 1.05},
        "维克托": {"伤害": 0.95, "承受伤害": 1.05},
        "塞拉斯": {"伤害": 1.05},
        "婕拉": {"伤害": 0.9, "承受伤害": 1.05, "技能急速": -10},
        "阿狸": {"伤害": 0.97, "治疗效果": 0.9},
        "特朗德尔": {"承受伤害": 1.05},
        "凯南": {"伤害": 1.05},
        "贝蕾亚": {"伤害": 1.05, "承受伤害": 0.9, "治疗效果": 1.05},
        "奈德丽": {"伤害": 1.1},
        "奥拉夫": {"伤害": 1.05},
        "阿卡丽": {"伤害": 1.05, "承受伤害": 0.9, "韧性": 20},
        "烈娜塔": {"伤害": 0.95, "承受伤害": 1.05,"护盾效果": 0.8},
        "辛吉德": {"伤害": 0.9, "承受伤害": 1.08},
        "格温": {"伤害": 1.05},
        "希瓦娜": {"承受伤害": 0.95},
        "崔丝塔娜": {"伤害": 1.05, "承受伤害": 0.95},
        "泰达米尔": {"伤害": 1.1,"承受伤害": 0.9,"治疗效果": 1.2},
        "李青": {"伤害": 1.05, "承受伤害": 0.95,"治疗效果": 1.1,"护盾效果": 1.2},
        "纳尔": {"伤害": 1.05, "承受伤害": 0.95,"攻速收益":1.025},
        "米利欧": {"治疗效果": 0.95,"护盾效果": 0.9, "技能急速": -10},
        "佐伊": {"伤害": 1.1, "承受伤害": 0.95},
        "悠米": {"伤害": 1.05},
        "慎": {"伤害": 1.05, "承受伤害": 0.95},
        "奎桑提": {"伤害": 1.05,"攻速收益":1.03},
        "霞": {"伤害": 1.05},
        "阿利斯塔": {"伤害": 0.95, "承受伤害": 1.05,"治疗效果": 0.8},
        "茂凯": {"伤害": 0.8, "承受伤害": 1.1,"治疗效果": 0.9},
        "斯维因": {"伤害": 0.95, "承受伤害": 1.15,"治疗效果": 0.8},
        "德莱厄斯": {"伤害": 1.05},
        "凯特琳": {"承受伤害": 1.05},
        "蔚": {"伤害": 1.05, "承受伤害": 0.95},
        "佛耶戈": {"伤害": 1.05},
        "卡蜜尔": {"伤害": 1.05, "承受伤害": 0.95,"护盾效果": 1.1, "技能急速": 10},
        "芮尔": {"伤害": 0.95,"治疗效果": 0.9,"护盾效果": 0.9},
        "德莱文": {"伤害": 1.05, "承受伤害": 0.95},
        "阿兹尔": { "承受伤害": 0.95,"技能急速": 20,"攻速收益":1.025},
        "莎弥拉": {"承受伤害": 1.05},
        "内瑟斯": {"伤害": 0.9, "承受伤害": 1.05},
        "奥恩": {"伤害": 0.9, "承受伤害": 1.05},
        "克格莫": {"伤害": 0.88, "承受伤害": 1.1},
        "斯卡纳": { "承受伤害": 1.05},
        "厄运小姐": {"伤害": 0.9, "承受伤害": 1.05},
        "诺提勒斯": {"伤害": 0.95, "承受伤害": 1.1},
        "扎克": {"承受伤害": 0.96, "治疗效果": 1.1},
        "卢锡安": {"伤害": 1.05, "承受伤害": 0.95, "技能急速": 10,"韧性": 20},
        "基兰": {"伤害": 1.05, "承受伤害": 0.95},
        "艾克": {"伤害": 1.1,"韧性": 20},
        "卡尔萨斯": {"伤害": 0.9, "承受伤害": 1.05},
        "乌迪尔": {"治疗效果": 0.9,"护盾效果": 0.9},
        "蕾欧娜": {"伤害": 0.95, "承受伤害": 1.05},
        "卡尔玛": {"伤害": 0.95},
        "莫德凯撒": {"伤害": 0.95, "承受伤害": 1.05},
        "安蓓萨": {"承受伤害": 1.05},
        "伊芙琳": {"伤害": 1.1, "承受伤害": 0.9,"韧性": 20},
        "塔里克": { "承受伤害": 1.1},
        "瑟提": {"承受伤害": 1.1},
        "赛恩": {"伤害": 0.9, "承受伤害": 1.1,"技能急速": -10},
        "杰斯": {"伤害": 1.05},
        "图奇": {"承受伤害": 0.95},
        "菲奥娜": {"承受伤害": 0.95},
        "贾克斯": {"伤害": 1.05, "承受伤害": 0.97},
        "厄加特": {"承受伤害": 1.05},
        "烬": {"伤害": 0.9, "承受伤害": 1.05},
        "维迦": {"伤害": 0.9, "承受伤害": 1.1},
        "弗拉基米尔": {"伤害": 0.95, "承受伤害": 1.05, "治疗效果":0.9},
        "巴德": {"伤害": 1.15, "承受伤害": 0.85,"治疗效果":1.2},
        "萨勒芬妮": {"伤害": 0.9, "承受伤害": 1.2, "治疗效果":0.8,"护盾效果": 0.8,"技能急速": -20},
        "雷克塞": {"伤害": 1.05, "承受伤害": 0.9},
        "科加斯": {"承受伤害": 1.1},
        "卡兹克": {"伤害": 1.1, "承受伤害": 0.9,"韧性": 20,"治疗效果":1.2},
        "卑尔维斯": {"伤害": 1.05},
        "玛尔扎哈": {"伤害": 0.9, "承受伤害": 1.1},
        "卡萨丁": { "承受伤害": 0.95},
        "卡莎": { "承受伤害": 0.9,"攻速收益":1.025},
        "维克兹": {"伤害": 0.95, "承受伤害": 1.05},
        "努努和威朗普": {"伤害": 1.1, "承受伤害": 0.9,"治疗效果":1.1,"韧性":20,"护盾效果": 1.2},
        "派克": {"伤害": 1.05, "承受伤害": 0.95,"韧性":20},
        "提莫": {"伤害": 0.95, "承受伤害": 1.1,"技能急速":-10},
        "彗": {"伤害": 0.95, "承受伤害": 1.05},
        "库奇": {"承受伤害": 0.9,"技能急速":-20},
        "凯隐": {"伤害": 0.95, "承受伤害": 0.9,"韧性":20,"治疗效果":0.8},
        "劫": {"伤害": 1.05, "承受伤害": 0.95,"韧性":20},
        "阿克尚": {"伤害": 1.05, "承受伤害": 0.95},
        "魔腾": {"伤害": 1.1, "承受伤害": 0.9,"治疗效果":1.2},
        "千珏": {"伤害": 1.1, "承受伤害": 0.9},
        "奇亚娜": {"伤害": 1.15, "承受伤害": 0.9,"韧性":20},
        "费德提克": {"伤害": 0.95, "承受伤害": 1.05},
        "泽拉斯": {"伤害": 0.93, "承受伤害": 1.05},
        "希维尔": {"伤害": 0.9, "承受伤害": 1.05},
        "赫卡里姆": {"伤害": 1.05, "承受伤害": 0.9,"技能急速":10,"治疗效果":1.2},
        "加里奥": {"伤害": 0.9, "承受伤害": 1.05},
        "凯尔": {"伤害": 0.95, "承受伤害": 1.1},
        "伊莉丝": {"伤害": 1.05, "承受伤害": 0.9,"韧性":10},
        "索拉卡": { "承受伤害": 0.97,"治疗效果":1.15},
        "泽丽": {"伤害": 1.1, "承受伤害": 0.95},
        "蒙多医生": {"伤害": 0.9, "承受伤害": 1.05},
        "沃里克": {"伤害": 1.05, "承受伤害": 0.95,"治疗效果":1.2}
    }
    return balance_adjustments.get(champion_name, {})


# 定义一个函数来提取英雄数据
def extract_champion_data(champion_file):
    with open(champion_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    champion_name = data["data"][list(data["data"].keys())[0]]["title"]
    stats = data["data"][list(data["data"].keys())[0]]["stats"]
    spells = data["data"][list(data["data"].keys())[0]]["spells"]

    # 提取基础属性
    hp = stats["hp"]
    hpperlevel = stats["hpperlevel"]
    mp = stats["mp"]
    mpperlevel = stats["mpperlevel"]
    movespeed = stats["movespeed"]
    armor = stats["armor"]
    armorperlevel = stats["armorperlevel"]
    spellblock = stats["spellblock"]
    spellblockperlevel = stats["spellblockperlevel"]
    attackdamage = stats["attackdamage"]
    attackdamageperlevel = stats["attackdamageperlevel"]
    attackspeed = stats["attackspeed"]
    attackspeedperlevel = stats["attackspeedperlevel"]

    # 初始化准则层得分
    base_damage =(attackdamage + attackdamageperlevel * 18)*(attackspeed+attackspeedperlevel*18)
    base_armor = armor + armorperlevel * 18
    base_spellblock = spellblock + spellblockperlevel * 18
    base_hp = hp + hpperlevel * 18
    伤害 = base_damage
    强韧 = (base_armor + base_spellblock+base_hp ) / 2
    功能 = (mp + mpperlevel * 18) / 2
    机动 = movespeed
    控制 = 0

    # 初始化协同效应得分
    synergy_scores = {
        "控制链": 0,
        "伤害叠加": 0,
        "功能互补": 0,
        "机动性协同": 0
    }

    # 初始化极地大乱斗特定因素得分
    aram_factor_scores = {
        "团战能力": 0,
        "地图适应性": 0,
        "资源管理": 0,
        "自保能力": 0,
        "反制能力": 0
    }

    # 解析技能描述
    for spell in spells:
        description = spell["description"].lower()
        tooltip = spell.get("tooltip", "").lower()
        vars_data = spell.get("vars", [])

        # 合并 description 和 tooltip
        full_description = description + " " + tooltip

        # 伤害相关
        # 攻速加成
        if "攻速" in full_description or "攻击速度" in full_description:
            伤害 += 0.1 * base_damage  # 假设攻速提升10%伤害
        # 最大生命值伤害
        if "最大生命值" in full_description and "伤害" in full_description:
            伤害 += 0.05 * base_hp  # 假设基于最大生命值的伤害加成
        # 真实伤害
        if "真实伤害" in full_description:
            伤害 += 0.2 * base_damage  # 假设真实伤害提升20%伤害

        # 强韧相关
        # 最大生命值护盾
        if "最大生命值" in full_description and "护盾" in full_description:
            强韧 += 0.05 * base_hp  # 假设基于最大生命值的护盾加成
        # 回复血量
        if "回复" in full_description or "治疗" in full_description or "全能吸血":
            强韧 += 0.1 * base_damage  # 假设回复能力提升10%强韧

        # 功能相关
        if "治疗" in full_description or "护盾" in full_description or "回复" in full_description:
            功能 += 1

        # 机动相关
        if "移速" in full_description or "传送" in full_description or "突进" in full_description:
            机动 += 1

        # 控制相关
        control_keywords = ["眩晕", "恐惧", "击飞", "魅惑", "定身", "凝滞", "沉默", "击退", "减速", "缚地", "禁锢","压制"]
        for keyword in control_keywords:
            if keyword in full_description:
                控制 += 1
                break

        # 提取技能标签
        # 控制类型
        for control_type in synergy_types["控制链"]:
            if control_type in full_description:
                synergy_scores["控制链"] += 1
                break
        # 伤害类型
        for damage_type in synergy_types["伤害叠加"]:
            if damage_type in full_description:
                synergy_scores["伤害叠加"] += 1
                break
        # 功能类型
        for function_type in synergy_types["功能互补"]:
            if function_type in full_description:
                synergy_scores["功能互补"] += 1
                break
        # 机动性类型
        for mobility_type in synergy_types["机动性协同"]:
            if mobility_type in full_description:
                synergy_scores["机动性协同"] += 1
                break

        # 极地大乱斗特定因素
        # 团战能力
        for factor in aram_factors["团战能力"]:
            if factor in full_description:
                aram_factor_scores["团战能力"] += 1
                break
        # 地图适应性
        for factor in aram_factors["地图适应性"]:
            if factor in full_description:
                aram_factor_scores["地图适应性"] += 1
                break
        # 资源管理
        for factor in aram_factors["资源管理"]:
            if factor in full_description:
                aram_factor_scores["资源管理"] += 1
                break
        # 自保能力
        for factor in aram_factors["自保能力"]:
            if factor in full_description:
                aram_factor_scores["自保能力"] += 1
                break
        # 反制能力
        for factor in aram_factors["反制能力"]:
            if factor in full_description:
                aram_factor_scores["反制能力"] += 1
                break

    # 计算协同效应得分
    control_synergy = synergy_scores["控制链"] * 0.2
    damage_synergy = synergy_scores["伤害叠加"] * 0.2
    function_synergy = synergy_scores["功能互补"] * 0.2
    mobility_synergy = synergy_scores["机动性协同"] * 0.2

    # 计算极地大乱斗特定因素得分
    aram_factor_scores["团战能力"] *= 0.3
    aram_factor_scores["地图适应性"] *= 0.2
    aram_factor_scores["资源管理"] *= 0.15
    aram_factor_scores["自保能力"] *= 0.15
    aram_factor_scores["反制能力"] *= 0.1


    # 获取英雄的平衡调整信息
    balance_adjustment = get_balance_adjustments(champion_name)

    # 应用协同效应得分和极地大乱斗特定因素得分
    伤害 += damage_synergy + aram_factor_scores["团战能力"]
    强韧 += control_synergy + aram_factor_scores["自保能力"]
    功能 += function_synergy + aram_factor_scores["资源管理"]
    机动 += mobility_synergy + aram_factor_scores["地图适应性"]
    控制 += control_synergy + aram_factor_scores["反制能力"]

    # 应用平衡调整
    if "伤害" in balance_adjustment:
        伤害 *= balance_adjustment["伤害"]
    if "技能急速" in balance_adjustment:
        # 技能急速可以提升伤害和功能得分
        伤害 += balance_adjustment["技能急速"] * 0.1
        功能 += balance_adjustment["技能急速"] * 0.05
    if "韧性" in balance_adjustment:
        # 韧性提升强韧得分
        强韧 += balance_adjustment["韧性"] * 0.1
    if "治疗效果" in balance_adjustment:
        # 治疗效果提升强韧和功能得分
        强韧 += balance_adjustment["治疗效果"] * 0.1
        功能 += balance_adjustment["治疗效果"] * 0.1
    if "护盾效果" in balance_adjustment:
        # 护盾效果提升强韧得分
        强韧 += balance_adjustment["护盾效果"] * 0.1
    if "攻速收益" in balance_adjustment:
        # 攻速收益提升伤害和机动得分
        伤害 += balance_adjustment["攻速收益"] * 0.1
        机动 += balance_adjustment["攻速收益"] * 0.05
    if "承受伤害" in balance_adjustment:
        # 承受伤害调整强韧得分
        强韧 /= balance_adjustment["承受伤害"]


    return {
        "name": champion_name,
        "伤害": 伤害,
        "强韧": 强韧,
        "功能": 功能,
        "机动": 机动,
        "控制": 控制
    }


# 提取所有英雄数据
champion_data = []
for file_name in os.listdir(base_path):
    if file_name.endswith(".json"):
        file_path = os.path.join(base_path, file_name)
        champion_data.append(extract_champion_data(file_path))

# 计算每个准则层的最大值和最小值
max_values = {criterion: max(hero[criterion] for hero in champion_data) for criterion in criteria}
min_values = {criterion: min(hero[criterion] for hero in champion_data) for criterion in criteria}

# 归一化处理
for hero in champion_data:
    for criterion in criteria:
        max_val = max_values[criterion]
        min_val = min_values[criterion]
        if max_val != min_val:
            hero[criterion] = (hero[criterion] - min_val) / (max_val - min_val)
        else:
            hero[criterion] = 0.5  # 如果最大值和最小值相同，所有值设为0.5

# 打印归一化后的数据
for hero in champion_data:
    print(hero)