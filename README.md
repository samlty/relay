# relay
这是一个UDP代理程序，用与辅助登录到内网vpn

## 实现思路
- 内网VPN不断向代理服务器发送FakeUDP报文，source Port为1194， 代理服务器纪录此报文经过了NAT转换后的VpnAddress（SourceIP和Port）
- 代理服务器启动UDP 1194端口绑定，将收到的报文转发到VpnAddress
