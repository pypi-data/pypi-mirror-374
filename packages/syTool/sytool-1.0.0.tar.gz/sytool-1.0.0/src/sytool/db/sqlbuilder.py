import re
from enum import Enum, auto
from functools import wraps
from typing import Tuple, List, Optional, Dict, Any, Union, Iterable


class SQLBuilderError(Exception):
    """SQL构建器基础异常"""


class InvalidOperatorError(SQLBuilderError):
    """无效的SQL操作符异常"""


class SQLInjectionWarning(UserWarning):
    """潜在SQL注入风险警告"""


class LogicOperator(Enum):
    """逻辑运算符类型枚举"""
    AND = auto()
    OR = auto()


class ConditionNode:
    """抽象条件节点基类"""

    def __init__(self, operator: LogicOperator = LogicOperator.AND):
        self.operator = operator
        self.parent: Optional[ConditionGroup] = None  # 新增父节点引用


class AtomicCondition(ConditionNode):
    """原子条件节点（字段+操作符+值）"""

    __slots__ = ('field', 'operator', 'value')

    def __init__(self, field: str, operator: str, value: object):
        super().__init__()
        self.field = field
        self.operator = operator.upper()
        self.value = value


class ConditionGroup(ConditionNode):
    """条件组节点（支持嵌套结构）"""

    __slots__ = ('conditions', 'nested')

    def __init__(self, operator: LogicOperator = LogicOperator.AND, nested: bool = False):
        super().__init__(operator)
        self.conditions: List[ConditionNode] = []
        self.nested = nested  # 是否需要括号包裹


def check_operation(allowed_operations: Union[str, Iterable[str]]):
    """操作类型校验装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if isinstance(allowed_operations, str):
                allowed = {allowed_operations}
            else:
                allowed = set(allowed_operations)

            if self._operation and self._operation not in allowed:
                raise SQLBuilderError(
                    f"方法 {func.__name__} 不能在 {self._operation} 操作中使用")
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def validate_identifier(func):
    """字段标识符校验装饰器"""

    @wraps(func)
    def wrapper(self, field: str, *args, **kwargs):
        self._validate_identifier(field)
        return func(self, field, *args, **kwargs)

    return wrapper


class SQLBuilder:
    """
    安全动态SQL构建器（支持复杂嵌套条件）

    优化点：
    1. 增强SQL注入防御机制 [1,2](@ref)
    2. 改进批量插入性能优化算法
    3. 修复分页逻辑边界问题
    4. 完善类型注解和文档
    """
    _VALID_OPERATORS = {'=', '>', '<', '>=', '<=', '!=', 'LIKE', 'BETWEEN',
                        'IN', 'NOT_IN', 'IS_NULL', 'IS_NOT_NULL'}
    _SAFE_FIELD_REGEX = re.compile(r'^([a-zA-Z_]\w*\.)*([a-zA-Z_]\w*|\*)$')
    _RESERVED_WORDS = {'select', 'insert', 'update', 'delete', 'join', 'where', 'table', 'from'}
    _VALID_JOIN_TYPES = {'INNER', 'LEFT', 'RIGHT', 'FULL'}
    _FUNCTION_NAMES = {'sum', 'count', 'avg', 'min', 'max'}  # 扩展常用函数名列表

    def __init__(self, table: str, dialect: str = 'mysql', max_parameters: int = 2100):
        self._validate_identifier(table)
        self.dialect = dialect.lower()
        self._table = self._escape_identifier(table)
        self.placeholder = self._get_placeholder()
        self._max_parameters = max(100, min(max_parameters, 65535))  # 参数范围限制
        self._reset_state()

    def _reset_state(self):
        """重置构建器状态"""
        self._operation: Optional[str] = None
        self._selected_fields: List[str] = []
        self._join_clauses: List[str] = []
        self._order_clauses: List[str] = []
        self._limit_value: Optional[int] = None
        self._offset_value: Optional[int] = None
        self._update_data: Dict[str, Any] = {}
        self._insert_records: List[Dict[str, Any]] = []
        self._batch_insert_fields: Optional[set] = None
        self._condition_root = ConditionGroup()
        self._current_group_stack = [self._condition_root]

    def and_(self) -> 'SQLBuilder':
        """设置后续条件使用AND连接"""
        self._current_group.operator = LogicOperator.AND
        return self

    def or_(self) -> 'SQLBuilder':
        """设置后续条件使用OR连接"""
        self._current_group.operator = LogicOperator.OR
        return self

    def start_group(self, nested: bool = True) -> 'SQLBuilder':
        """开启新条件组（默认创建嵌套组）"""
        new_group = ConditionGroup(
            operator=self._current_group.operator,
            nested=nested
        )
        self._current_group.conditions.append(new_group)
        self._current_group_stack.append(new_group)
        return self

    def end_group(self) -> 'SQLBuilder':
        """结束当前条件组"""
        if len(self._current_group_stack) <= 1:
            raise SQLBuilderError("条件组结束标记不匹配")
        self._current_group_stack.pop()
        return self

    # endregion

    # region MyBatis-Plus风格快捷方法
    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def eq(self, field: str, value: Any, condition: bool = True) -> 'SQLBuilder':
        """等于条件（=）"""
        return self._add_condition(field, '=', value, condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def ne(self, field: str, value: Any, condition: bool = True) -> 'SQLBuilder':
        """不等于条件（!=或<>）"""
        op = '!=' if self.dialect != 'sqlserver' else '<>'
        return self._add_condition(field, op, value, condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def gt(self, field: str, value: Any, condition: bool = True) -> 'SQLBuilder':
        """大于条件（>）"""
        return self._add_condition(field, '>', value, condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def ge(self, field: str, value: Any, condition: bool = True) -> 'SQLBuilder':
        """大于等于条件（>=）"""
        return self._add_condition(field, '>=', value, condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def lt(self, field: str, value: Any, condition: bool = True) -> 'SQLBuilder':
        """小于条件（<）"""
        return self._add_condition(field, '<', value, condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def le(self, field: str, value: Any, condition: bool = True) -> 'SQLBuilder':
        """小于等于条件（<=）"""
        return self._add_condition(field, '<=', value, condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def between(self, field: str, start: Any, end: Any, condition: bool = True) -> 'SQLBuilder':
        """区间条件（BETWEEN）"""
        return self._add_condition(field, 'BETWEEN', (start, end), condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def like(self, field: str, value: str, case_insensitive: bool = False, condition: bool = True) -> 'SQLBuilder':
        """模糊查询（LIKE/ILIKE）"""
        op = 'ILIKE' if case_insensitive and self.dialect == 'postgresql' else 'LIKE'
        return self._add_condition(field, op, f"%{value}%", condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def in_list(self, field: str, values: Iterable, condition: bool = True) -> 'SQLBuilder':
        """包含条件（IN）"""
        return self._add_condition(field, 'IN', values, condition)

    @validate_identifier
    @check_operation({'SELECT', 'UPDATE', 'DELETE'})
    def is_null(self, field: str, condition: bool = True) -> 'SQLBuilder':
        """空值条件（IS NULL）"""
        return self._add_condition(field, 'IS_NULL', None, condition)

    # ========================

    def join(self, table: str, on: str, join_type: str = "INNER") -> 'SQLBuilder':
        """
        添加JOIN子句
        :param table: 关联表名
        :param on: 关联条件（格式：left_field=right_field）
        :param join_type: JOIN类型（INNER/LEFT/RIGHT/FULL）
        """
        join_type = join_type.upper()
        if join_type not in self._VALID_JOIN_TYPES:
            raise ValueError(f"无效JOIN类型: {join_type}")

        self._validate_identifier(table)

        # 解析关联条件
        try:
            left, right = map(str.strip, on.split('=', 1))
            self._validate_identifier(left)
            self._validate_identifier(right)
        except ValueError:
            raise SQLBuilderError(f"无效的JOIN条件格式: {on}")

        safe_condition = f"{self._escape_identifier(left)} = {self._escape_identifier(right)}"
        self._join_clauses.append(
            f"{join_type} JOIN {self._escape_identifier(table)} ON {safe_condition}"
        )
        return self

    def order_by(self, field: str, direction: str = 'ASC') -> 'SQLBuilder':
        """添加排序条件"""
        direction = direction.upper()
        if direction not in ('ASC', 'DESC'):
            raise ValueError("排序方向必须是ASC或DESC")
        self._order_clauses.append(f"{self._escape_identifier(field)} {direction}")
        return self

    def limit(self, count: int, condition: bool = True) -> 'SQLBuilder':
        """设置返回结果限制"""
        if not condition:
            return self
        self._limit_value = count
        return self

    def offset(self, offset: int, condition: bool = True) -> 'SQLBuilder':
        """设置结果偏移量"""
        if not condition:
            return self
        self._offset_value = offset
        return self

    # --------------------------
    # 数据操作（DML）方法
    # --------------------------
    @check_operation({'SELECT'})
    def select(self, *fields: str) -> 'SQLBuilder':
        """
        设置查询字段（支持字段别名和表达式）

        :param fields: 字段列表（支持"name AS username"格式）
        :return: 当前实例
        """
        self._operation = 'SELECT'
        self._selected_fields = [self._escape_expression(f) for f in fields] if fields else ['*']
        return self

    @check_operation('UPDATE')
    def update(self) -> 'SQLBuilder':
        """设置UPDATE操作"""
        self._operation = 'UPDATE'
        return self

    @check_operation('DELETE')
    def delete(self) -> 'SQLBuilder':
        """设置DELETE操作"""
        self._operation = 'DELETE'
        return self

    @check_operation('INSERT')
    def insert(self, batch_mode: bool = False) -> 'SQLBuilder':
        """
        设置INSERT模式
        :param batch_mode: 是否批量插入模式
        """
        self._operation = 'INSERT'
        self._batch_insert_mode = batch_mode
        return self

    @check_operation('INSERT')
    def values(self, **kwargs) -> 'SQLBuilder':
        """添加插入数据（批量模式需保持字段一致）"""
        if not kwargs:
            raise ValueError("插入记录不能为空")

        if not self._insert_records:
            self._batch_insert_fields = set(kwargs.keys())
            self._insert_records.append(kwargs)
        else:
            if self._batch_insert_mode:
                if set(kwargs.keys()) != self._batch_insert_fields:
                    raise ValueError("批量插入字段不一致")
                self._insert_records.append(kwargs)
            else:
                raise RuntimeError("单次插入已存在记录")
        return self

    @check_operation('UPDATE')
    def set(self, field, value, condition: bool = True) -> 'SQLBuilder':
        """设置UPDATE操作"""
        if not condition:
            return self

        safe_field = self._escape_identifier(field)
        self._update_data[safe_field] = value
        return self

    # --------------------------
    # SQL生成核心方法
    # --------------------------
    def build(self) -> Tuple[str, Tuple]:
        """生成最终SQL和参数元组"""
        if not self._operation:
            raise SQLBuilderError("未指定操作类型")

        method_name = f'_build_{self._operation.lower()}'
        if not hasattr(self, method_name):
            raise SQLBuilderError(f"不支持的操作类型: {self._operation}")

        sql, params = getattr(self, method_name)()
        self._reset_state()  # 构建后重置状态
        return sql, tuple(params)

    def _build_select(self) -> Tuple[str, List]:
        """构建SELECT查询语句"""
        clauses = [
            f"SELECT {', '.join(self._selected_fields)}",
            f"FROM {self._table}"
        ]

        if self._join_clauses:
            clauses.extend(self._join_clauses)

        # 拼接where条件
        where_clause, where_params = self._build_where_clause()
        if where_clause:
            clauses.append(where_clause)
        sql = ' '.join(clauses)

        if self._order_clauses:
            sql += f" ORDER BY {', '.join(self._order_clauses)}"

        sql, params = self._apply_pagination(sql)
        where_params = where_params + params
        return sql, where_params

    def _build_where_clause(self) -> Tuple[str, List]:
        """递归生成带正确括号的WHERE子句"""

        def build_node(node: ConditionNode, level=0) -> Tuple[str, list]:
            fragments = []
            params = []
            for condition in node.conditions:
                if isinstance(condition, AtomicCondition):
                    frag, p = self._build_atomic_condition(condition)
                    fragments.append(frag)
                    params.extend(p)
                elif isinstance(condition, ConditionGroup):
                    sub_frag, sub_params = build_node(condition, level + 1)
                    fragments.append(f"({sub_frag})" if condition.nested else sub_frag)
                    params.extend(sub_params)

            connector = " AND " if node.operator == LogicOperator.AND else " OR "
            return connector.join(fragments), params

        where_clause, params = build_node(self._condition_root)
        return f" WHERE {where_clause}" if where_clause else "", params

    def _build_atomic_condition(self, condition: AtomicCondition) -> Tuple[str, list]:
        """构建原子条件SQL片段"""
        operator = condition.operator
        params = []

        # 参数化处理
        if operator == 'BETWEEN':
            frag = f"{condition.field} BETWEEN {self.placeholder} AND {self.placeholder}"
            params.extend(condition.value)
        elif operator == 'IN':
            placeholders = ', '.join([self.placeholder] * len(condition.value))
            frag = f"{condition.field} IN ({placeholders})"
            params.extend(condition.value)
        elif operator in ('IS_NULL', 'IS_NOT_NULL'):
            frag = f"{condition.field} {operator.replace('_', ' ')}"
        else:
            frag = f"{condition.field} {operator} {self.placeholder}"
            params.append(condition.value[0] if isinstance(condition.value, (list, tuple)) else condition.value)

        return frag, params

    def _build_update(self) -> Tuple[str, Tuple]:
        """构建支持多表关联的UPDATE语句"""
        if not self._update_data:
            raise SQLBuilderError("UPDATE操作需要更新字段")

        # 核心更新字段处理
        set_clause = ', '.join(
            [f"{field} = {self.placeholder}" for field in self._update_data]
        )
        params = list(self._update_data.values())

        # 关联表处理（网页1、网页2）
        from_clause = []
        if self._join_clauses:
            from_clause.append(f"FROM {' '.join(self._join_clauses)}")

        # 条件处理（网页9条件树结构）
        where_clause, where_params = self._build_where_clause()

        # 方言适配（网页1的SQL Server语法）
        if self.dialect == 'sqlserver' and from_clause:
            sql = f"UPDATE {self._table} SET {set_clause} {' '.join(from_clause)}"
        else:
            sql = f"UPDATE {self._table} {' '.join(from_clause)} SET {set_clause}"

        # 添加WHERE条件
        if where_clause:
            sql += where_clause
            params.extend(where_params)

        return sql, tuple(params)

    def _build_delete(self) -> Tuple[str, Tuple]:
        """构建支持联表删除的DELETE语句"""
        # 关联表处理（网页7联表删除）
        using_clause = []
        if self._join_clauses:
            if self.dialect == 'postgresql':
                using_clause.append(f"USING {' '.join(self._join_clauses)}")
            else:
                using_clause.append(f"FROM {' '.join(self._join_clauses)}")

        # 条件处理（复用条件树）
        where_clause, where_params = self._build_where_clause()

        # 构建基础SQL
        sql = f"DELETE FROM {self._table}"
        if using_clause:
            sql += f" {' '.join(using_clause)}"

        # 添加WHERE条件
        if where_clause:
            sql += where_clause

        return sql, tuple(where_params)

    def _build_insert(self) -> Tuple[str, Tuple]:
        """构建INSERT语句（支持批量插入优化）"""
        if not self._insert_records:
            raise SQLBuilderError("INSERT操作需要插入数据")

        columns = [self._escape_identifier(k) for k in self._insert_records[0].keys()]
        column_str = ', '.join(columns)
        col_count = len(columns)

        # 计算最优批次大小（考虑参数限制和网络包大小）
        max_batch_size = max(1, self._max_parameters // col_count)
        batch_size = min(max_batch_size, 1000)  # 防止单个包过大

        sql_batches = []
        all_params = []

        for i in range(0, len(self._insert_records), batch_size):
            batch = self._insert_records[i:i + batch_size]
            placeholders = [f"({', '.join([self.placeholder] * col_count)})" for _ in batch]
            params = [v for record in batch for v in record.values()]

            batch_sql = (f"INSERT INTO {self._table} ({column_str}) VALUES "
                         f"{', '.join(placeholders)}")
            sql_batches.append(batch_sql)
            all_params.extend(params)

        return '; '.join(sql_batches), tuple(all_params)

    def _escape_expression(self, expr: str) -> str:
        """智能转义包含函数和别名的表达式"""
        # 处理AS别名
        alias_match = re.split(r'\s+AS\s+', expr, flags=re.IGNORECASE)
        if len(alias_match) == 2:
            expr_part, alias_part = alias_match
            return f"{self._escape_expression_part(expr_part)} AS {self._escape_identifier(alias_part)}"
        return self._escape_expression_part(expr)

    def _escape_expression_part(self, expr: str) -> str:
        """转义表达式部分"""
        # 处理函数中的字段（如COUNT(table.field)）
        if '(' in expr and ')' in expr:
            return re.sub(r'\b([a-zA-Z_]\w*\.)*[a-zA-Z_]\w*\b',
                          lambda m: self._escape_identifier(m.group()), expr)
        return self._escape_identifier(expr)

    def _escape_identifier(self, identifier: str) -> str:
        """安全转义SQL标识符，防止注入攻击"""
        # 如果是已知函数名则直接返回
        if identifier.lower() in self._FUNCTION_NAMES:
            return identifier

        escaped_parts = []
        for part in identifier.split('.'):
            if part == '*':
                escaped_parts.append('*')
                continue
            if part.lower() in self._RESERVED_WORDS:
                escaped_parts.append(self._wrap_reserved_word(part))
            elif self._SAFE_FIELD_REGEX.match(part):
                escaped_parts.append(self._wrap_normal_word(part))
            else:
                raise SQLInjectionWarning(f"非法标识符格式: {identifier}")
        return '.'.join(escaped_parts)

    def _wrap_reserved_word(self, word: str) -> str:
        """处理保留字的转义"""
        if self.dialect == 'postgresql':
            return f'"{word}"'
        return f'`{word}`'

    def _wrap_normal_word(self, word: str) -> str:
        """常规标识符转义策略"""
        return word if self.dialect == 'postgresql' else f'`{word}`'

    def _validate_identifier(self, identifier: str):
        """验证标识符格式合法性"""
        if not identifier:  # 新增空值校验
            raise ValueError("标识符不能为空")
        if not self._SAFE_FIELD_REGEX.match(identifier):
            raise SQLInjectionWarning(f"非法标识符: {identifier}")
        if any(char in identifier for char in (';', '--', '/*')):
            raise SQLInjectionWarning(f"潜在注入风险: {identifier}")

    @property
    def _current_group(self) -> ConditionGroup:
        """获取当前条件组"""
        return self._current_group_stack[-1]

    def _get_placeholder(self) -> str:
        """获取参数占位符"""
        return {
            'mysql': '%s',
            'postgresql': '%s',
            'sqlite': '?',
            'sqlserver': '?'
        }.get(self.dialect, '%s')

    def _apply_pagination(self, sql: str) -> tuple[str, list[int, int]]:
        """处理分页语法（多方言适配）"""
        params = []
        if self.dialect == 'sqlserver':
            # SQL Server使用OFFSET FETCH语法
            if self._offset_value is not None or self._limit_value is not None:
                if "ORDER BY" not in sql:
                    raise SQLBuilderError("SQL Server分页必须包含ORDER BY")
                pagination = []
                # 处理自动添加OFFSET 0的情况
                if self._limit_value is not None and self._offset_value is None:
                    self._offset_value = 0
                    params.append(0)
                    pagination.append(f"OFFSET {self.placeholder} ROWS")
                elif self._offset_value is not None:
                    pagination.append(f"OFFSET {self.placeholder} ROWS")
                    params.append(self._offset_value)

                if self._limit_value is not None:
                    pagination.append(f"FETCH NEXT {self.placeholder} ROWS ONLY")
                    params.append(self._limit_value)

                if pagination:
                    sql += " " + " ".join(pagination)
        else:
            # 其他数据库使用LIMIT/OFFSET
            limits = []
            if self._limit_value is not None:
                limits.append(f"LIMIT {self.placeholder}")
                params.append(self._limit_value)
            if self._offset_value is not None:
                limits.append(f"OFFSET {self.placeholder}")
                params.append(self._offset_value)
            if limits:
                sql += " " + " ".join(limits)
        return sql, params

    def _add_condition(self, field: str, operator: str, value: object, condition: bool = True) -> 'SQLBuilder':
        """
        添加原子条件到当前条件组
        :param field: 字段名
        :param operator: 操作符
        :param value: 值
        :param condition: 执行条件
        """
        if not condition:
            return self

        # 验证操作符合法性
        operator = operator.upper().replace(' ', '_')
        if operator not in self._VALID_OPERATORS:
            raise InvalidOperatorError(f"无效操作符: {operator}")

        # 转义字段名并验证值类型
        safe_field = self._escape_identifier(field)
        validated_value = self._validate_condition_value(operator, value)

        # 创建原子条件并添加到当前组
        current_group = self._current_group
        current_group.conditions.append(
            AtomicCondition(safe_field, operator, validated_value)
        )
        return self

    def _validate_condition_value(self, operator: str, value: object) -> list:
        """验证条件值类型并返回参数列表"""
        if operator in ('IS_NULL', 'IS_NOT_NULL'):
            if value is not None:
                raise ValueError(f"{operator} 操作符不需要值参数")
            return []
        elif operator == 'BETWEEN':
            if not isinstance(value, (tuple, list)) or len(value) != 2:
                raise ValueError("BETWEEN需要两个元素的元组")
            return list(value)
        elif operator == 'IN':
            if not isinstance(value, (tuple, list)):
                raise ValueError("IN操作需要可迭代参数")
            return list(value)
        else:
            return [value]


# --------------------------
# 使用示例
# --------------------------
if __name__ == "__main__":
    # 示例1：单条插入
    builder = SQLBuilder('users', 'mysql')
    sql, params = (builder.insert()
                   .values(name='Alice', age=30, email='alice@example.com')
                   .build())
    print("单条插入:")
    print(sql)  # INSERT INTO `users` (`name`, `age`, `email`) VALUES (%s, %s, %s)
    print(params)  # ('Alice', 30, 'alice@example.com')
    print('\n==================================================================\n')

    # 示例2：批量插入（自动分批次）
    builder = SQLBuilder('products', 'postgresql', max_parameters=6)  # 测试用较小值
    (builder.insert(batch_mode=True)
     .values(name='Keyboard', price=99.99)
     .values(name='Mouse', price=49.99)
     .values(name='Monitor', price=199.99))
    sql, params = builder.build()
    print("批量插入:")
    print(sql)  # INSERT INTO products (name, price) VALUES (%s, %s), (%s, %s); INSERT ...
    print(params)  # ('Keyboard', 99.99, 'Mouse', 49.99, 'Monitor', 199.99)
    print('\n==================================================================\n')

    # 示例3：带条件更新
    builder = SQLBuilder('users', 'sqlite')
    sql, params = (builder.update().set('name', 'Bob').set('age', 35)
                   .eq('id', 1001)
                   .build())
    print("条件更新:")
    print(sql)  # UPDATE `users` SET `name` = ?, `age` = ? WHERE `id` = ?
    print(params)  # ('Bob', 35, 1001)
    print('\n==================================================================\n')

    # 示例4：复杂查询+分页
    builder = SQLBuilder('orders', 'mysql')
    sql, params = (builder.select('id as trade_id', 'total')
                   .join('customers', 'orders.customer_id = customers.id', 'LEFT')
                   .eq('status', 'completed')
                   .between('created_at', '2023-01-01', '2023-12-31')
                   .order_by('total', 'DESC')
                   .limit(10)
                   .offset(5)
                   .build())
    print("分页查询:")
    print(sql)  # SELECT `id`, `total` FROM `orders` LEFT JOIN ... BETWEEN ... LIMIT 10 OFFSET 5
    print(params)  # ('completed', '2023-01-01', '2023-12-31', 10, 5)
    print('\n==================================================================\n')

    # 统计
    builder = SQLBuilder('orders', 'mysql')
    sql, params = (builder.select('sum(m.money)')
                   .build())
    print("统计查询:")
    print(sql)  # SELECT `id`, `total` FROM `orders` LEFT JOIN ... BETWEEN ... LIMIT 10 OFFSET 5
    print(params)  # ('completed', '2023-01-01', '2023-12-31', 10, 5)
    print('\n==================================================================\n')

    # 示例5：删除操作
    builder = SQLBuilder('logs', 'postgresql')
    sql, params = (builder.delete()
                   .gt('created_at', '2020-01-01')
                   .like('name', 'bob%')
                   .between('time', '2025-03-24 10:01:00', '2025-04-24 10:01:00')
                   .build())
    print("条件删除:")
    print(sql)  # DELETE FROM logs WHERE created_at < %s
    print(params)  # ('2020-01-01',)
    print('\n==================================================================\n')

    """使用示例"""
    # 示例1：简单AND查询
    builder = SQLBuilder('users')
    sql, params = builder.select().gt("age", 18).eq("status", 1).build()
    print(f"select所有字段 SQL: {sql}")  # SELECT * FROM `users` WHERE `age` > ? AND `status` = ?
    print(params)  # ('2020-01-01',)
    print('\n==================================================================\n')

    # 示例2：复杂嵌套条件
    builder = SQLBuilder('products')
    (builder.select("id", "name")
     .start_group()
     .gt("price", 100)
     .or_()
     .start_group()
     .eq("category", "Electronics")
     .and_()
     .gt("stock", 0)
     .end_group()
     .end_group()
     .or_()
     .eq("is_active", 1))
    sql, params = builder.build()
    print(
        f"嵌套查询: {sql}")  # SELECT `id`, `name` FROM `products` WHERE (`price` > ? OR (`category` = ? AND `stock` > ?)) AND `is_active` = ?
    print(params)  # ('2020-01-01',)
    print('\n==================================================================\n')
