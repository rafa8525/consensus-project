## VPN Test — 2025-10-13 23:21:04
- DNS: **PASS** — Resolved dns.google
- Outbound: **PASS** — TCP 1.1.1.1:53 ok
- PublicIP: **PASS** — 54.82.74.200
- ENV VPN_ENABLED: `unset`

## VPN Test — 2025-10-13 23:21:04
- DNS: **PASS** — Resolved dns.google
- Outbound: **PASS** — TCP 1.1.1.1:53 ok
- PublicIP: **PASS** — 54.82.74.200
- ENV VPN_ENABLED: `unset`

## Activation Test — 2025-10-14 02:02:45
SUCCESS
52.207.196.103

## Load Test Attempt 1 — 2025-10-14 02:02:46
SUCCESS
<!doctype html><html lang="en"><head><title>Example Domain</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{background:#eee;width:60vw;margin:15vh auto;font-family:system-ui,sans-serif}h1{font-size:1.5em}div{opacity:0.8}a:link,a:visited{color:#348}</style><body><div><h1>Example Domain</h1><p>This domain is for use in documentation examples without needing permission. Avoid use in operations.<p><a href="https://iana.org/domains/example">Learn more</a></div></body></html>

## Load Test Attempt 2 — 2025-10-14 02:02:46
SUCCESS
<!doctype html><html lang="en"><head><title>Example Domain</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{background:#eee;width:60vw;margin:15vh auto;font-family:system-ui,sans-serif}h1{font-size:1.5em}div{opacity:0.8}a:link,a:visited{color:#348}</style><body><div><h1>Example Domain</h1><p>This domain is for use in documentation examples without needing permission. Avoid use in operations.<p><a href="https://iana.org/domains/example">Learn more</a></div></body></html>

## Load Test Attempt 3 — 2025-10-14 02:02:47
SUCCESS
<!doctype html><html lang="en"><head><title>Example Domain</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{background:#eee;width:60vw;margin:15vh auto;font-family:system-ui,sans-serif}h1{font-size:1.5em}div{opacity:0.8}a:link,a:visited{color:#348}</style><body><div><h1>Example Domain</h1><p>This domain is for use in documentation examples without needing permission. Avoid use in operations.<p><a href="https://iana.org/domains/example">Learn more</a></div></body></html>

## Stress Test (Ping) — 2025-10-14 02:02:51
SUCCESS
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=115 time=1.01 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=115 time=0.957 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=115 time=0.961 ms
64 bytes from 8.8.8.8: icmp_seq=4 ttl=115 time=0.962 ms
64 bytes from 8.8.8.8: icmp_seq=5 ttl=115 time=0.953 ms

--- 8.8.8.8 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4004ms
rtt min/avg/max/mdev = 0.953/0.968/1.011/0.021 ms

## Failover Test (DNS) — 2025-10-14 02:03:06
FAIL


## Detection Test (IP Fingerprint) — 2025-10-14 02:03:06
SUCCESS
{
  "ip": "52.207.196.103",
  "hostname": "ec2-52-207-196-103.compute-1.amazonaws.com",
  "city": "Ashburn",
  "region": "Virginia",
  "country": "US",
  "loc": "39.0437,-77.4875",
  "org": "AS14618 Amazon.com, Inc.",
  "postal": "20147",
  "timezone": "America/New_York",
  "readme": "https://ipinfo.io/missingauth"
}

