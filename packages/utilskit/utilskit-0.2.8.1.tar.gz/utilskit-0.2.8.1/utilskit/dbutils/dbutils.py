# DB
import pandas as pd
import pymysql
from sqlalchemy import create_engine

__all__ = ['query2db', 'df2db', 'get_db_column']


# def get_info():
#     db_host = '192.168.0.85'
#     db_port = 3306
#     db_user = 'theimc'
#     db_passward = 'theimc#10!'
#     db_name = 'BUSMONITORING'
#     charset = 'utf8mb4'
#     if_exists = 'append'
#     autocommit = True
#     return (db_host, db_port, db_user, db_passward, db_name, charset, if_exists, autocommit)


# def get_info_p5000():
#     db_host = "59.25.131.135"
#     db_port = 3306
#     db_user = "ai_m"
#     db_password = "temp"
#     db_name = "bus"
#     charset = 'utf8mb4'
#     if_exists = 'append'
#     autocommit = True
#     return (db_host, db_port, db_user, db_password, db_name, charset, if_exists ,autocommit)


def db_connect(host, user, port, password, name, charset='utf8mb4', autocommit=True):
    # db_host = db_info_dict['host']
    # db_port = db_info_dict['port']
    # db_user = db_info_dict['user']
    # db_passward = db_info_dict['passward']
    # db_name = db_info_dict['name']
    # charset = db_info_dict['charset']
    # if_exists = db_info_dict['if_exists']
    # autocommit = db_info_dict['autocommit']
    conn = pymysql.connect(
        host=host, 
        user=user, 
        port=port, 
        password=password, 
        db=name,
        charset=charset,
        autocommit=autocommit
    )
    return conn


def query2db(query, host, port, user, password, db_name, charset='utf8mb4', autocommit=True):
    conn = db_connect(
        host=host, 
        user=user, 
        port=port, 
        password=password, 
        name=db_name, 
        charset=charset, 
        autocommit=autocommit
    )
    cursor = conn.cursor()
    cursor.execute(query)
    info = cursor.fetchall()
    cursor.close()
    return info


def get_db_column(host, port, user, password, db_name, table):
    # 센서 정보 컬럼명 추출
    query = f"""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = '{db_name}' 
    AND TABLE_NAME = '{table}'"""
    column_list = query2db(query, host, port, user, password, db_name)
    column_list = [x[0] for x in column_list]
    return column_list


def df2db(dataframe, table, host, port, user, password, db_name, 
          charset='utf8mb4', index=False):
    
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset={charset}"
    # engine = create_engine(url, encoding=encoding)
    engine = create_engine(url)
    conn = engine.connect()
    dataframe.to_sql(name=table, con=engine, if_exists='append', index=index)
    conn.close()
    

# def pd2db(db_info_dict, df, table, encoding='utf-8-sig', index=False):
#     db_host = db_info_dict['host']
#     db_port = db_info_dict['port']
#     db_user = db_info_dict['user']
#     db_passward = db_info_dict['passward']
#     db_name = db_info_dict['name']
#     charset = db_info_dict['charset']
#     if_exists = db_info_dict['if_exists']
#     autocommit = db_info_dict['autocommit']
#     url = f"mysql+pymysql://{db_user}:{db_passward}@{db_host}:{db_port}/{db_name}?charset={charset}"
#     # engine = create_engine(url, encoding=encoding)
#     engine = create_engine(url)
#     conn = engine.connect()
#     df.to_sql(name=table, con=engine, if_exists=if_exists, index=index)
#     conn.close()
    

"""
def main():
    db_host = '211.195.9.226'
    db_port = 3306
    db_user = 'root'
    db_passward = 'theimc#10!'
    db_name = 'flagship'
    charset = 'utf8mb4'
    table = 'test'
    if_exists = 'append'
    autocommit = True
    
    df = pd.read_csv('D:/python/project/temp/example.csv', encoding='utf-8-sig')
    
    pd2db(
        db_user=db_user, 
        db_passward=db_passward, 
        db_host=db_host, 
        db_port=db_port, 
        db_name=db_name, 
        charset=charset, 
        df=df, 
        table=table, 
        if_exists=if_exists, 
        encoding='utf-8-sig', 
        index=False
    )
    

if __name__ == '__main__':
    main()

"""









            
