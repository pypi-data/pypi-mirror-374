# authlib/db_helper.py

from datetime import datetime,timedelta
import uuid
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func,text
from wxswutilsapi import Logger
import time
logger = Logger()
class mydb:
    def __init__(self, db_session, default_time_field='created_at'):
        self.db = db_session
        self.default_time_field = default_time_field

    def apply_filters(self,query, model, params, filters, field_mappings, joins):
        time_field_name = params.get('_time', self.default_time_field)  # 默认时间字段为 created_at
        time_field = getattr(model, time_field_name, None)

        if 'start_time' in filters and time_field is not None:
            query = query.filter(time_field >= filters['start_time'])
        if 'end_time' in filters and time_field is not None:
            query = query.filter(time_field <= filters['end_time'])

        for key, value in params.items():
            if key.startswith('%'):
                raw_key = key[1:]
                if raw_key in field_mappings:
                    relation, column_name = field_mappings[raw_key].split('.')
                    related_model = joins.get(relation)
                    if related_model:
                        column = getattr(related_model, column_name, None)
                        if column is not None:
                            query = query.filter(column.like(f"%{value}%"))
                else:
                    column = getattr(model, raw_key, None)
                    if column is not None:
                        query = query.filter(column.like(f"%{value}%"))
            elif key not in ['_start', '_count', '_order', '_by', 'startTime', 'endTime', '_fields', '_time']:
                column = getattr(model, key, None)
                if column is not None:
                    query = query.filter(column == value)
        return query
    
    def row_to_dict(self, row, fields):
        data = {}
        for idx, field in enumerate(fields):
            if field == "password":
                continue
            value = row[idx]
            if isinstance(value, datetime):
                data[field] = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                data[field] = value
        return data
    
    def fetch_all_by2(self, model, params, fields=None, no_total=False, field_mappings=None):
        """
        通用查询方法，支持字段筛选、关联字段、过滤、排序、分页。

        :param model: SQLAlchemy模型类
        :param params: 查询参数字典，支持过滤、分页、排序等
        :param fields: 要查询的字段列表，None表示查询全部模型字段
        :param no_total: 是否跳过统计总数
        :param field_mappings: 关联字段映射字典，格式 {'alias': 'relation.column'}
        :return: (结果列表[dict], 总数int)
        """
        if field_mappings is None:
            field_mappings = {}

        try:
            # 解析时间过滤
            filters = {}
            start_time = params.get('startTime')
            end_time = params.get('endTime')
            if start_time:
                filters['start_time'] = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if end_time:
                filters['end_time'] = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

            query = self.db.query(model)
            joins = {}

            # 处理关联字段映射，动态添加join和字段
            for alias, path in field_mappings.items():
                relation, column_name = path.split('.')
                related_model = getattr(model, relation).property.mapper.class_
                joins[relation] = related_model
                query = query.add_columns(getattr(related_model, column_name).label(alias))

            # 加入关联join
            for relation, related_model in joins.items():
                query = query.join(related_model, getattr(model, relation))

            # 如果指定了fields，改用add_columns选择字段
            if fields:
                columns = []
                for f in fields:
                    col = getattr(model, f, None)
                    if col is None:
                        raise ValueError(f"字段 '{f}' 在模型 {model.__name__} 中不存在")
                    columns.append(col)
                query = query.with_entities(*columns)

            # 应用过滤条件
            query = self.apply_filters(query, model, params, filters, field_mappings, joins)

            # 排序
            if '_order' in params and '_by' in params:
                _order = params['_order']
                _by = params['_by']
                column = getattr(model, _by, None)
                if column is not None:
                    query = query.order_by(column.asc() if _order.lower() == 'asc' else column.desc())

            # 分页
            if '_start' in params and '_count' in params:
                query = query.offset(params['_start']).limit(params['_count'])

            # 执行查询
            result = query.all()

            # 处理结果
            if field_mappings:
                # 带关联字段，结果是元组，row[0]是模型实例，其他是label字段
                result_dict = [
                    {**row[0].to_dict(), **{alias: getattr(row, alias) for alias in field_mappings}}
                    for row in result
                ]
            elif fields:
                # fields 查询只返回字段元组，构造字典
                result_dict = [self.row_to_dict(row, fields) for row in result]
            else:
                # 返回完整模型实例
                result_dict = [item.to_dict() for item in result]

            # 统计总数（除非no_total为True）
            total = 0
            if not no_total:
                total_query = self.db.query(model)
                for relation, related_model in joins.items():
                    total_query = total_query.join(related_model, getattr(model, relation))
                total_query = self.apply_filters(total_query, model, params, filters, field_mappings, joins)
                total = total_query.count()

            return result_dict, total

        except Exception as e:
            raise ValueError(f"查询失败: {str(e)}") from e
        
    def fetch_all_by(self, model, params, fields=None, no_total=False, field_mappings=None):
        """
        通用查询方法，支持字段筛选、关联字段、过滤、排序、分页。

        :param model: SQLAlchemy模型类
        :param params: 查询参数字典，支持过滤、分页、排序等
        :param fields: 要查询的字段列表，None表示查询全部模型字段
        :param no_total: 是否跳过统计总数
        :param field_mappings: 关联字段映射字典，格式 {'alias': 'relation.column'}
        :return: (结果列表[dict], 总数int)
        """
        start = time.perf_counter()
        if field_mappings is None:
            field_mappings = {}

        try:
            # 解析时间过滤
            filters = {}
            start_time = params.get('startTime')
            end_time = params.get('endTime')
            if start_time:
                filters['start_time'] = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if end_time:
                filters['end_time'] = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

            # 准备查询字段列表
            columns = []

            if fields:
                for f in fields:
                    col = getattr(model, f, None)
                    if col is None:
                        raise ValueError(f"字段 '{f}' 在模型 {model.__name__} 中不存在")
                    columns.append(col)
            else:
                # 没指定fields，查询整个模型
                columns.append(model)

            joins = {}
            # 处理关联字段映射，动态添加join和字段
            for alias, path in field_mappings.items():
                relation, column_name = path.split('.')
                related_model = getattr(model, relation).property.mapper.class_
                joins[relation] = related_model
                columns.append(getattr(related_model, column_name).label(alias))

            # 创建查询对象，传入所有列
            query = self.db.query(*columns)

            # 加入关联join
            for relation, related_model in joins.items():
                query = query.join(related_model, getattr(model, relation))

            # 应用过滤条件
            query = self.apply_filters(query, model, params, filters, field_mappings, joins)

            # 排序
            if '_order' in params and '_by' in params:
                _order = params['_order']
                _by = params['_by']
                column = getattr(model, _by, None)
                if column is not None:
                    query = query.order_by(column.asc() if _order.lower() == 'asc' else column.desc())

            # 分页
            if '_start' in params and '_count' in params:
                query = query.offset(params['_start']).limit(params['_count'])

            # 执行查询
            result = query.all()
            # 处理结果
            if field_mappings and fields:
                result_dict = []
                for row in result:
                    # 用row_to_dict处理fields部分（row前len(fields)个元素）
                    main_dict = self.row_to_dict(row[:len(fields)], fields)
                    # 手动添加field_mappings部分（row后面的元素）
                    for idx, alias in enumerate(field_mappings):
                        val = row[len(fields) + idx]
                        if isinstance(val, datetime):
                            val = val.strftime("%Y-%m-%d %H:%M:%S")
                        main_dict[alias] = val
                    result_dict.append(main_dict)
            elif field_mappings:
                # 只有关联字段映射，row[0]是模型实例，其它是label字段
                result_dict = []
                for row in result:
                    base_dict = row[0].to_dict()
                    for alias in field_mappings:
                        val = getattr(row, alias)
                        if isinstance(val, datetime):
                            val = val.strftime("%Y-%m-%d %H:%M:%S")
                        base_dict[alias] = val
                    result_dict.append(base_dict)
            elif fields:
                # 只有fields，row是字段元组
                result_dict = [self.row_to_dict(row, fields) for row in result]
            else:
                # 返回完整模型实例
                result_dict = [item.to_dict() for item in result]
            cost = time.perf_counter() - start
            logger.info(f"FETCH_ALL_BY 查询SQL：{query.statement.compile(compile_kwargs={'literal_binds': True})} ---耗时：{cost:.3f} s")
            # 统计总数（除非no_total为True）
            total = 0
            if not no_total:
                total_query = self.db.query(getattr(model, 'id')) 
                for relation, related_model in joins.items():
                    total_query = total_query.join(related_model, getattr(model, relation))
                total_query = self.apply_filters(total_query, model, params, filters, field_mappings, joins)
                logger.info(f"total_query SQL: {total_query.statement.compile(compile_kwargs={'literal_binds': True})}")
                total = total_query.count()
            
            cost = time.perf_counter() - start
            logger.info(f"FETCH_ALL_BY 结束 ---耗时：{cost:.3f} s")
            return result_dict, total

        except Exception as e:
            raise ValueError(f"查询失败: {str(e)}") from e
        
    def fetch_total_for_group_join(
        self,
        left_model,
        right_model,
        left_field: str,
        right_field: str,
        group_field: str,
        filters: dict
    ):
        """
        通用的 join 聚合查询：统计 right_model 在 join 关系中按 group_field 分组后的数量。
    
        示例用途：
        - 统计 Spectrum 在 Plate → Project 的 join 中，按 project_id 分组的数量。
    
        参数说明：
        - left_model: 中间表（如 Plate）
        - right_model: 实际目标数据表（如 Spectrum）
        - left_field: join 中 left_model 的字段名（如 'id'）
        - right_field: join 中 right_model 的字段名（如 'plate_id'）
        - group_field: 用于分组的字段名（如 'project_id'，应是 left_model 的字段）
        - filters: 过滤条件，作用于 left_model（如 {'project_id': [...]}）
    
        返回：
        - dict: {group_field_value: count}
        """
        try:
            # 获取列对象
            left_field_col = getattr(left_model, left_field)
            right_field_col = getattr(right_model, right_field)
            group_field_col = getattr(left_model, group_field)
    
            # 构造基础 join 查询
            q = self.db.query(group_field_col, func.count(right_field_col)) \
                .join(right_model, right_field_col == left_field_col)
    
            # 添加过滤条件（作用于 left_model）
            for field, value in filters.items():
                column = getattr(left_model, field)
                if isinstance(value, list):
                    q = q.filter(column.in_(value))
                else:
                    q = q.filter(column == value)
    
            # 分组并执行查询
            q = q.group_by(group_field_col)
            return {k: v for k, v in q.all()}
    
        except Exception as e:
            raise ValueError(f"聚合查询失败: {str(e)}") from e


    def fetch_by_fields(self, model, conditions, fields=None):
        """
        根据多个字段的值查询，只有id支持批量in查询，其他字段为等于查询。

        :param model: SQLAlchemy 模型类
        :param conditions: 查询条件字典，如 {'id': [...], 'status': 'active', '_order': 'desc', '_by': 'time'}
        :param fields: 要查询的字段列表，None 表示返回所有字段
        :return: 结果列表（每项为 dict）
        """
        start = time.perf_counter()
        if not conditions:
            return []

        try:
            # 选择字段
            if fields:
                column_objs = []
                for f in fields:
                    col = getattr(model, f, None)
                    if col is None:
                        raise ValueError(f"字段 '{f}' 不存在于模型 {model.__name__}")
                    column_objs.append(col)
                query = self.db.query(*column_objs)
            else:
                query = self.db.query(model)

            # 先提取排序参数（从conditions取并删除）
            _order = conditions.pop('_order', None)
            _by = conditions.pop('_by', None)

            # 构建查询条件
            for field, value in conditions.items():
                if value is None:
                    continue
                column_attr = getattr(model, field, None)
                if column_attr is None:
                    # 字段不存在，跳过不报错
                    continue

                if field == 'id':
                    # id字段支持批量查询
                    if isinstance(value, (list, tuple, set)):
                        query = query.filter(column_attr.in_(value))
                    else:
                        query = query.filter(column_attr == value)
                else:
                    # 其他字段只支持等于查询（单值）
                    if isinstance(value, (list, tuple, set)):
                        # 如果传入列表，取第一个，避免in_（你也可以改成抛错或其他逻辑）
                        value = next(iter(value))
                    query = query.filter(column_attr == value)

            # 排序
            if _by:
                col = getattr(model, _by, None)
                if col is not None:
                    if _order and _order.lower() == 'desc':
                        query = query.order_by(col.desc())
                    else:
                        query = query.order_by(col.asc())

            result = query.all()
            cost = time.perf_counter() - start
            logger.info(f"FETCH_BY_FIELDS 查询SQL：{query.statement.compile(compile_kwargs={'literal_binds': True})} ---耗时：{cost:.3f} s")

            # 转换结果
            if fields:
                return [self.row_to_dict(row, fields) for row in result]
            else:
                return [item.to_dict() for item in result]

        except Exception as e:
            raise ValueError(f"fetch_by_fields 查询失败: {str(e)}") from e


    def insert_data(self, model, data,check_id=True):
        try:
            if 'id' not in data and check_id:
                data['id'] = str(uuid.uuid4())
            obj = model(**data)
            self.db.add(obj)
            self.db.commit()
            return data['id'] if check_id else None
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"插入失败: {str(e)}") from e
        
    def insert_many(self, model, data_list):
        try:
            objects = []
            for data in data_list:
                if 'id' not in data:
                    data['id'] = str(uuid.uuid4())
                obj = model(**data)
                objects.append(obj)
            self.db.bulk_save_objects(objects)
            self.db.commit()
            return [d['id'] for d in data_list]
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"批量插入失败: {str(e)}") from e
        
    def fetch_batch_insert(self, table_name, column_list, data):
        """
        用 SQLAlchemy 批量插入数据到 MySQL。
        :param table_name: 表名字符串
        :param column_list: 列名列表
        :param data: 列数据列表，元素可以是单值或列表，长度必须一致
        :return: 插入的行数
        """
        try:
            if len(column_list) != len(data):
                raise ValueError(f"字段数与数据长度不匹配: {len(column_list)} vs {len(data)}")

            # 计算批量插入条数（取列表长度）
            row_count = None
            for item in data:
                if isinstance(item, (list, tuple)):
                    if row_count is None:
                        row_count = len(item)
                    elif row_count != len(item):
                        raise ValueError("所有数组长度必须一致")
            
            if row_count is None:
                # 全是单值，单条插入
                row_count = 1
                data_rows = [dict(zip(column_list, data))]
            else:
                # 构造多条记录
                data_rows = []
                for i in range(row_count):
                    row = {}
                    for col_idx, col in enumerate(column_list):
                        val = data[col_idx]
                        if isinstance(val, (list, tuple)):
                            row[col] = val[i]
                        else:
                            row[col] = val
                    data_rows.append(row)

            metadata = MetaData(bind=self.db.bind)
            table = Table(table_name, metadata, autoload_with=self.db.bind)

            with self.db.begin():
                self.db.execute(table.insert(), data_rows)

            return row_count

        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"MySQL批量插入失败: {e}")

    def update_by_id(self, model, data):
        try:
            if 'id' not in data:
                raise ValueError("更新数据必须包含'id'")
            obj = self.db.query(model).filter(model.id == data['id']).first()
            if not obj:
                raise ValueError("未找到对应数据")
            for key, value in data.items():
                setattr(obj, key, value)
            self.db.commit()
            return obj
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"更新失败: {str(e)}") from e
        
    def update_by_conditions(self, model, data: dict, conditions: dict):
        """
        根据条件更新指定模型表的数据。
        :param model: SQLAlchemy 模型类
        :param data: 需要更新的字段字典，例如 {"name": "new_name"}
        :param conditions: 查询条件字典，例如 {"status": "active", "type": "A"}
        :return: 更新的行数
        """
        try:
            query = self.db.query(model)
    
            # 构建 WHERE 条件
            for key, value in conditions.items():
                column = getattr(model, key, None)
                if column is None:
                    raise ValueError(f"条件字段 '{key}' 在模型 {model.__name__} 中不存在")
                query = query.filter(column == value)
    
            # 执行更新
            update_count = query.update(data, synchronize_session=False)
            self.db.commit()
            return update_count
    
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"条件更新失败: {str(e)}") from e

    def delete_by_conditions(self, model, filters: dict, safe_mode=True):
        try:
            query = self.db.query(model)
            for key, value in filters.items():
                column = getattr(model, key, None)
                if column is not None:
                    query = query.filter(column == value)

            if safe_mode and query.count() > 1:
                raise ValueError("匹配记录不唯一，删除操作被拒绝。")

            query.delete()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"删除失败: {str(e)}") from e
        
    def delete_by_ids_batch(self, model, ids: list, batch_size=1000):
        """
        根据 id 列表批量删除记录，支持分批执行，避免 SQL 太长。
        
        :param model: SQLAlchemy 模型类
        :param ids: 要删除的 id 列表
        :param batch_size: 每批删除数量，默认 1000
        :return: 删除的总行数
        """
        total_deleted = 0
        try:
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                deleted_count = self.db.query(model)\
                                       .filter(model.id.in_(batch_ids))\
                                       .delete(synchronize_session=False)
                total_deleted += deleted_count
                self.db.commit()
            return total_deleted
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"批量删除失败: {str(e)}") from e
        
    def fetch_total_by(self, model, params):
        try:
            query = self.db.query(func.count(model.id))

            for key, value in params.items():
                if key.startswith('%'):
                    raw_key = key[1:]
                    column = getattr(model, raw_key, None)
                    if column is not None:
                        query = query.filter(column.like(f"%{value}%"))
                else:
                    column = getattr(model, key, None)
                    if column is not None:
                        query = query.filter(column == value)

            total = query.scalar()
            return total
        except Exception as e:
            raise ValueError(f"fetch_total_by 失败: {str(e)}") from e
        
    def fetch_field_total_for_group(self, model, group_field, count_field='id', filters=None):
        """
        获取指定 group_field 分组后 count_field 的计数结果（MySQL 版本）

        :param model: SQLAlchemy 模型类
        :param group_field: 分组字段名（字符串）
        :param count_field: 计数字段名，默认 'id'
        :param filters: 可选的过滤条件 dict
        :return: {group_value: count, ...}
        """
        try:
            group_col = getattr(model, group_field)
            count_col = getattr(model, count_field) if count_field != '*' else '*'

            query = self.db.query(group_col, func.count(count_col).label("total")).group_by(group_col)

            if filters:
                for key, value in filters.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, (list, tuple)):
                            query = query.filter(column.in_(value))
                        else:
                            query = query.filter(column == value)

            rows = query.all()
            return {getattr(row, group_field): row.total for row in rows}

        except Exception as e:
            raise ValueError(f"fetch_field_total_for_group 失败: {str(e)}") from e
        
    def get_unique_name(self, model, base_name, project_id):
        """
        获取指定 project_id 下唯一的 name 名称，自动避免冲突
        """
        try:
            # 检查基础名称是否存在
            count = self.fetch_total_by(model, {
                "name": base_name,
                "project_id": project_id
            })
            if count == 0:
                return base_name

            # 若存在，递增查找 base_name(1), base_name(2), ...
            index = 1
            while True:
                new_name = f"{base_name}({index})"
                count = self.fetch_total_by(model, {
                    "name": new_name,
                    "project_id": project_id
                })
                if count == 0:
                    return new_name
                index += 1

        except Exception as e:
            raise ValueError(f"get_unique_name: {str(e)}") from e
        
    def fetch_nearest_by_time(self, model, plate_id, target_time_str, max_minutes=30, limit_count=20,
                          fields=None, time_field_name=None, field_mappings=None):
        """
        查询给定 plate_id 下 used=1 的记录中，指定时间字段 target_time 附近（±max_minutes）最近的若干条记录。
    
        :param model: SQLAlchemy 模型类
        :param plate_id: plate_id 值
        :param target_time_str: 目标时间字符串（格式: '%Y-%m-%d %H:%M:%S' 或 '%Y/%m/%d %H:%M'）
        :param max_minutes: 前后时间范围（分钟）
        :param limit_count: 返回数量
        :param fields: 指定返回字段列表，None 表示返回全字段
        :param time_field_name: 比较用的时间字段，None 表示使用 self.default_time_field
        :param field_mappings: 关联字段映射字典，格式 {'alias': 'relation.column'}
        :return: (结果列表[dict], 总数int)
        """
        try:
            # 解析时间字符串
            if "/" in target_time_str:
                target_time = datetime.strptime(target_time_str, "%Y/%m/%d %H:%M")
            else:
                target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")
    
            start_time = target_time - timedelta(minutes=max_minutes)
            end_time = target_time + timedelta(minutes=max_minutes)
    
            time_field_name = time_field_name or self.default_time_field
            time_field = getattr(model, time_field_name, None)
            if time_field is None:
                raise ValueError(f"模型 {model.__name__} 中找不到字段 '{time_field_name}'")
    
            if not hasattr(model, "used"):
                raise ValueError(f"模型 {model.__name__} 中缺少 'used' 字段")
    
            columns = []
            joins = {}
            if fields:
                for f in fields:
                    col = getattr(model, f, None)
                    if col is None:
                        raise ValueError(f"字段 '{f}' 在模型 {model.__name__} 中不存在")
                    columns.append(col)
            else:
                columns.append(model)
    
            # 处理关联字段映射
            if field_mappings:
                for alias, path in field_mappings.items():
                    relation, col_name = path.split('.')
                    related_model = getattr(model, relation).property.mapper.class_
                    joins[relation] = related_model
                    columns.append(getattr(related_model, col_name).label(alias))
    
            # 构造查询
            query = self.db.query(*columns)
    
            # 加入关联 join
            for relation, related_model in joins.items():
                query = query.join(related_model, getattr(model, relation))
    
            # 添加过滤条件
            query = query.filter(
                model.plate_id == plate_id,
                time_field.between(start_time, end_time),
                model.used == 1
            )
    
            # 按时间差排序
            query = query.order_by(
                func.abs(
                    func.timestampdiff(
                        text("SECOND"),
                        time_field,
                        target_time
                    )
                )
            )
    
            # 限制返回条数
            query = query.limit(limit_count)
    
            result = query.all()
    
            # 处理返回结果
            if field_mappings and fields:
                result_list = []
                for row in result:
                    main_dict = self.row_to_dict(row[:len(fields)], fields)
                    for idx, alias in enumerate(field_mappings):
                        val = row[len(fields) + idx]
                        if isinstance(val, datetime):
                            val = val.strftime("%Y-%m-%d %H:%M:%S")
                        main_dict[alias] = val
                    result_list.append(main_dict)
            elif field_mappings:
                result_list = []
                for row in result:
                    base_dict = row[0].to_dict()
                    for alias in field_mappings:
                        val = getattr(row, alias)
                        if isinstance(val, datetime):
                            val = val.strftime("%Y-%m-%d %H:%M:%S")
                        base_dict[alias] = val
                    result_list.append(base_dict)
            elif fields:
                result_list = [self.row_to_dict(row, fields) for row in result]
            else:
                result_list = [item.to_dict() for item in result]
            result_list.sort(
                key=lambda x: datetime.strptime(x['time'], "%Y-%m-%d %H:%M:%S")
            )
            total_count = len(result_list)
            return result_list, total_count
    
        except Exception as e:
            raise ValueError(f"fetch_nearest_by_time 查询失败: {str(e)}") from e

    def fetch_nearest_by_time_same_round(self, model, plate_id, target_time_str,
                                         target_max_time=10, max_minutes=30,
                                         limit_count=20, fields=None,
                                         time_field_name=None, field_mappings=None):
        """
        查询同一轮次内最近的记录。

        1. 找最近一条记录，如果和 target_time 差 > target_max_time 秒 → 返回空
        2. 根据最近记录的 round_num 限定在同一轮次内，再取 ±max_minutes 最近的 limit_count 条记录。
        """
        try:
            # 解析目标时间
            if "/" in target_time_str:
                target_time = datetime.strptime(target_time_str, "%Y/%m/%d %H:%M")
            else:
                target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")

            time_field_name = time_field_name or self.default_time_field
            time_field = getattr(model, time_field_name, None)
            if time_field is None:
                raise ValueError(f"模型 {model.__name__} 中找不到字段 '{time_field_name}'")
            if not hasattr(model, "used") or not hasattr(model, "round_num"):
                raise ValueError(f"模型 {model.__name__} 缺少 'used' 或 'round_num' 字段")

            # ① 找最近一条记录
            nearest = (
                self.db.query(model)
                .filter(model.plate_id == plate_id, model.used == 1)
                .order_by(func.abs(func.timestampdiff(text("SECOND"), time_field, target_time)))
                .first()
            )
            if not nearest:
                return [], 0

            diff_sec = abs((nearest.time - target_time).total_seconds())
            if diff_sec > target_max_time * 60:
                return [], 0

            round_num = nearest.round_num

            # ② 在该轮次内查询
            start_time = target_time - timedelta(minutes=max_minutes)
            end_time = target_time + timedelta(minutes=max_minutes)

            query = self.db.query(*([model] if not fields else [
                getattr(model, f) for f in fields
            ]))

            if field_mappings:
                for alias, path in field_mappings.items():
                    relation, col_name = path.split('.')
                    related_model = getattr(model, relation).property.mapper.class_
                    query = query.join(related_model, getattr(model, relation))
                    query = query.add_columns(getattr(related_model, col_name).label(alias))

            query = (
                query.filter(
                    model.plate_id == plate_id,
                    model.round_num == round_num,
                    model.used == 1,
                    time_field.between(start_time, end_time)
                )
                .order_by(func.abs(func.timestampdiff(text("SECOND"), time_field, target_time)))
                .limit(limit_count)
            )

            result = query.all()

            # 格式化输出（保持和原方法一致）
            if field_mappings and fields:
                result_list = []
                for row in result:
                    main_dict = self.row_to_dict(row[:len(fields)], fields)
                    for idx, alias in enumerate(field_mappings):
                        val = row[len(fields) + idx]
                        if isinstance(val, datetime):
                            val = val.strftime("%Y-%m-%d %H:%M:%S")
                        main_dict[alias] = val
                    result_list.append(main_dict)
            elif field_mappings:
                result_list = []
                for row in result:
                    base_dict = row[0].to_dict()
                    for alias in field_mappings:
                        val = getattr(row, alias)
                        if isinstance(val, datetime):
                            val = val.strftime("%Y-%m-%d %H:%M:%S")
                        base_dict[alias] = val
                    result_list.append(base_dict)
            elif fields:
                result_list = [self.row_to_dict(row, fields) for row in result]
            else:
                result_list = [item.to_dict() for item in result]

            result_list.sort(key=lambda x: datetime.strptime(x['time'], "%Y-%m-%d %H:%M:%S"))
            return result_list, len(result_list)

        except Exception as e:
            raise ValueError(f"fetch_nearest_by_time_same_round 查询失败: {str(e)}") from e