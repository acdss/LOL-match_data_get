# import threading
# from mysql.connector import pooling
# from tenacity import retry, stop_after_attempt, wait_fixed
# import requests
# import time
#
# # 每秒最大请求数
# REQUESTS_PER_SECOND = 20
# # 每分钟最大请求数
# REQUESTS_PER_2_MINUTES = 100
#
# # 记录请求时间戳（按地区区分）
# request_timestamps = {}
#
# # 已处理的puuid集合（按地区区分）
# processed_puuids = {}
#
# # 线程锁
# lock = threading.Lock()
#
# # 针对API限速或网络波动，添加重试逻辑
# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
# def safe_api_call(url, region):
#     with lock:
#         current_time = time.time()
#         request_timestamps.setdefault(region, [])
#         request_timestamps[region] = [t for t in request_timestamps[region] if current_time - t <= 120]
#
#         # 检查是否超过每秒请求数限制
#         if len(request_timestamps[region]) >= REQUESTS_PER_SECOND:
#             wait_time = current_time - request_timestamps[region][-REQUESTS_PER_SECOND] + (1 / REQUESTS_PER_SECOND)
#             time.sleep(wait_time)
#
#         # 检查是否超过每2分钟请求数限制
#         if len(request_timestamps[region]) >= REQUESTS_PER_2_MINUTES:
#             wait_time = current_time - request_timestamps[region][0] + (
#                     current_time - request_timestamps[region][0]) / (
#                                 REQUESTS_PER_2_MINUTES - len(request_timestamps[region]))
#             time.sleep(wait_time)
#
#         # 记录当前请求时间
#         request_timestamps[region].append(current_time)
#
#     try:
#         response = requests.get(url, params={'api_key': API_KEY})
#         response.raise_for_status()  # 如果状态码不是 200，会抛出 HTTPError
#         return response.json()
#     except requests.exceptions.HTTPError as e:
#         print(f"HTTP 请求失败: {e}")
#         print(f"URL: {url}")
#         print(f"状态码: {e.response.status_code}")
#         print(f"响应内容: {e.response.text}")
#         raise
#
#
# # MySQL连接配置
# config = {
#     "user": "root",
#     "password": "Aa637525",
#     "host": "localhost",
#     "database": "lol_aram",
#     "raise_on_warnings": True
# }
#
# # 创建数据库连接池
# pool = pooling.MySQLConnectionPool(pool_name="aram_pool", pool_size=10, **config)
#
# # API密钥
# API_KEY = "RGAPI-52f3f4c0-13c7-4f75-98a5-74e4e20e646b"
#
# def get_db_connection():
#     try:
#         return pool.get_connection()
#     except Exception as e:
#         print(f"数据库连接失败: {e}")
#         return None
#
# # 批量插入对局数据
# def batch_insert_match_data(matches, region):
#     conn = get_db_connection()
#     if conn is None:
#         return
#
#     cursor = conn.cursor()
#
#     try:
#         # 批量插入对局基本信息
#         match_data_batch = []
#         for match in matches:
#             match_info = match["info"]
#             platform_id = match_info["platformId"]
#             game_id = match_info["gameId"]
#             match_id = f"{platform_id}_{game_id}"
#
#             match_data = (
#                 match_id,
#                 match_info["gameVersion"],
#                 match_info["gameDuration"],
#                 450,  # 大乱斗queue_id固定为450
#                 match_info["gameStartTimestamp"]
#             )
#             match_data_batch.append(match_data)
#
#         if match_data_batch:
#             cursor.executemany('''
#                 INSERT INTO matches (match_id, game_version, game_duration, queue_id, game_start)
#                 VALUES (%s, %s, %s, %s, %s)
#                 ON DUPLICATE KEY UPDATE match_id = match_id
#             ''', match_data_batch)
#
#         # 批量插入玩家数据
#         participant_data_batch = []
#         for match in matches:
#             match_info = match["info"]
#             platform_id = match_info["platformId"]
#             game_id = match_info["gameId"]
#             match_id = f"{platform_id}_{game_id}"
#
#             if "participants" in match_info:
#                 for participant in match_info["participants"]:
#                     if "riotIdGameName" in participant and "riotIdTagline" in participant and "championId" in participant and "win" in participant and "kills" in participant and "deaths" in participant and "assists" in participant:
#                         summoner_name = f"{participant['riotIdGameName']}#{participant['riotIdTagline']}"
#                         participant_data = (
#                             match_id,
#                             summoner_name.replace("'", "\\'"),  # 转义特殊字符
#                             participant["championId"],
#                             1 if participant["win"] else 0,
#                             participant["kills"],
#                             participant["deaths"],
#                             participant["assists"]
#                         )
#                         participant_data_batch.append(participant_data)
#                     else:
#                         print(f"玩家数据不完整，跳过")
#
#         if participant_data_batch:
#             cursor.executemany('''
#                 INSERT INTO participants
#                 (match_id, summoner_name, champion_id, win, kills, deaths, assists)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#             ''', participant_data_batch)
#
#         conn.commit()
#     except Exception as e:
#         print(f"插入数据失败: {e}")
#         conn.rollback()
#     finally:
#         cursor.close()
#         conn.close()
#
# # 修复异常对局
# def fix_inconsistent_matches():
#     conn = get_db_connection()
#     if conn is None:
#         return
#
#     cursor = conn.cursor()
#
#     try:
#         # 找出胜者和败者数量不一致的对局
#         cursor.execute('''
#             SELECT match_id, COUNT(*) AS total_participants, SUM(win) AS total_win, COUNT(*) - SUM(win) AS total_lose
#             FROM participants
#             GROUP BY match_id
#             HAVING total_win != 5 OR total_lose != 5
#         ''')
#         inconsistent_matches = cursor.fetchall()
#
#         # 删除异常对局数据
#         for match_id, total_participants, total_win, total_lose in inconsistent_matches:
#             print(f"修复对局 {match_id}，胜者数量: {total_win}，败者数量: {total_lose}")
#
#             # 删除参与者数据
#             cursor.execute("DELETE FROM participants WHERE match_id = %s", (match_id,))
#             # 删除对局数据
#             cursor.execute("DELETE FROM matches WHERE match_id = %s", (match_id,))
#             conn.commit()
#
#             # 重新获取并插入数据
#             platform_id, game_id = match_id.split("_")
#             match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{platform_id}_{game_id}"
#             match_data = safe_api_call(match_url, region)
#             if match_data and "info" in match_data:
#                 batch_insert_match_data([match_data], region)
#             else:
#                 print(f"对局 {match_id} 数据不完整，跳过")
#
#     except Exception as e:
#         print(f"修复不一致的对局失败: {e}")
#         conn.rollback()
#     finally:
#         cursor.close()
#         conn.close()
#
# # 主程序
# if __name__ == "__main__":
#     regions = ["asia", "europe", "americas"]
#     for region in regions:
#         fix_inconsistent_matches()