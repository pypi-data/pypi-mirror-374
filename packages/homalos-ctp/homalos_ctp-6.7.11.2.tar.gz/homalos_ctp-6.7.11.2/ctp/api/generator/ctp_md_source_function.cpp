void MdApi::createFtdcMdApi(string pszFlowPath, bool bIsUsingUdp, bool bIsMulticast, bool bIsProductionMode)
{
	this->api = CThostFtdcMdApi::CreateFtdcMdApi(pszFlowPath.c_str(), bIsUsingUdp, bIsMulticast, bIsProductionMode);
	this->api->RegisterSpi(this);
};

string MdApi::getApiVersion()
{
	string version = this->api->GetApiVersion();
	return version;
};

void MdApi::release()
{
	this->api->Release();
};

void MdApi::init()
{
	this->active = true;
	this->task_thread = thread(&MdApi::processTask, this);

	this->api->Init();
};

int MdApi::join()
{
	int i = this->api->Join();
	return i;
};

string MdApi::getTradingDay()
{
	string day = this->api->GetTradingDay();
	return day;
};

void MdApi::registerFront(string pszFrontAddress)
{
	this->api->RegisterFront((char*)pszFrontAddress.c_str());
};

void MdApi::registerNameServer(string pszNsAddress)
{
	this->api->RegisterNameServer((char*)pszNsAddress.c_str());
};

void MdApi::registerFensUserInfo(const dict &req)
{
	CThostFtdcFensUserInfoField myreq = CThostFtdcFensUserInfoField();
	memset(&myreq, 0, sizeof(myreq));
	getString(req, "BrokerID", myreq.BrokerID);
	getString(req, "UserID", myreq.UserID);
	getChar(req, "LoginMode", &myreq.LoginMode);
	this->api->RegisterFensUserInfo(&myreq);
};

int MdApi::exit()
{
	this->active = false;
	this->task_queue.terminate();
	this->task_thread.join();

	this->api->RegisterSpi(NULL);
	this->api->Release();
	this->api = NULL;
	return 1;
};

int MdApi::subscribeMarketData(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };
	int i = this->api->SubscribeMarketData(myreq, 1);
	return i;
};

int MdApi::unSubscribeMarketData(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };
	int i = this->api->UnSubscribeMarketData(myreq, 1);
	return i;
};

int MdApi::subscribeForQuoteRsp(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };
	int i = this->api->SubscribeForQuoteRsp(myreq, 1);
	return i;
};

int MdApi::unSubscribeForQuoteRsp(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };
	int i = this->api->UnSubscribeForQuoteRsp(myreq, 1);
	return i;
};

int MdApi::reqUserLogin(const dict &req, int reqid)
{
	CThostFtdcReqUserLoginField myreq = CThostFtdcReqUserLoginField();
	memset(&myreq, 0, sizeof(myreq));
	getString(req, "TradingDay", myreq.TradingDay);
	getString(req, "BrokerID", myreq.BrokerID);
	getString(req, "UserID", myreq.UserID);
	getString(req, "Password", myreq.Password);
	getString(req, "UserProductInfo", myreq.UserProductInfo);
	getString(req, "InterfaceProductInfo", myreq.InterfaceProductInfo);
	getString(req, "ProtocolInfo", myreq.ProtocolInfo);
	getString(req, "MacAddress", myreq.MacAddress);
	getString(req, "OneTimePassword", myreq.OneTimePassword);
	getString(req, "reserve1", myreq.reserve1);
	getString(req, "LoginRemark", myreq.LoginRemark);
	getInt(req, "ClientIPPort", &myreq.ClientIPPort);
	getString(req, "ClientIPAddress", myreq.ClientIPAddress);
	int i = this->api->ReqUserLogin(&myreq, reqid);
	return i;
};

int MdApi::reqUserLogout(const dict &req, int reqid)
{
	CThostFtdcUserLogoutField myreq = CThostFtdcUserLogoutField();
	memset(&myreq, 0, sizeof(myreq));
	getString(req, "BrokerID", myreq.BrokerID);
	getString(req, "UserID", myreq.UserID);
	int i = this->api->ReqUserLogout(&myreq, reqid);
	return i;
};

int MdApi::reqQryMulticastInstrument(const dict &req, int reqid)
{
	CThostFtdcQryMulticastInstrumentField myreq = CThostFtdcQryMulticastInstrumentField();
	memset(&myreq, 0, sizeof(myreq));
	getInt(req, "TopicID", &myreq.TopicID);
	getString(req, "reserve1", myreq.reserve1);
	getString(req, "InstrumentID", myreq.InstrumentID);
	int i = this->api->ReqQryMulticastInstrument(&myreq, reqid);
	return i;
};

