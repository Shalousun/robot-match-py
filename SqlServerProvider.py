# -*- coding: utf-8 -*-
import os

os.environ['NLS_LANG'] = '.AL32UTF8'
import pymssql
import pandas as pd
import DataProcessor as df


class SqlServerProvider:
    def __init__(self, connect):
        self.connect = connect

    def get_tables(self):
        sql = ""
        try:
            cursor = self.connect.cursor()
            cursor.execute(sql)
            rs = cursor.fetchall()
            return rs
        except Exception as e:
            print(e)

    def get_fields_info(self, table_name):

        if table_name and table_name.strip():
            # table_name is not None AND table_nameg is not empty or blank
            sql = "SELECT C.table_name, C.COLUMN_NAME, C.DATA_TYPE, C.CHARACTER_MAXIMUM_LENGTH, C.NUMERIC_PRECISION ," \
                  " C.NUMERIC_SCALE,CASE C.IS_NULLABLE WHEN   'NO' THEN 0 ELSE 1 END  as 'IS_NULLABLE' , CASE  WHEN Z.CONSTRAINT_NAME IS NULL THEN 0 ELSE 1 END AS IsPartOfPrimaryKey " \
                  "FROM INFORMATION_SCHEMA.COLUMNS C OUTER APPLY ( SELECT CCU.CONSTRAINT_NAME FROM " \
                  "INFORMATION_SCHEMA.TABLE_CONSTRAINTS TC JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE CCU ON " \
                  "CCU.CONSTRAINT_NAME = TC.CONSTRAINT_NAME WHERE TC.TABLE_SCHEMA = C.TABLE_SCHEMA " \
                  "AND TC.TABLE_NAME = C.TABLE_NAME AND TC.CONSTRAINT_TYPE = 'PRIMARY KEY' " \
                  "AND CCU.COLUMN_NAME = C.COLUMN_NAME ) Z WHERE C.TABLE_NAME = '" + table_name + " '"
        else:
            # table_name is None OR table_name is empty or blank
            sql = "SELECT  C.table_name,C.COLUMN_NAME,C.DATA_TYPE,C.CHARACTER_MAXIMUM_LENGTH,C.NUMERIC_PRECISION ," \
                  " C.NUMERIC_SCALE, CASE C.IS_NULLABLE WHEN   'NO' THEN 0 ELSE 1 END  as 'IS_NULLABLE', CASE  WHEN Z.CONSTRAINT_NAME IS NULL THEN 0 ELSE 1 END AS IsPartOfPrimaryKey " \
                  "FROM INFORMATION_SCHEMA.COLUMNS C OUTER APPLY ( SELECT CCU.CONSTRAINT_NAME FROM " \
                  "INFORMATION_SCHEMA.TABLE_CONSTRAINTS TC JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE CCU ON " \
                  "CCU.CONSTRAINT_NAME = TC.CONSTRAINT_NAME WHERE TC.TABLE_SCHEMA = C.TABLE_SCHEMA " \
                  "AND TC.TABLE_NAME = C.TABLE_NAME AND TC.CONSTRAINT_TYPE = 'PRIMARY KEY' " \
                  "AND CCU.COLUMN_NAME = C.COLUMN_NAME ) Z "
        col_list = []

        data_list = []
        try:
            cursor = self.connect.cursor()
            cursor.execute(sql)
            rs = cursor.fetchall()
            for row in rs:
                # tuple to list
                tem = list(row)
                print tem[2]
                # convert data type value
                tem[2] = df.proccess_data_type(row[2])
                # 对每个column进行统计
                col_name = tem[1]
                if tem[2] == 2:
                    tem[3] = 22  # 将sqlserver的所有数字型的字段长度改成22
                    data_sql = "SELECT '" + col_name + "' as column_name,round(max(" + col_name + "),2),round(min(" \
                               + col_name + "),2),round(avg(" + col_name + "),2),round(STDEV(" + col_name \
                               + "),2),round(VAR(" + col_name + "),2) from " + table_name
                else:
                    data_sql = "SELECT '" + col_name + "' as column_name,round(max(DATALENGTH(" + col_name + ")),2),round(min(DATALENGTH(" \
                               + col_name + ")),2),round(avg(DATALENGTH(" + col_name + ")),2),round(STDEV(DATALENGTH(" + col_name \
                               + ")),2),round(VAR(DATALENGTH(" + col_name + ")),2) from " + table_name
                cursor.execute(data_sql)
                rs_data = cursor.fetchall()
                list_data = list(rs_data[0])
                data_list.append(list_data)
                col_list.append(tem)

            df_col = pd.DataFrame(list(col_list),
                                  columns=['table_name', 'column_name', 'data_type', 'CHARACTER_MAXIMUM_LENGTH',
                                           'NUMERIC_PRECISION', 'NUMERIC_SCALE', 'nullable',
                                           'IsPartOfPrimaryKey'])
            df_data = pd.DataFrame(data=data_list, columns=['column_name', 'max', 'min', 'avg', 'stddev', 'varience'])
            df_col = df_col.merge(df_data, on='column_name', how='left')
            return df_col
        except Exception as ex:
            print(ex)
        finally:
            self.connect.close()


def get_connect():
    try:
        conn = pymssql.connect(host='192.168.15.99',
                               user='sa',
                               password='boco#1234',
                               database='lis6')
        return conn
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    connect = get_connect()
    mss_sql = SqlServerProvider(connect)
    rs = mss_sql.get_fields_info("lab_dilution")
    print rs
    # rs_dataframe = pd.DataFrame(list(rs), columns=['table_name', 'column_name', 'data_type', 'CHARACTER_MAXIMUM_LENGTH',
    #                                                 'NUMERIC_PRECISION', 'NUMERIC_SCALE', 'nullable',
    #                                                 'IsPartOfPrimaryKey'])
    # print(rs_dataframe)
