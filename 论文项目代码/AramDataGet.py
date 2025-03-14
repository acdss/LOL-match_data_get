import logging
import threading
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from tenacity import retry, stop_after_attempt, wait_fixed
import requests
import time
from sqlalchemy import create_engine
from sqlalchemy import text


# 设置日志级别为 ERROR
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 每秒最大请求数
REQUESTS_PER_SECOND = 20
# 每分钟最大请求数
REQUESTS_PER_2_MINUTES = 100

# 记录请求时间戳（按地区区分）
request_timestamps = {}

# 已处理的puuid集合（按地区区分）
processed_puuids = {}

# 线程锁
lock = threading.Lock()


# 针对API限速或网络波动，添加重试逻辑
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def safe_api_call(url, region):
    with lock:
        current_time = time.time()
        request_timestamps.setdefault(region, [])
        request_timestamps[region] = [t for t in request_timestamps[region] if current_time - t <= 120]

        # 检查是否超过每秒请求数限制
        if len(request_timestamps[region]) >= REQUESTS_PER_SECOND:
            wait_time = current_time - request_timestamps[region][-REQUESTS_PER_SECOND] + (1 / REQUESTS_PER_SECOND)
            time.sleep(wait_time)

        # 检查是否超过每2分钟请求数限制
        if len(request_timestamps[region]) >= REQUESTS_PER_2_MINUTES:
            wait_time = current_time - request_timestamps[region][0] + (
                    current_time - request_timestamps[region][0]) / (
                                REQUESTS_PER_2_MINUTES - len(request_timestamps[region]))
            time.sleep(wait_time)

        # 记录当前请求时间
        request_timestamps[region].append(current_time)

    response = requests.get(url, params={'api_key': API_KEY})
    response.raise_for_status()
    return response.json()



# 创建 SQLAlchemy 引擎
engine = create_engine(
    "mysql+pymysql://root:Aa637525@localhost/lol_aram",
    pool_size=50,  # 连接池大小
    max_overflow=10,  # 允许额外创建的连接数
    pool_timeout=10,  # 连接超时时间
    pool_recycle=3600,  # 连接回收时间
    echo=False  # 是否打印SQL语句
)


# API密钥
API_KEY = "RGAPI-a345540d-fbc1-40a3-9d52-f66ebb38369f"


# 创建会话工厂
Session = sessionmaker(bind=engine)

# 自定义异常类
class DatabaseConnectionError(Exception):
    pass

def get_db_session():
    try:
        session = Session()
        return session
    except SQLAlchemyError as e:
        logging.error(f"数据库连接失败: {e}")
        raise DatabaseConnectionError("无法获取数据库会话") from e

#
#
# 插入对局数据
def insert_match_data(match_info, region):
    session = get_db_session()
    try:
        # 提取platformId和gameId
        platform_id = match_info["platformId"]
        game_id = match_info["gameId"]
        # 组合matchId
        match_id = f"{platform_id}_{game_id}"
        # 插入对局基本信息
        session.execute(text('''
                INSERT INTO matches (match_id, game_version, game_duration, queue_id, game_start)
                VALUES (:match_id, :game_version, :game_duration, :queue_id, :game_start)
                ON DUPLICATE KEY UPDATE match_id = match_id
            '''), {
            'match_id': match_id,
            'game_version': match_info["gameVersion"],
            'game_duration': match_info["gameDuration"],
            'queue_id': 450,
            'game_start': match_info["gameStartTimestamp"]
        })

        # 批量插入玩家数据
        participants_batch = []
        if "participants" in match_info:
            for participant in match_info["participants"]:
                if "riotIdGameName" in participant and "riotIdTagline" in participant and "championId" in participant and "win" in participant and "kills" in participant and "deaths" in participant and "assists" in participant:
                    summoner_name = f"{participant['riotIdGameName']}#{participant['riotIdTagline']}"
                    participants_batch.append({
                        'match_id': match_id,
                        'summoner_name': summoner_name.replace("'", "\\'"),  # 转义特殊字符
                        'champion_id': participant["championId"],
                        'win': 1 if participant["win"] else 0,
                        'kills': participant["kills"],
                        'deaths': participant["deaths"],
                        'assists': participant["assists"]
                    })
                else:
                    print(f"玩家数据不完整，跳过")
        else:
            print(f"对局数据中没有参与者信息，跳过")

        if participants_batch:
            session.execute(text('''
                    INSERT INTO participants
                    (match_id, summoner_name, champion_id, win, kills, deaths, assists)
                    VALUES (:match_id, :summoner_name, :champion_id, :win, :kills, :deaths, :assists)
                '''), participants_batch)

        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        # 截取错误信息的第一行并记录
        error_message = str(e).split('\n')[0]
        logger.error(f"插入数据失败: {error_message}")
    finally:
        session.close()


# 保存当前正在处理的puuid到数据库
def save_current_puuid(region, puuid):
    session = get_db_session()
    try:
        # 使用字典作为参数
        session.execute(text('''
               INSERT INTO current_puuid (region, puuid)
               VALUES (:region, :puuid)
               ON DUPLICATE KEY UPDATE puuid = :puuid
           '''), {'region': region, 'puuid': puuid})
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"保存当前puuid失败: {e}")
    finally:
        session.close()


# 从数据库中读取上次处理的puuid
def get_last_processed_puuid():
    conn = get_db_session()
    try:
        result = conn.execute(text('''
             SELECT region, puuid FROM current_puuid
         ''')).fetchall()
        return {region: puuid for region, puuid in result}
    except SQLAlchemyError as e:
        logging.error(f"读取上次处理的puuid失败: {e}")
    finally:
        conn.close()
    return {}


# 获取并保存对局数据
def fetch_and_save_aram_matches(puuid, region):
    # 初始化该地区已处理集合
    with lock:
        processed_puuids.setdefault(region, set())

    # 如果puuid已经处理过，直接返回
    if puuid in processed_puuids[region]:
        return

    # 标记当前puuid为已处理
    processed_puuids[region].add(puuid)

    # 保存当前正在处理的puuid到数据库
    save_current_puuid(region, puuid)

    matches_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=450&count=100"
    match_ids = safe_api_call(matches_url, region)

    if not match_ids:
        print(f"未获取到对局ID,地区: {region}, puuid: {puuid}")
        return
    for match_id in match_ids:
        print(f"正在处理对局: {match_id}, 地区: {region}")
        match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        match_data = safe_api_call(match_url, region)
        if match_data and "info" in match_data:
            match_info = match_data["info"]
            insert_match_data(match_info, region)

            # 递归调用时需要控制速率
            if "metadata" in match_data and "participants" in match_data["metadata"]:
                for participant in match_data["metadata"]["participants"]:
                    threading.Thread(target=fetch_and_save_aram_matches, args=(participant, region)).start()
        else:
            print(f"对局 {match_id} 数据不完整，跳过")

    # 主程序

    # 获取上次处理的puuid


last_processed_puuids = get_last_processed_puuid()

# 如果有上次处理的puuid，从这些puuid继续处理
if last_processed_puuids:
    print("从上次的位置继续处理")
    for region, puuid in last_processed_puuids.items():
        threading.Thread(target=fetch_and_save_aram_matches, args=(puuid, region)).start()
else:
    # 如果没有上次的记录，从初始puuid开始处理
    regions = ["asia", "europe", "americas"]

    # 从公开数据的玩家抓取数据
    player_puuids = {
        "asia": "vWAwhZE6NsJQ6rNsBoEMClem0dO_E7jCJAj-StJ6miBlmNnm75pNdGKwplDuCl6oBH7BCplwyyN4Ig",
        "europe": "62BpE8hkagUMaeg7gLzzvUVdrLLqFhujSwQf-BKRnObjRolTE4F4dQm6SCP-iS9Vu3BYglVnZWiyGg",
        "americas": "MdfsBXkaB9TboYmxSKqo6cBlZdtMoTXHr_Mnvh79ECve53JRXjPRrv4POzF7mchRxJU9X1hOLNCgSg"
    }
    # 为每个地区的puuid启动一个线程
    for region, puuid in player_puuids.items():
        threading.Thread(target=fetch_and_save_aram_matches, args=(puuid, region)).start()

