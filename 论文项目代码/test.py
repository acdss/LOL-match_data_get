import time

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from AramDataGet import safe_api_call, insert_match_data
from collections import deque



# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
# def get_player_puuid_by_riot_id(game_name, tag_line, region="asia"):
#     api_key = "RGAPI-64139b5d-2973-49b4-9ce0-f146fe5e4169"
#     url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={api_key}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         account_info = response.json()
#         return account_info.get("puuid")
#     except requests.exceptions.HTTPError as e:
#         print(f"HTTP 错误: {e}")
#         return None
#     except requests.exceptions.RequestException as e:
#         print(f"请求错误: {e}")
#         return None
#
#
# # 获取玩家的 puuid
# game_name = "Heru"
# tag_line = "KR821"
# player_puuid = get_player_puuid_by_riot_id(game_name, tag_line)
#
# if player_puuid:
#     print(f"玩家 {game_name}#{tag_line} 的 puuid: {player_puuid}")
# else:
#     print(f"未能获取玩家 {game_name}#{tag_line} 的 puuid")
# from mysql.connector import pooling
#
# # 自定义配置字典（无需安装任何包）
# dbconfig = {
#     "user": "root",
#     "password": "Aa637525",
#     "host": "localhost",
#     "database": "lol_aram"
# }
#
# # 创建连接池（提升性能）
# connection_pool = pooling.MySQLConnectionPool(
#     pool_name="my_pool",
#     pool_size=5,  # 连接池大小
#     **dbconfig  # 展开字典参数
# )
#
# # 从连接池获取连接
# def get_connection():
#     return connection_pool.get_connection()
#
# # 使用示例
# try:
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM matches LIMIT 5")
#     results = cursor.fetchall()
#     print(results)
# except Exception as e:
#     print(f"数据库操作失败: {e}")
# finally:
#     if 'conn' in locals() and conn.is_connected():
#         cursor.close()
#         conn.close()
# 获取并保存对局数据
# 已处理的puuid集合
#
# match_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/KR_6758834036"
# match_data = safe_api_call(match_url, "asia")
# if match_data and "info" in match_data:
#   match_info = match_data["info"]
#   insert_match_data(match_info, "asia")