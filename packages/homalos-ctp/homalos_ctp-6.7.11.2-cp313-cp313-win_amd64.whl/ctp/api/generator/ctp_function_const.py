#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName	: ctp_function_const.py
@Date		: 2025-09-03 14:41:07.155071
@Author		: Donny
@Email		: donnymoving@gmail.com
@Software	: PyCharm
@Description: homalos-ctp md和td基础函数名称文件， 不是 Req 和 On 开头的函数
"""


class CtpFunctionConst:
	# 原有函数名
	EXIT: str = "Exit"
	CREATE_FTDC_MD_API: str = "CreateFtdcMdApi"
	GET_API_VERSION: str = "GetApiVersion"
	RELEASE: str = "Release"
	INIT: str = "Init"
	JOIN: str = "Join"
	GET_TRADING_DAY: str = "GetTradingDay"
	REGISTER_FRONT: str = "RegisterFront"
	REGISTER_NAME_SERVER: str = "RegisterNameServer"
	REGISTER_FENS_USER_INFO: str = "RegisterFensUserInfo"
	REGISTER_SPI: str = "RegisterSpi"
	SUBSCRIBE_MARKET_DATA: str = "SubscribeMarketData"
	UN_SUBSCRIBE_MARKET_DATA: str = "UnSubscribeMarketData"
	SUBSCRIBE_FOR_QUOTE_RSP: str = "SubscribeForQuoteRsp"
	UN_SUBSCRIBE_FOR_QUOTE_RSP: str = "UnSubscribeForQuoteRsp"

	# 新增函数名
	CREATE_FTDC_TRADER_API: str = "CreateFtdcTraderApi"
	GET_FRONT_INFO: str = "GetFrontInfo"
	SUBSCRIBE_PRIVATE_TOPIC: str = "SubscribePrivateTopic"
	SUBSCRIBE_PUBLIC_TOPIC: str = "SubscribePublicTopic"
	REGISTER_USER_SYSTEM_INFO: str = "RegisterUserSystemInfo"
	SUBMIT_USER_SYSTEM_INFO: str = "SubmitUserSystemInfo"
	REGISTER_WECHAT_USER_SYSTEM_INFO: str = "RegisterWechatUserSystemInfo"
	SUBMIT_WECHAT_USER_SYSTEM_INFO: str = "SubmitWechatUserSystemInfo"
