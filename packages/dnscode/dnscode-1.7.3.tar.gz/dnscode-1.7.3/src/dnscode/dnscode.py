#	DNScode - Simplifying DNS Zone Management
#	Copyright (C) 2025 Minecraftchest1

#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum
from dataclasses import dataclass, field
import time
import ipaddress

"""@package dnscode

Simplifying DNS Zone management
"""

class InvalidDataException(Exception):
	"""Exception raised when invalid data is passed to a record."""

	def __init__(self, message):
		self.message = message
		super().__init__(self, message)

@dataclass
class Record:
	"""Base class for DNS records."""

	rclass: str	= 'IN'    # DNS class, usually 'IN' for internet
	rtype: str	= 'A'      # Record type (A, AAAA, MX, etc.)
	name: str	= '@'       # Name of the record (e.g., domain name)
	data: str	= '0.0.0.0' # Data associated with the record (e.g., IP address or hostname)
	ttl: int	= 3600       # Time to live (TTL) for the record in seconds

	def __str__(self):
		"""Returns a string representation of the record."""
		return f"{self.name} {self.ttl} {self.rclass} {self.rtype} {self.data}"

@dataclass
class A(Record):
	"""Represents an 'A' (IPv4 address) record."""

	#host: str

	def __init__(self, name: str = '@', ttl: int = 3600, host: str = '0.0.0.0'):
		if isinstance(ipaddress.ip_address(host), ipaddress.IPv4Address):
			self.data = host
		else:
			raise InvalidDataException(message=f'{str(host)} is not a valid IPv4 address.')

		self.rtype	= 'A'
		self.name	= str(name)
		self.ttl	= ttl

@dataclass
class AAAA(Record):
	"""Represents an 'AAAA' (IPv6 address) record."""

	#host:str

	def __init__(self, name: str = '@', ttl: int = 3600, host: str = '0.0.0.0'):
		if isinstance(ipaddress.ip_address(host), ipaddress.IPv6Address):
			self.data = host
		else:
			raise InvalidDataException(message=f'{str(host)} is not a valid IPv6 address.')

		self.rtype	= 'AAAA'
		self.name	= str(name)
		self.ttl	= ttl

@dataclass
class CNAME(Record):
	"""Represents a 'CNAME' (Canonical Name) record."""

	#target: str

	def __init__(self, name: str = '@', ttl: int = 3600, host: str = 'example.com'):
		self.rtype	= 'CNAME'
		self.name	= str(name)
		self.ttl	= ttl
		self.data = host

@dataclass
class MX(Record):
	"""Represents an 'MX' (Mail Exchange) record."""

	#host: str

	def __init__(self, name: str = '@', ttl: int = 3600, priority: int = 10, host: str = 'example.com'):
		self.rtype	= 'MX'
		self.name	= name
		self.ttl	= ttl
		self.priority	= priority
		self.host = host
		self.data = f"{self.priority} {self.host}"

@dataclass
class NS(Record):
	"""Represents an 'NS' (Name Server) record."""

	#target: str

	def __init__(self, name: str = '@', ttl: int = 3600, host: str = 'example.com'):
		self.rtype	= 'NS'
		self.name	= name
		self.ttl	= ttl
		self.host	= host
		self.data = host

@dataclass
class PTR(Record):
	"""Represents a 'PTR' (Pointer) record."""

	#host: str

	def __init__(self, name: str = '@', ttl: int = 3600, host: str = 'example.com'):
		self.rtype	= 'PTR'
		self.name	= name
		self.ttl	= ttl
		self.data = host

@dataclass
class SOA(Record):
	"""Represents an 'SOA' (Start of Authority) record."""

	#mname: str
	#rname: str
	#serial: int
	#refresh: int
	#retry: int
	#expire: int

	def __init__(self, name: str = '@', mname: str = 'ns1.example.com', rname: str = 'admin.example.com',
				serial: int = int(time.time()), refresh: int = 86400, retry: int = 7200,
				expire: int = 15552000, ttl: int = 21700):
		self.rtype	= 'SOA'
		self.name	= name
		self.mname	= mname
		self.rname	= rname
		self.serial	= serial
		self.refresh	= refresh
		self.retry	= retry
		self.expire	= expire
		self.ttl	= ttl
		self.data	= f"{self.mname} {self.rname} {self.serial} {self.refresh} {self.retry} {self.expire} {self.refresh}"

@dataclass
class SRV(Record):
	"""Represents an 'SRV' (Service) record."""

	#service: str
	#protocol: str
	#priority: int
	#weight: int
	#port: int
	#target: str

	def __init__(self, name: str = '@', ttl: int = 3600, service: str = "service", protocol: str = 'proto',
				priority: int = 10, weight: int = 10, port: int = 0, host: str = 'example.com'):
		self.rtype	= 'SRV'
		self.name	= f"_{service}._{protocol}.{name}"
		self.ttl	= ttl
		self.service	= service
		self.protocol	= protocol
		self.priority	= priority
		self.weight	= weight
		self.port	= port
		self.host = host
		self.data = f"{self.priority} {self.weight} {self.port} {self.host}"

@dataclass
class TXT(Record):
	"""Represents a 'TXT' (Text) record."""

	#target: str

	def __init__(self, name: str = '@', ttl: int = 3600, text: str = 'example.com'):
		self.rtype	= 'TXT'
		self.name	= str(name)
		self.ttl	= ttl
		self.data	= "\"" + text + "\""

@dataclass
class Zone:
	"""Represents a DNS zone containing multiple records."""
	origin: str = 'example.com'
	records: list = field(default_factory=list)

	def __post_init__(self):
		"""Initializes a zone with the given origin and ensures it ends with a dot."""
		if self.origin[-1] != '.':
			self.origin = self.origin + '.'

		#self.records: list = field(default_factory=list)

	def __str__(self):
		"""Returns a string representation of the zone."""
		zone = ''
		for record in self.records:
			zone += str(record) + '\n'
		return zone

	def __mkfqdn(self, name: str) -> str:
		"""Converts a name to a fully qualified domain name (FQDN)."""
		if str(name)[-1] != '.':
			return str(name) + '.' + self.origin
		else:
			return str(name)

	def new_A(self, name: str = '@', ttl: int = 3600, host: str = '0.0.0.0'):
		"""Creates and adds a new A record to the zone."""
		if isinstance(name, list):
			for recordname in name:
				recordname = self.__mkfqdn(recordname)
				self.add(A(name=recordname, ttl=ttl, host=host))
		else:
			name = self.__mkfqdn(name)
			self.add(A(name=name, ttl=ttl, host=host))

	def new_AAAA(self, name: str = '@', ttl: int = 3600, host: str = 'fe80::42:2cff:fe29:8db1'):
		"""Creates and adds a new AAAA record to the zone."""
		if isinstance(name, list):
			for recordname in name:
				recordname = self.__mkfqdn(recordname)
				self.add(AAAA(name=recordname, ttl=ttl, host=host))
		else:
			name = self.__mkfqdn(name)
			self.add(AAAA(name=name, ttl=ttl, host=host))

	def new_CNAME(self, name: str = '@', ttl: int = 3600, host: str = 'example.com'):
		"""Creates and adds a new CNAME record to the zone."""
		if isinstance(name, list):
			for recordname in name:
				recordname = self.__mkfqdn(recordname)
				self.add(CNAME(name=recordname, ttl=ttl, host=host))
		else:
			name = self.__mkfqdn(name)
			self.add(CNAME(name=name, ttl=ttl, host=host))

	def new_MX(self, name: str = '@', ttl: int = 3600, priority: int = 10, host: str = 'example.com'):
		"""Creates and adds a new MX record to the zone."""
		if isinstance(name, list):
			for recordname in name:
				recordname = self.__mkfqdn(recordname)
				self.add(MX(name=recordname, ttl=ttl, priority=priority, host=host))
		else:
			name = self.__mkfqdn(name)
			self.add(MX(name=name, ttl=ttl, priority=priority, host=host))

	def new_NS(self, name: str = '@', ttl: int = 3600, host: str = 'example.com'):
		"""Creates and adds a new NS record to the zone."""
		if isinstance(name, list):
			for recordname in name:
				recordname = self.__mkfqdn(recordname)
				self.add(NS(name=recordname, ttl=ttl, host=host))
		else:
			name = self.__mkfqdn(name)
			self.add(NS(name=name, ttl=ttl, host=host))

	def new_PTR(self, name: str = '@', ttl: int = 3600, host: str = 'example.com'):
		"""Creates and adds a new PTR record to the zone."""
		if isinstance(name, list):
			for recordname in name:
				recordname = self.__mkfqdn(recordname)
				self.add(PTR(name=recordname, ttl=ttl, host=host))
		else:	
			name = self.__mkfqdn(name)
			self.add(PTR(name=name, ttl=ttl, host=host))

	def new_SOA(self, name, mname: str = 'ns1.example.com', rname: str = 'admin.example.com',
				serial: int = int(time.time()), refresh: int = 86400, retry: int = 7200,
				expire: int = 15552000, ttl: int = 21700):
		"""Creates and adds a new SOA record to the zone."""
		mname = self.__mkfqdn(mname)
		self.add(SOA(name=name,mname=mname, rname=rname, serial=serial, refresh=refresh, retry=retry, expire=expire, ttl=ttl))

	def new_SRV(self, name: str = '@', ttl: int = 3600, service: str = 'service', protocol: str = 'proto',
				priority: int = 10, weight: int = 10, port: int = 443, host: str = 'example.com'):
		"""Creates and adds a new SRV record to the zone."""
		if isinstance(name, list):
			for recordname in name:
				recordname = self.__mkfqdn(recordname)
				self.add(SRV(name=recordname, ttl=ttl, service=service, protocol=protocol,
						priority=priority, weight=weight, port=port, host=host))
		else:
			name = self.__mkfqdn(name)
			self.add(SRV(name=name, ttl=ttl, service=service, protocol=protocol,
					priority=priority, weight=weight, port=port, host=host))

	def new_TXT(self, name: str = '@', ttl: int = 3600, text: str = 'example.com'):
		"""Creates and adds a new CNAME record to the zone."""
		if isinstance(name, list):
			for recordname in name:
				recordname = self.__mkfqdn(recordname)
				self.add(TXT(name=recordname, ttl=ttl, text=text))
		else:		
			name = self.__mkfqdn(name)
			self.add(TXT(name=name, ttl=ttl, text=text))

	def new_record(self, name: str = '@', ttl: int = 3600, rtype: str = 'A', data: str = '0.0.0.0'):
		"""Creates and adds a generic DNS record to the zone."""
		name = self.__mkfqdn(name)
		self.add(Record(name=name, ttl=ttl, rtype=rtype, data=data))

	def add(self, record: Record):
		"""Adds a record to the zone."""
		self.records.append(record)

	def save_stdout(self):
		for record in self.records:
			print(str(record))

	def save_file(self, filepath: str):
		"""Saves the zone records to a file."""
		with open(filepath, 'w') as file:
			for record in self.records:
				file.write(str(record) + '\n')