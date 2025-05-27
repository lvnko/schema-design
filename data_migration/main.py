import psycopg2, configparser, os
from pathlib import Path
from utils.TableMigrator import TableMigrator
from utils.RecycleLog import RecycleLogger
from itertools import chain
import numpy as np

dir_path = Path(__file__).parent.resolve()
recycle_logger = RecycleLogger(f"{dir_path}/logs/recycle.csv")

config = configparser.ConfigParser()
config.read(f"{dir_path}/db.ini")
db_tables_to_create = ["users", "topics", "posts", "comments", "votes"]

def get_sql(sql_statement_name):
    return open(f"{dir_path}/sql_statements/{sql_statement_name}.sql", "r").read()

def init_db():
    """
    Initialize all tables in the schema.
    """
    with psycopg2.connect(**config["postgres"]) as conn:
        with conn.cursor() as cursor:
            for table in db_tables_to_create:
                sql = get_sql(table)
                cursor.execute(sql)
        print("All tables are created if not exists.")


def migrate_users():
    """
    Migrate all users from old tables to users tables.
    """
    tables_to_extract_users = ['bad_posts', 'bad_comments']
    INSERT_INTO_USERS = get_sql('insert_into_users')

    limit = 10000

    for i in range(10):
        offset = i * limit
        for table in tables_to_extract_users:
            select_sql = f"""
            SELECT username
            FROM {table}
            WHERE username IS NOT NULL
            LIMIT {limit}
            OFFSET {offset};
            """
            with psycopg2.connect(**config["postgres"]) as conn:
                with conn.cursor("myCursor") as cursor:
                    cursor.execute(select_sql)
                    with conn.cursor() as client_cursor:
                        for user in cursor:
                            client_cursor.execute(INSERT_INTO_USERS, user)
                            # print(f"Inserted user : {user[0]}")

            print(f"Users extracted (#{offset} to #{offset + limit}) from {table} are now successfully migrated!")

    print(f"All users collected from {tables_to_extract_users} are now successfully migrated!")


def migrate_users_from_votes():
    
    INSERT_INTO_USERS = get_sql('insert_into_users')
    limit = 5000

    for i in range(20):
        offset = i * limit
        select_sql=f"""
        SELECT upvotes, downvotes
        FROM bad_posts
        LIMIT {limit}
        OFFSET {offset};
        """
    
        with psycopg2.connect(**config["postgres"]) as conn:
            with conn.cursor("myCursor") as cursor:
                cursor.execute(select_sql)
                with conn.cursor() as client_cursor:
                    for (upvotes, downvotes) in cursor:
                        users = [] if upvotes is None else upvotes.split(",")
                        users += [] if downvotes is None else downvotes.split(",")
                        for user in users:
                            client_cursor.execute(INSERT_INTO_USERS, (user,))
    
        print(f"Users extracted (#{offset} to #{offset + limit}) from bad_posts(upvotes, downvotes) are now successfully migrated!")

    print("All users collected from votes are now successfully migrated!")

def migrate_topics():
    """
    Migrate all topics from old tables to topics tables.
    """
    # ˋ這裡我把先前的 Migrate 方式 comment 掉，改用 TableMigrator Class 來做資料遷移。
    # SELECT_USER_ID = get_sql('select_user_id')
    # limit = 10000

    # insert_sql="""
    # INSERT INTO topics (name, user_id)
    # VALUES (%s, %s)
    # ON CONFLICT (name) DO NOTHING;
    # """

    # for i in range(5):
    #     offset = i * limit

    #     select_sql=f"""
    #     SELECT topic, username
    #     FROM bad_posts
    #     LIMIT {limit}
    #     OFFSET {offset};
    #     """
    #     with psycopg2.connect(**config["postgres"]) as conn:
    #         with conn.cursor("myCursor") as server_cursor:
    #             server_cursor.execute(select_sql)
    #             with conn.cursor() as client_cursor:
    #                 for topic in server_cursor:
    #                     client_cursor.execute(SELECT_USER_ID, (topic[1],))
    #                     users = client_cursor.fetchall()
    #                     if users:
    #                         [[user_id]] = users
    #                         # print(f"topic : {topic}")
    #                         # print(f"user : {user_id}")
    #                         client_cursor.execute(insert_sql, (topic[0], user_id))
    #                     else:
    #                         print(f"Found a topic from a non-registerd user : {topic[1]}.")
    #                         recycle_logger.log(
    #                             recycle_to="users.name",
    #                             value=topic[1],
    #                             came_from="bac_posts.username",
    #                             can_be_recycle=True
    #                         )

    #     print(f"Topic extracted (#{offset} to #{offset + limit}) from bad_posts(topic, username) are now successfully migrated!")
    
    # print("All topics are now successfully migrated!")

    """
    Renew the migrate method with TableMigrator Class.
    """

    select_sql=f"""
    SELECT
        bad_post_id,
        topic,
        username,
        user_id
    FROM (
        SELECT
            bp.id AS bad_post_id,
            bp.topic,
            bp.username,
            u.id AS user_id,
            ROW_NUMBER() OVER (PARTITION BY bp.topic ORDER BY bp.id, bp.username) AS rn
        FROM
            bad_posts bp
        INNER JOIN
            users u ON bp.username = u.name
    ) bad_topics
    WHERE rn = 1
    ORDER BY bad_post_id;
    """
    insert_sql="""
    INSERT INTO topics (name, user_id)
    VALUES (%s, %s)
    ON CONFLICT (name) DO NOTHING;
    """

    migrator = TableMigrator(conn_config=config["postgres"])

    def validate_func(row):
        return True

    def transform_func(row):
        print(f"to insert row : {row}")
        return (row["topic"], row["user_id"])
    
    total_migrated = migrator.migrate_table(
        source_query=select_sql,
        insert_query=insert_sql,
        transform_func=transform_func,
        validate_func=validate_func
    )

    print(f"total_migrated topics : {total_migrated}")


def migrate_posts():
    """
    Migrate all posts from old tables to posts tables.
    """
    select_sql=f"""
    SELECT
        bp.id,
        bp.title,
        bp.url,
        bp.text_content,
        bp.topic,
        bp.username,
        u.id AS user_id,
        t.id AS topic_id
    FROM
        bad_posts bp
    LEFT JOIN
        users u ON bp.username = u.name
    LEFT JOIN
        topics t ON bp.topic = t.name
    ORDER BY bp.id;
    """
    insert_sql = """
    INSERT INTO posts (title, url, content, topic_id, user_id)
    VALUES (%s, %s, %s, %s, %s);
    """

    migrator = TableMigrator(conn_config=config["postgres"])

    def validate_func(row):
        
        id, title, url, text_content, topic, topic_id = row["id"], row["title"], row["url"], row["text_content"], row["topic"], row["topic_id"]
        
        if title is None:
            recycle_logger.log(
                recycle_to="posts",
                value=id,
                came_from="bad_posts.id",
                can_be_recycle=False,
                missing='title'
            )
            return False
        if topic is None:
            recycle_logger.log(
                recycle_to="posts",
                value=id,
                came_from="bad_posts.id",
                can_be_recycle=False,
                missing='topic'
            )
            return False
        if topic_id is None:
            recycle_logger.log(
                recycle_to="topic",
                value=topic,
                came_from="bad_posts",
                can_be_recycle=True
            )
            recycle_logger.log(
                recycle_to="posts",
                value=id,
                came_from="bad_posts.id",
                can_be_recycle=True,
                missing='topic_id'
            )
            return False
        if url is None and text_content is None:
            recycle_logger.log(
                value=id,
                came_from="bad_posts.id",
                can_be_recycle=False,
                missing='url OR text_content'
            )
            return False
        
        return True

    def transform_func(row):
        id, title, url, text_content, topic, username, user_id, topic_id = row.values()
        return (title[:100], url, text_content, topic_id, user_id)

    total_migrated = migrator.migrate_table(
        source_query=select_sql,
        insert_query=insert_sql,
        transform_func=transform_func,
        validate_func=validate_func
    )

    print(f"total_migrated posts : {total_migrated}")

def migrate_comments():
    """
    Migrate all comments from old tables to comments tables.
    """
    select_sql=f"""
    SELECT
        bc.id,
        bc.text_content,
        cu.name AS comment_user,
        cu.id AS comment_user_id,
        p.id AS post_id,
        pu.name AS post_username
    FROM
        bad_comments bc
    INNER JOIN
        bad_posts bp
        ON bp.id = bc.post_id
    LEFT JOIN
        users pu
        ON pu.name = bp.username
    LEFT JOIN
        posts p
        ON SUBSTRING(bp.title FROM 1 FOR 100) = p.title
        AND p.user_id = pu.id
    LEFT JOIN
        users cu
        ON cu.name = bc.username
    ORDER BY bc.id
    """
    insert_sql = """
    INSERT INTO comments (content, post_id, user_id)
    VALUES (%s, %s, %s);
    """

    migrator = TableMigrator(
        conn_config=config["postgres"]
    )

    def validate_func(row):
        if row["post_id"] is None:
            recycle_logger.log(
                recycle_to="comments",
                value=row["id"],
                came_from="bad_comments.id",
                can_be_recycle=False,
                missing='post_id'
            )
            return False
        if row["text_content"] is None or len(row["text_content"]) == 0:
            recycle_logger.log(
                recycle_to="comments",
                value=row["id"],
                came_from="bad_comments.id",
                can_be_recycle=False,
                missing='text_content'
            )
            return False
        return True
    
    def transform_func(row):
        # content, post_id, user_id
        return (
            row["text_content"],
            row["post_id"],
            row["comment_user_id"]
        )

    total_migrated = migrator.migrate_table(
        source_query=select_sql,
        insert_query=insert_sql,
        transform_func=transform_func,
        validate_func=validate_func
    )

    print(f"total_migrated comments : {total_migrated}")

def migrate_votes():
    """
    Migrate all votes from old tables to votes tables.
    """

    # Practice code:
    # def test(str):
    #     # return chain(*str.split(","))
    #     # return str.split(",")
    #     return str.split(",")
    # arr = [*test("A,B,C"), *test("1,2,3,4")]
    # print(arr)

    select_sql=f"""
    SELECT
        u_split.id AS user_id,
        split_username.username,
        p.id AS post_id,
        bp.id AS bad_post_id,
        1 AS result
    FROM
        bad_posts bp
    LEFT JOIN
        users bp_u
        ON bp_u.name = bp.username
    LEFT JOIN
        posts p
        ON p.title = SUBSTRING(bp.title FROM 1 FOR 100)
        AND p.user_id = bp_u.id
    CROSS JOIN LATERAL
        regexp_split_to_table(bp.upvotes, ',') AS split_username(username)
    LEFT JOIN
        users u_split
        ON u_split.name = split_username.username
    UNION ALL
    SELECT
        u_split.id AS user_id,
        split_username.username,
        p.id AS post_id,
        bp.id AS bad_post_id,
        -1 AS result
    FROM
        bad_posts bp
    LEFT JOIN
        users bp_u
        ON bp_u.name = bp.username
    LEFT JOIN
        posts p
        ON p.title = SUBSTRING(bp.title FROM 1 FOR 100)
        AND p.user_id = bp_u.id
    CROSS JOIN LATERAL
        regexp_split_to_table(bp.downvotes, ',') AS split_username(username)
    LEFT JOIN
        users u_split
        ON u_split.name = split_username.username
    ORDER BY
        bad_post_id, result DESC, user_id
    """
    insert_sql = """
    INSERT INTO votes (post_id, user_id, result)
    VALUES (%s, %s, %s)
    ON CONFLICT (post_id, user_id) DO NOTHING;
    """

    migrator = TableMigrator(
        conn_config=config["postgres"]
        # total_limit=30,
        # testing=True
    )

    def validate_func(row):
        post_id, result = row['post_id'], row['result']
        if post_id is None:
            recycle_logger.log(
                recycle_to="votes",
                value=f"{row['bad_post_id']}, {row['username']}, {result}",
                came_from="bad_post_id, username, result",
                can_be_recycle=True,
                missing='post_id'
            )
            return False
        if result is None or (result != 1 and result != -1):
            recycle_logger.log(
                recycle_to="votes",
                value=f"{row['bad_post_id']}, {row['username']}",
                came_from="bad_post_id, username",
                can_be_recycle=False,
                missing='result'
            )
            return False
        return True
    
    def transform_func(row):
        # print(f"insert row : {row}")
        # (post_id, user_id, result)
        return (
            row["post_id"],
            row["user_id"],
            row["result"]
        )
    
    total_migrated = migrator.migrate_table(
        source_query=select_sql,
        insert_query=insert_sql,
        transform_func=transform_func,
        validate_func=validate_func
    )

    print(f"total_migrated votes : {total_migrated}")




if __name__ == "__main__":
    # init_db()
    # migrate_users()
    # migrate_users_from_votes()
    # migrate_topics()
    # migrate_posts()
    # migrate_comments()
    # migrate_votes()
    pass