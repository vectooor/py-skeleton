
import sqlparse
from sqlparse import tokens as T

"""
需要 pip install sqlparse 
或者(如果使用了conda管理package) conda install sqlparse
"""

def extract_where(where_cluase, where_condition):
    """
        抽取SQL中的where条件，返回一个字典数组，字典格式如下：
        {
            'key': 'CERTNO',
            'comparison': '=',
            'value': '370627195709120245'
        }
    """
    for token in where_cluase.tokens:
        # 遇到括号，递归解析
        if isinstance(token, sqlparse.sql.Parenthesis):
            extract_where(token, where_condition)
        # SQL的区间操作（包括=、IN等）
        elif isinstance(token, sqlparse.sql.Comparison):
            where_condition.append({
                'key': token.left.value,
                # 比较符
                'comparison': token.token_next(0)[1].value,
                # 如果类型是字符串，去掉首尾的单引号或双引号
                # （在SQL语句中，如果是字符串，则首尾必定存在单引号或双引号）
                # 如果是其他类型有额外的需求，在此调整即可
                'value': token.right.value[1:-1] if token.right.ttype == T.String.Single else token.right.value
            })
        else:
            pass


if __name__ == '__main__':
    sql = "SELECT * FROM t_userinfo WHERE (CERTNO = '370627195709120245') AND (CNAME='ymz') AND age>=18"
    where_condition =[]

    where_cluase = sqlparse.parse(sql)[0][-1]
    extract_where(where_cluase, where_condition)
    
    for item in where_condition:
        print(item)
