import logging
from sqlalchemy import create_engine, text

# 设置日志级别为 ERROR
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 创建 SQLAlchemy 引擎
engine = create_engine(
    "mysql+pymysql://root:Aa637525@localhost/lol_aram",
    pool_size=50,  # 连接池大小
    max_overflow=10,  # 允许额外创建的连接数
    pool_timeout=10,  # 连接超时时间
    pool_recycle=3600,  # 连接回收时间
    echo=False  # 是否打印SQL语句
)

def calculate_and_store_win_rate():
    try:
        with engine.connect() as conn:
            # 计算胜率
            query = text("""
                SELECT 
                    champion_id,
                    COUNT(*) AS total_matches,
                    SUM(win) AS wins,
                    (SUM(win) / COUNT(*)) AS win_rate
                FROM 
                    participants
                GROUP BY 
                    champion_id
            """)
            result = conn.execute(query).fetchall()

            # 插入到新表
            insert_query = text("""
                INSERT INTO champion_win_rates (champion_id, total_matches, wins, win_rate)
                VALUES (:champion_id, :total_matches, :wins, :win_rate)
                ON DUPLICATE KEY UPDATE
                    total_matches = :total_matches,
                    wins = :wins,
                    win_rate = :win_rate
            """)

            for row in result:
                champion_id, total_matches, wins, win_rate = row
                conn.execute(insert_query, {
                    'champion_id': champion_id,
                    'total_matches': total_matches,
                    'wins': wins,
                    'win_rate': win_rate
                })

            conn.commit()
    except Exception as e:
        logger.error(f"计算并存储胜率失败: {e}")

if __name__ == "__main__":
    calculate_and_store_win_rate()
    print("胜率数据已成功存储到 champion_win_rates 表中")