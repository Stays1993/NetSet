from ipaddress import IPv4Network
a = {"s": 24}
CDIR = a.get('s', 0)
SubnetMask = IPv4Network(f"0.0.0.0/{CDIR}").netmask.exploded
print(SubnetMask.exploded)
