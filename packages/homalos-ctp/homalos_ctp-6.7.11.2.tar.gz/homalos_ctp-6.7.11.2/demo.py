#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName   : demo.py
@Date       : 2025/9/2 15:13
@Author     : Donny
@Email      : donnymoving@gmail.com
@Software   : PyCharm
@Description: md demo
"""
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

from ctp.api import MdApi


class CtpMdApi(MdApi):

    def __init__(self) -> None:
        super().__init__()

        self.req_id: int = 0  # 请求ID
        self.subscribe_symbol: set = set()  # 已订阅的合约

        self.address: str = ""      # 服务器地址
        self.userid: str = ""       # 用户名
        self.password: str = ""     # 密码
        self.broker_id: str = ""    # 经纪公司代码

        self.login_status: bool = False
        self.connect_status: bool = False

        self.current_date = datetime.now().strftime("%Y%m%d")

    def onFrontConnected(self) -> None:
        """
        服务器连接成功回报
        :return:
        """
        print("CTP行情API回调: onFrontConnected")
        print("开始登录流程")
        self.login()

    def onFrontDisconnected(self, reason: int) -> None:
        """
        行情服务器连接断开回报
        当客户端与交易托管系统通信连接断开时，该方法被调用。
        当发生这个情况后，API会自动重新连接，客户端可不做处理。
        自动重连地址，可能是原来注册的地址，也可能是系统支持的其它可用的通信地址，它由程序自动选择。
        注:重连之后需要重新认证、登录
        :param reason: 错误代号，连接断开原因，为10进制值，因此需要转成16进制后再参照下列代码：
                0x1001 网络读失败
                0x1002 网络写失败
                0x2001 接收心跳超时
                0x2002 发送心跳失败
                0x2003 收到错误报文
        :return: 无
        :param reason:
        :return:
        """
        # 解析断开原因
        reason_hex = hex(reason)
        reason_mapping = {
            0x1001: "网络读失败",
            0x1002: "网络写失败",
            0x2001: "接收心跳超时",
            0x2002: "发送心跳失败",
            0x2003: "收到错误报文"
        }
        reason_msg = reason_mapping.get(reason, f"未知原因({reason_hex})")

        print(f"行情服务器连接断开，原因：{reason_msg} ({reason_hex})")

    def onRspUserLogin(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """用户登录请求回报（修复版本）"""
        if error["ErrorID"] == 0:
            print("CTP行情API回调: onRspUserLogin - 行情服务器登录成功")
            self.login_status = True

            # 更新日期
            self.update_date()
        else:
            print(f"行情服务器登录失败: ErrorID={error.get('ErrorID', '')}, ErrorMsg={error.get('ErrorMsg', '')}")


    def onRspError(self, error: dict, reqid: int, last: bool) -> None:
        """
        请求报错回报
        :param error:
        :param reqid:
        :param last:
        :return:
        """
        print(f"CTP行情API回调: onRspError - 请求报错, ErrorID={error.get('ErrorID', '')}, ErrorMsg={error.get('ErrorMsg', '')}")
        print("行情接口报错", error)

    def onRspSubMarketData(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """订阅行情回报
        :param data:
        :param error:
        :param reqid:
        :param last:
        :return:
        """
        symbol = data.get("InstrumentID", "UNKNOWN")
        print(f"CTP行情API回调: onRspSubMarketData - 订阅回报, 合约={symbol}, ErrorID={error.get('ErrorID', 'N/A') if error else 'None'}")
        if not error or not error["ErrorID"]:
            # 订阅成功
            if data and "InstrumentID" in data:
                symbol = data["InstrumentID"]
                print(f"symbol: {symbol}")
        else:
            print(f"行情订阅失败: {error}")

    def onRtnDepthMarketData(self, data: dict) -> None:
        """
        行情数据推送
        :param data:
        :return:
        """
        print("onRtnDepthMarketData")
        # 获取合约代码用于日志记录
        symbol: str = data.get("InstrumentID", "UNKNOWN")

        print(f"CTP行情数据接收: {symbol} @ {data.get('UpdateTime', 'N/A')} 价格={data.get('LastPrice', 'N/A')}")

        # 过滤没有时间戳的异常行情数据
        if not data["UpdateTime"]:
            print(f"跳过无时间戳的行情数据: {symbol}")
            return

    def connect(self, address: str, userid: str, password: str, broker_id: str) -> None:
        """
        连接服务器
        :param address:
        :param userid:
        :param password:
        :param broker_id:
        :return:
        """
        self.address = address
        self.userid = userid
        self.password = password
        self.broker_id = broker_id

        is_using_udp = False  # 是否使用UDP行情
        is_multicast = False  # 是否使用组播行情(组播行情只能在内网中使用，需要咨询所连接的系统是否支持组播行情。)
        is_production_mode = True  # 选在连接的是生产还是评测前置，True:使用生产版本的API False:使用测评版本API

        ctp_con_dir: Path = Path.cwd().joinpath("con")

        if not ctp_con_dir.exists():
            ctp_con_dir.mkdir()

        api_path_str = str(ctp_con_dir) + "\\md"
        print("CtpMdApi：尝试创建路径为 {} 的 API".format(api_path_str))
        try:
            self.createFtdcMdApi(api_path_str.encode("GBK").decode("utf-8"), is_using_udp, is_multicast,
                                 is_production_mode)  # 加上utf-8编码，否则中文路径会乱码
            print("CtpMdApi：createFtdcMdApi调用成功。")

        except Exception as e_create:
            print("CtpMdApi：createFtdcMdApi 失败！错误：{}".format(e_create))
            print("CtpMdApi：createFtdcMdApi 回溯：{}".format(traceback.format_exc()))
            return

        self.registerFront(address)
        print("CtpMdApi：尝试使用地址初始化 API：{}...".format(address))
        try:
            self.init()
            print("CtpMdApi：init 调用成功。")
            self.connect_status = True
        except Exception as e_init:
            print("CtpMdApi：初始化失败！错误：{}".format(e_init))
            print("CtpMdApi：初始化回溯：{}".format(traceback.format_exc()))
            return

    def login(self) -> None:
        """
        用户登录
        :return:
        """
        ctp_req: dict = {
            "UserID": self.userid,
            "Password": self.password,
            "BrokerID": self.broker_id
        }

        self.req_id += 1
        self.reqUserLogin(ctp_req, self.req_id)

    def subscribe(self, symbol: str) -> None:
        """
        订阅行情
        :return:
        """
        print(f"CTP行情API: 准备订阅合约 {symbol}")

        # 过滤重复的订阅
        if symbol in self.subscribe_symbol:
            print(f"合约 {symbol} 已在订阅列表中，跳过重复订阅")
            return

        if self.login_status:
            print(f"CTP行情API: 发送订阅请求 {symbol}")
            result = self.subscribeMarketData(symbol)
            print(f"CTP行情API: 订阅请求已发送 {symbol}, 返回值={result}")
        else:
            print(f"CTP行情API: 未登录，无法订阅 {symbol}")
        self.subscribe_symbol.add(symbol)

    def close(self) -> None:
        """
        关闭连接
        :return:
        """
        if self.connect_status:
            self.connect_status = False
            self.exit()

    def update_date(self) -> None:
        """
        更新当前日期
        :return:
        """
        self.current_date = datetime.now().strftime("%Y%m%d")


class MarketData(object):
    def __init__(self):
        # CTP API相关
        self.md_api: CtpMdApi | None = None

    @staticmethod
    def _prepare_address(address: str) -> str:
        """
        如果没有方案，则帮助程序会在前面添加 tcp:// 作为前缀。
        :param address:
        :return:
        """
        if not any(address.startswith(scheme) for scheme in ["tcp://", "ssl://", "socks://"]):
            return "tcp://" + address
        return address

    def connect(self, setting: dict[str, Any]) -> None:
        """连接CTP服务器"""
        try:
            print("开始连接CTP行情服务器...")
            print(f"setting: {setting}")

            # 兼容性配置字段处理
            user_id = setting.get("user_id", "")
            password = setting.get("password", "")
            broker_id = setting.get("broker_id", "")
            md_address_raw = setting.get("md_address", "")

            # 参数验证
            if not all([user_id, password, broker_id, md_address_raw]):
                raise ValueError("缺少必要的连接参数")

            # 创建API实例
            if not self.md_api:
                self.md_api = CtpMdApi()

            md_address: str = self._prepare_address(md_address_raw)
            self.md_api.connect(md_address, user_id, password, broker_id)

            print(f"正在连接到 {md_address}...")

        except Exception as e:
            print(f"连接失败: {e}")
            if self.md_api:
                self.md_api.close()

    def subscribe(self, symbol: str) -> None:
        """订阅合约行情"""
        if self.md_api:
            self.md_api.subscribe(symbol)
        else:
            print("行情API未连接，无法订阅")

    def close(self) -> None:
        """关闭连接"""
        if self.md_api:
            self.md_api.close()
            self.md_api = None


if __name__ == '__main__':
    import time
    
    # CTP配置（使用SimNow测试环境）
    ctp_config = {
        "user_id": "",  # 用户名
        "password": "",  # 密码
        "broker_id": "9999",  # 经纪商代码
        "md_address": "tcp://182.254.243.31:30011",  # 行情服务器地址
        # "md_address": "tcp://182.254.243.31:40011",  # 行情服务器地址
        "appid": "simnow_client_test",
        "auth_code": "0000000000000000"
    }
    
    market = MarketData()
    market.connect(setting=ctp_config)
    
    # 等待连接和登录完成
    print("等待连接和登录完成...")
    time.sleep(3)
    
    # 订阅一些常用的期货合约（SimNow模拟环境中的活跃合约）
    contracts_to_subscribe = [
        "SA601",
        "FG601"
    ]

    # 订阅合约的tick数据
    subscribe_count = 0
    
    print(f"开始订阅 {len(contracts_to_subscribe)} 个合约...")
    for contract in contracts_to_subscribe:
        print(f"订阅合约: {contract}")
        market.subscribe(contract)
        subscribe_count += 1
        time.sleep(1)  # 避免订阅请求过快

    print(f"已订阅 {subscribe_count} 个合约")
    print("订阅完成，等待行情数据...")
    print("程序将运行60秒来接收行情数据，按Ctrl+C可提前退出")
    
    try:
        # 保持程序运行60秒来接收行情数据
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n用户中断程序")
    finally:
        print("关闭连接...")
        market.close()
        print("程序结束")
