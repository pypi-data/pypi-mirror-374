void createFtdcMdApi(string pszFlowPath="", bool bIsUsingUdp=false, bool bIsMulticast=false, bool bIsProductionMode=true);

string getApiVersion();

void release();

void init();

int join();

string getTradingDay();

void registerFront(string pszFrontAddress);

void registerNameServer(string pszNsAddress);

void registerFensUserInfo(const dict &req);

int exit();

int subscribeMarketData(string instrumentID);

int unSubscribeMarketData(string instrumentID);

int subscribeForQuoteRsp(string instrumentID);

int unSubscribeForQuoteRsp(string instrumentID);

int reqUserLogin(const dict &req, int reqid);

int reqUserLogout(const dict &req, int reqid);

int reqQryMulticastInstrument(const dict &req, int reqid);

