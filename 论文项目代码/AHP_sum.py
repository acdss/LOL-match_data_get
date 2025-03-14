import numpy as np


# 准则层
from ChampionDataGet import champion_data

criteria = ["伤害", "强韧", "功能", "机动", "控制"]

# 方案层
schemes = [hero['name'] for hero in champion_data]


# 两两比较结果（使用字典存储）
comparisons = {
    ("伤害", "强韧"): 3,
    ("伤害", "功能"): 4,
    ("伤害", "机动"): 2,
    ("伤害", "控制"): 4,
    ("强韧", "功能"): 1/3,
    ("强韧", "机动"): 1/3,
    ("强韧", "控制"): 1/4,
    ("功能", "机动"): 3,
    ("功能", "控制"): 2,
    ("机动", "控制"): 1/2
}

# 构造判断矩阵
def create_judgment_matrix(criteria, comparisons):
    n = len(criteria)
    matrix = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                # 获取准则名称
                criterion_i = criteria[i]
                criterion_j = criteria[j]
                # 查找比较结果
                if (criterion_i, criterion_j) in comparisons:
                    matrix[i][j] = comparisons[(criterion_i, criterion_j)]
                elif (criterion_j, criterion_i) in comparisons:
                    matrix[i][j] = 1 / comparisons[(criterion_j, criterion_i)]
    return matrix

# 计算权重
def calculate_weights(matrix):
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_eigenvalue_index = np.argmax(eigenvalues)
    max_eigenvector = eigenvectors[:, max_eigenvalue_index]
    weights = max_eigenvector / np.sum(max_eigenvector)
    return weights.real

# 一致性检验
def consistency_check(matrix, weights):
    n = matrix.shape[0]
    CI = (np.dot(matrix, weights) - n * weights) / (n - 1)
    RI = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]  # 随机一致性指标
    CR = np.max(CI) / RI[n-1]
    return CR

# 构造判断矩阵
judgment_matrix = create_judgment_matrix(criteria,comparisons)

# 计算准则层权重
criteria_weights = calculate_weights(judgment_matrix)

# 一致性检验
CR = consistency_check(judgment_matrix, criteria_weights)
print(f"一致性比率 (CR): {CR}")
if CR < 0.1:
    print("判断矩阵的一致性可以接受")
else:
    print("判断矩阵的一致性需要调整")

# 计算方案层综合得分
for hero in champion_data:
    total_score = 0
    for criterion in criteria:
        total_score += hero[criterion] * criteria_weights[criteria.index(criterion)]
    hero["综合得分"] = total_score

# 打印综合得分
for hero in champion_data:
    print(f"英雄: {hero['name']}, 综合得分: {hero['综合得分']:.4f}")

# 对英雄按综合得分进行排序
sorted_heroes = sorted(champion_data, key=lambda x: x["综合得分"], reverse=True)

# 输出综合分数前五的英雄
print("综合分数前五的英雄:")
for i in range(5):
    hero = sorted_heroes[i]
    print(f"排名 {i+1}: {hero['name']}, 综合得分: {hero['综合得分']:.4f}")