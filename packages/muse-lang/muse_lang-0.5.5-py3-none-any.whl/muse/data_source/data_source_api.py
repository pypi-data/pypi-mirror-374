from muse.data_source.base import DataSourceInterface
from muse.data_source.ds_utils import filter_ports, filter_ports_sec, convert_decimal_to_float, get_all_unique_fields
import polars as pl
import os
from muse.utils.jx_http_request import JxHttpClient
from collections import OrderedDict
from muse.muse_config import DATA_PATH, MID_BASE_URL

class DataSourceApi(DataSourceInterface):
    data_locate = DATA_PATH

    MID_URL_HOST = "http://jixu.asuscomm.com"

    def get_datasource_name(self):
        return '指标库数据源'

    def get_repository_list(self):
        rep_path = self.data_locate + '指标库/'
        filenames = []
        for filename in os.listdir(rep_path):
            # 确保是文件而不是子目录
            if os.path.isfile(os.path.join(rep_path, filename)):
                # 分割文件名和扩展名
                name_without_ext = os.path.splitext(filename)[0]
                filenames.append(name_without_ext)
        return filenames

    def get_repository_metadata(self, repository_name):
        rep_locate = f'{self.data_locate}指标库/{repository_name}.xlsx'
        if not os.path.exists(rep_locate):
            return {}
        # 选择合适的指标
        metadata = dict()
        metadata['指标库名称'] = repository_name

        df = pl.read_excel(rep_locate)
        # 指标描述需要额外获取，描述应包含所有枚举值信息; 指标类型信息
        ind_list = [{'指标名称': ind, '指标描述': ind, '指标类型': 'string'} for ind in df.columns]
        metadata['指标列表'] = ind_list
        # 每个指标库都应该一样的部分
        params = {
                    'port_ids': {'参数描述': '产品代码列表', '参数类型': 'list'},
                    'port_tags': {'参数描述': '产品标签列表', '参数类型': 'list'},
                    'asset_tags': {'参数描述': '资产标签列表', '参数类型':'list'},
                    'start_date': {'参数描述': '查询开始日期', '参数类型': 'date'},
                    'end_date': {'参数描述': '查询结束日期', '参数类型': 'data'}
                  }
        # 每个指标库不一样的部分放到下面填补
        metadata['参数列表'] = params
        return metadata

    from collections import OrderedDict

    def get_all_repository_metadata(self):
        jxClient = JxHttpClient(MID_BASE_URL)
        original_data_list = jxClient.get("/xlsApiPlugin/loadMuseInds?topics=API指标库")

        if not original_data_list:
            return []  # 如果没有数据，返回空列表

        transformed_data_list = []  # 存储所有转换后的指标库

        # 循环处理每一个指标库
        for original_data in original_data_list:
            transformed_data = OrderedDict()

            # 转换基本信息
            transformed_data['指标库名称'] = original_data['apiName']
            transformed_data['指标库描述'] = original_data['apiDesc']

            # 转换参数列表
            transformed_data['参数列表'] = {}
            for param_key, param_value in original_data['apiParamMap'].items():
                transformed_param = {
                    '参数描述': param_value['apiParamName'],
                    '参数类型': param_value['apiParamType']
                }
                transformed_data['参数列表'][param_key] = transformed_param

            if 'PORT_IDS' in transformed_data['参数列表']:
                PORT_TAGS_PARAMS = {
                    '参数描述': '逗号分隔的产品标签列表',
                    '参数类型': 'String'
                }
                transformed_data['参数列表']['PORT_TAGS'] = PORT_TAGS_PARAMS

            if 'SEC_IDS' in transformed_data['参数列表']:
                SEC_TAGS_PARAMS = {
                    '参数描述': '逗号分隔的资产标签列表',
                    '参数类型': 'String'
                }
                transformed_data['参数列表']['SEC_TAGS'] = SEC_TAGS_PARAMS

            # 转换指标列表
            transformed_data['指标列表'] = []
            for indicator in original_data['indList']:
                ind_name = indicator['indName']
                ind_desc = indicator['indDesc']
                if ind_name == '产品代码':
                    ind_desc = '理财产品的系统唯一标识码，指标库重要关联指标'
                elif ind_name == '资产代码' or ind_name == '证券代码':
                    ind_desc = '理财产品投资的金融资产的系统唯一标识码, 指标库重要关联指标'
                elif ind_name == '统计日期':
                    ind_desc = '表示数据统计日期, 指标库重要关联指标。数据表示为YYYY-mm-dd的日期字符串'

                transformed_indicator = {
                    '指标名称': ind_name,
                    '指标描述': ind_desc
                }
                transformed_data['指标列表'].append(transformed_indicator)

            transformed_data_list.append(transformed_data)

        return transformed_data_list  # 返回转换后的列表

    def get_basic_inds(self):
        return ['资产代码', '资产名称', '资产标签', '产品代码', '产品简称', '产品标签', '主体代码', '主体名称', '主体标签', '日期']

    def get_port_tags(self):
        # tags = pl.read_excel(self.data_locate + '产品标签列.xlsx')
        jxClient = JxHttpClient(self.MID_URL_HOST + ":9084")
        port_targs_params = {
            "classCode": 80,
            "grpName": "限额指标产品标签组",
            "curUser": {
                "realName": "系统管理员",
                "userName": "padmin",
                "orgCode": "BM0008"
            }
        }
        rst = jxClient.post("/labelSystem/getLabelCloud", data=port_targs_params)
        rst_list = [item['typeName'] for item in rst if item['count'] > 0]
        return rst_list

    def get_port_inds(self):
        inds = pl.read_excel(self.data_locate + '产品指标列.xlsx')
        return inds.columns

    def get_asset_tags(self):
        # tags = pl.read_excel(self.data_locate + '资产标签列.xlsx')
        # tags = pl.read_excel(self.data_locate + '产品标签列.xlsx')
        jxClient = JxHttpClient(self.MID_URL_HOST + ":9084")
        port_targs_params = {
            "classCode": 81,
            "grpName": "压测标签组",
            "curUser": {
                "realName": "系统管理员",
                "userName": "padmin",
                "orgCode": "BM0008"
            }
        }
        rst = jxClient.post("/labelSystem/getLabelCloud", data=port_targs_params)
        rst_list = [item['typeName'] for item in rst if item['count'] > 0]
        return rst_list

    def get_asset_inds(self):
        inds = pl.read_excel(self.data_locate + '资产指标列.xlsx')
        return inds.columns

    def get_data(self, run_method: str, data_subject: str, sec_ids: list = [], port_ids: list = [], tags: list = [],
                 inds: list = [], start_date=None, end_date=None, penetrate=None):
        if penetrate:
            penetrate = '全穿透'
        else:
            penetrate = '不穿透'
        pdf = None

        if data_subject == '持仓指标':
            asset_df = pl.read_excel(self.data_locate + '资产指标汇总.xlsx')
            asset_tags = pl.read_excel(self.data_locate + '资产标签.xlsx')
            asset_df = asset_df.join(asset_tags, on=['资产代码'], how='left')
            pdf = filter_ports_sec(pdf=asset_df, port_ids=port_ids, sec_ids=sec_ids, start_date=start_date,
                                   end_date=end_date)
            # 获得产品代码
            port_ids = pdf.select("产品代码").unique().to_series().to_list()
            ports = pl.read_excel(self.data_locate + '产品指标汇总.xlsx')
            port_tags = pl.read_excel(self.data_locate + '产品标签.xlsx')
            ports = ports.join(port_tags, on=['产品代码'], how='left')
            ports = filter_ports(pdf=ports, port_ids=port_ids, start_date=start_date, end_date=end_date)
            # 合并资产和产品
            pdf = pdf.join(ports, on=['产品代码', '日期'], how='left')
            pdf = convert_decimal_to_float(pdf)
        elif data_subject == '产品指标':
            ports = pl.read_excel(self.data_locate + '产品指标汇总.xlsx')
            port_tags = pl.read_excel(self.data_locate + '产品标签.xlsx')
            ports = ports.join(port_tags, on=['产品代码'], how='left')
            pdf = filter_ports_sec(pdf=ports, port_ids=port_ids, start_date=start_date, end_date=end_date)

        merged_cols = tags + inds
        if len(merged_cols) > 0:
            all_cols = get_all_unique_fields(merged_cols, self.get_basic_inds())
            existing_cols = [c for c in all_cols if c in pdf.columns]
            pdf = pdf.select(existing_cols)
        return pdf

    # 根据标签获取id列表
    def get_ids_by_tags(self, tags: list = [], tag_grps = []):
        tag_grps_list = ["限额指标产品标签组","压测标签组"]
        if tag_grps:
            tag_grps_list = tag_grps

        port = '9084'
        api_params = {
            "grpNames": tag_grps_list,
            "labelNames": tags
        }

        MID_URL = self.MID_URL_HOST + ":" + port
        jxClient = JxHttpClient(MID_URL)
        rst = jxClient.post("/labelSystem/getIdsByLabelName", data=api_params)
        return rst

    def get_repository_inds(self, run_method: str, repository: str, ind_list: list, params: dict):
        # 设置端口映射
        port_mapping = {
            '中邮.': ('', '9084'),
            '华夏.': ('', '9083'),
            '几许.': ('', '9083')
        }

        # 处理仓库前缀和端口
        for prefix, (replace_str, port_num) in port_mapping.items():
            if repository.startswith(prefix):
                repository = repository.replace(prefix, replace_str)
                port = port_num
                break
        else:
            port = '9084'  # 默认端口

        # 基础API参数
        api_params = {
            "resource": repository,
            "paramMaps": {"SYS_ID": ""},
            "ind_name_list": ind_list,
            "pageSize": 1000000,
            "pageNum": 1,
            "curUser": {"userName": "test001"}
        }

        # 处理日期参数, 如果传入了小写的，则转成大写
        date_mapping = {
            'start_date': 'START_DATE',
            'end_date': ['END_DATE', 'DATA_DATE']
        }

        for src_key, dest_keys in date_mapping.items():
            if src_key in params:
                value = params.pop(src_key)
                if value:
                    # 统一将目标键转换为列表处理
                    target_keys = dest_keys if isinstance(dest_keys, list) else [dest_keys]
                    for target_key in target_keys:
                        params[target_key] = value

        ### ---------- 处理 port_ids ---------- 开始
        port_ids = []
        if 'port_ids' in params:
            port_ids_param = params.pop('port_ids', '')
            # 处理逗号分隔的字符串，转换为列表
            if isinstance(port_ids_param, str):
                port_ids = [item.strip() for item in port_ids_param.split(',') if item.strip()]
            elif isinstance(port_ids_param, list):
                port_ids = port_ids_param

        # 再处理 port_tags
        if 'PORT_TAGS' in params:
            port_tags = params.pop('PORT_TAGS')  # 使用 pop 移除参数
            # 处理逗号分隔的字符串，转换为列表
            if isinstance(port_tags, str):
                port_tags = [tag.strip() for tag in port_tags.split(',') if tag.strip()]

            if isinstance(port_tags, list) and port_tags:
                port_tags_ids = self.get_ids_by_tags(tags=port_tags)
                # 合并并去重
                if port_tags_ids:
                    port_ids = list(set(port_ids + port_tags_ids))

        if port_ids:
            params['PORT_IDS'] = ",".join(port_ids)
        ### ---------- 处理 port_ids ---------- 结束

        ### ---------- 处理 sec_ids ---------- 开始
        sec_ids = []
        if 'SEC_IDS' in params:
            sec_ids_param = params.pop('sec_ids', '')
            # 处理逗号分隔的字符串，转换为列表
            if isinstance(sec_ids_param, str):
                sec_ids = [item.strip() for item in sec_ids_param.split(',') if item.strip()]
            elif isinstance(sec_ids_param, list):
                sec_ids = sec_ids_param

        if 'SEC_TAGS' in params:
            sec_tags = params.pop('SEC_TAGS')  # 使用 pop 移除参数
            # 处理逗号分隔的字符串，转换为列表
            if isinstance(sec_tags, str):
                sec_tags = [tag.strip() for tag in sec_tags.split(',') if tag.strip()]

            if isinstance(sec_tags, list) and sec_tags:
                sec_tags_ids = self.get_ids_by_tags(tags=sec_tags)
                if sec_tags_ids:
                    sec_ids = list(set(sec_ids + sec_tags_ids))

        if sec_ids:
            params['SEC_IDS'] = ",".join(sec_ids)
        ### ---------- 处理 sec_ids ---------- 结束

        api_params["paramMaps"] = {**api_params["paramMaps"], **params}
        # print(api_params)
        MID_URL = self.MID_URL_HOST + ":" + port
        jxClient = JxHttpClient(MID_URL)
        rst = jxClient.post("/xlsApiPlugin/museLoadData", data=api_params)
        # 提取列名
        column_names = [header['ind_name'] for header in rst['headers']]

        df = create_dataframe_safely(rst['datas'], column_names)
        # 转换为Polars DataFrame
        # df = pl.DataFrame(
        #     rst['datas'],
        #     schema=column_names,
        #     orient='row'
        # )
        return df

    def get_all_repository_params(self, rep_list: list):
        jxClient = JxHttpClient(MID_BASE_URL)
        params = jxClient.get(f"/museapi/getApiParamListByApiCodes?apiCodes={','.join(rep_list)}")
        return params


def create_dataframe_safely(data, schema):
    """安全创建DataFrame，处理混合数据类型问题"""
    # 方法1：先尝试正常创建
    try:
        return pl.DataFrame(data, schema=schema, orient='row', infer_schema_length=10000)
    except Exception as e:
        print(f"方法1失败: {e}")

    # 方法2：逐列构建
    data_dict = {}
    for col_idx, col_name in enumerate(schema):
        col_data = []
        for row in data:
            if col_idx < len(row):
                value = row[col_idx]
                # 统一数值类型
                if isinstance(value, (int, float)):
                    col_data.append(float(value))
                else:
                    col_data.append(value)
            else:
                col_data.append(None)
        data_dict[col_name] = col_data

    return pl.DataFrame(data_dict)

if __name__ == '__main__':
    ds = DataSourceApi()
    params={
        "START_DATE": "2022-01-05",
        "END_DATE": "2025-01-05",
        "SEC_IDS": "000001.SZ",
        "PORT_IDS": "2001JB0003",
        "BENCHMARK_ID": "399300_CNSESZ",
        "BENCHMARK_TYPE": "01"
    }
    # print(ds.get_repository_inds(run_method='', repository='产品每日估值汇总', ind_list=['产品代码','统计日期','当日份额','当日单位净值'], params=params))
    # print(ds.get_repository_inds(run_method='', repository='产品每日估值汇总', ind_list=['产品代码', '统计日期', '当日份额', '当日单位净值'], params=params))
    # print(ds.get_repository_inds(run_method='', repository='股票历史日线', ind_list=['股票代码', '交易日期', '开盘价', '收盘价','最高价','最低价','涨跌额'], params=params))

    # print(ds.get_repository_inds(run_method='', repository='几许.股票历史日线', ind_list=['股票代码', '交易日期', '开盘价', '收盘价', '最高价', '最低价', '涨跌额'], params=params))
    # print(ds.get_repository_inds(run_method='', repository='中邮.产品估值（时序）', ind_list=[], params=params))

    # rst = ds.get_all_repository_metadata()

    # 支持根据标签获取相关ID编号
    # ds = DataSourceApi()
    # rst = ds.get_ids_by_tags(tags = ['债券'])
    # rst = ds.get_ids_by_tags(tags=['AA+级同业存单'])
    rst = ds.get_asset_tags()
    print(rst)