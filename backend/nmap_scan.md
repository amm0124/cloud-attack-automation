<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<?xml-stylesheet href="file:///C:/Users/user/Nmap/nmap.xsl" type="text/xsl"?>
<!-- Nmap 7.97 scan initiated Fri Jun 27 10:08:31 2025 as: C:\\Users\\user\\Nmap\\nmap.exe -p 8080,80,443 -sV -oX C:\\Users\\user\\cloud-attack-automation\\cloud-attack-automation\\backend\\nmap_scan.md 43.200.173.55 -->
<nmaprun scanner="nmap" args="C:\\Users\\user\\Nmap\\nmap.exe -p 8080,80,443 -sV -oX C:\\Users\\user\\cloud-attack-automation\\cloud-attack-automation\\backend\\nmap_scan.md 43.200.173.55" start="1750986511" startstr="Fri Jun 27 10:08:31 2025" version="7.97" xmloutputversion="1.05">
<scaninfo type="syn" protocol="tcp" numservices="3" services="80,443,8080"/>
<verbose level="0"/>
<debugging level="0"/>
<hosthint><status state="up" reason="unknown-response" reason_ttl="0"/>
<address addr="43.200.173.55" addrtype="ipv4"/>
<hostnames>
</hostnames>
</hosthint>
<host starttime="1750986514" endtime="1750986522"><status state="up" reason="reset" reason_ttl="52"/>
<address addr="43.200.173.55" addrtype="ipv4"/>
<hostnames>
<hostname name="ec2-43-200-173-55.ap-northeast-2.compute.amazonaws.com" type="PTR"/>
</hostnames>
<ports><port protocol="tcp" portid="80"><state state="closed" reason="reset" reason_ttl="52"/><service name="http" method="table" conf="3"/></port>
<port protocol="tcp" portid="443"><state state="filtered" reason="no-response" reason_ttl="0"/><service name="https" method="table" conf="3"/></port>
<port protocol="tcp" portid="8080"><state state="open" reason="syn-ack" reason_ttl="52"/><service name="http" product="Jetty" version="10.0.18" method="probed" conf="10"><cpe>cpe:/a:mortbay:jetty:10.0.18</cpe></service></port>
</ports>
<times srtt="15015" rttvar="8906" to="100000"/>
</host>
<runstats><finished time="1750986522" timestr="Fri Jun 27 10:08:42 2025" summary="Nmap done at Fri Jun 27 10:08:42 2025; 1 IP address (1 host up) scanned in 11.78 seconds" elapsed="11.78" exit="success"/><hosts up="1" down="0" total="1"/>
</runstats>
</nmaprun>
