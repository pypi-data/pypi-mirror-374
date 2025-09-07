# DNScode
## Simplifying DNS Zone management

---

## About

DNScode is a project to help simplify DNS zone management, when using plain text files with servers like BIND and NSD. It provides a framework for programmatically generating zone
files with Python, allowing for more flexability, compared to other DNS as code solutions.

## Installation
``` bash
# Create working directory
mkdir dnsproject
cd dnsproject

# Create virtual envrionment (optional, but highly recomended)
python3 -m venv .venv
source .venv/bin/activate

# Install the dnscode package
pip install dnscode
```

## Usage

Import the dnscode package into a python script, create a zone object, then add records into the zone. Records can be added either via helper functions in the [dnscode.Zone](https://dnscode.minecraftchest1.us/classdnscode_1_1dnscode_1_1Zone) class, or by manually creating record objects and adding them through [dnscode.Zone.add()](https://dnscode.minecraftchest1.us/classdnscode_1_1dnscode_1_1Zone#a338bc686b7c7db2cab7827996a3f23f3). Both methods are shown in the example below.

Once the zone is setup, you can save it as a text file using [dnscode.Zone.save_file()](https://dnscode.minecraftchest1.us/classdnscode_1_1dnscode_1_1Zone#adfe5442ed2137a324f1c5ba676ba2043). Currently, it also outputs to to STDOUT. See https://code.minecraftchest1.us/minecraftchest1/dnscode/issues/5 for details.

API docs at https://dnscode.minecraftchest1.us/classdnscode_1_1dnscode_1_1Zone

```python
import dnscode

zone = dnscode.Zone(origin='example.com')				# Create zone object
zone.new_SOA(mname='ns1.minecraftchest1.us.',			# Create SOA
	rname='admin.minecraftchest1.us.',
	refresh=onemonth, retry=oneday, ttl=oneday)
zone.new_A(name='myhost', ttl=3600, host='0.0.0.0')		#New A record
zone.new_AAAA(name='myhost', ttl-3600, hosts='::1')
# More helper functions in the docs

cname = dnscode.CNAME(name='mycname', ttl=60, host='example.com')
# More record objects in the docs.
zone.add(cname)

zone.save_file('example.zone')
```