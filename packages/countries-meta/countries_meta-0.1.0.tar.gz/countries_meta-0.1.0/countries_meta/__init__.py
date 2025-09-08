import csv
import json
import importlib.resources
from zoneinfo import ZoneInfo
from datetime import datetime
from dataclasses import dataclass, asdict


TIMEZONE_REGIONS = (
	'Africa',
	'America',
	'Asia',
	'Atlantic',
	'Australia',
	'Europe',
	'Indian',
	'Pacific'
)


@dataclass(slots=True)
class Country:
	code: str
	name: str
	origin_name: str
	dial_code: str
	currency_code: str
	currency_symbol: str
	capital: str
	timezone: str

	def __str__(self):
		return f'<Country[{self.code}]: {self.name}>'

	@classmethod
	def from_row(cls, code, name, origin_name, dial_code, currency_code, currency_symbol, capital, region_index, subregion):
		origin_name = origin_name or name
		dial_code = f'+{dial_code}'

		region_name = TIMEZONE_REGIONS[int(region_index)]
		subregion = subregion or capital
		timezone = f'{region_name}/{subregion}'

		return cls(code, name, origin_name, dial_code, currency_code, currency_symbol, capital, timezone)

	@property
	def tzinfo(self):
		return ZoneInfo(self.timezone)
	
	@property
	def now(self):
		return datetime.now(self.tzinfo)

	@property
	def time_offset(self):
		return self.now.utcoffset().total_seconds() / 3600

	
	def to_dict(self, *keys):
		data = asdict(self)
		data['now'] = self.now.isoformat()
		data['time_offset'] = self.time_offset
		
		return {k: data[k] for k in (keys or data.keys()) if k in data}

	def to_json(self, *keys):
		return json.dumps(self.to_dict(*keys), ensure_ascii=False)


class Countries:
	def __init__(self):
		self._countries = self._load_countries()

	def __str__(self):
		return f'<Countries[{len(self)}]>'

	def __iter__(self):
		return iter(self._countries)

	def __len__(self):
		return len(self._countries)

	def __getitem__(self, code):
		result = self.get_by_code(code)
		if not result:
			raise KeyError(code)
		return result

	def _load_countries(self):
		with importlib.resources.open_text("countries_meta", "countries.csv", encoding="utf-8") as f:
			reader = csv.reader(f)
			next(reader)

			result = []
			for row in reader:
				row = [None if c == '' else c.strip() for c in row]
				result.append(Country.from_row(*row))

			return result

	def _get_by_field(self, field, value, default=None, transform=lambda x: x):
		value = transform(value)
		for country in self._countries:
			if getattr(country, field) == value:
				return country
		return default

	@property
	def get(self): return self.get_by_code

	def get_by_code(self, code, default=None):
		return self._get_by_field('code', code.upper(), default)

	def get_by_name(self, name, default=None):
		return self._get_by_field('name', name.lower(), default, transform=lambda v: v.lower())

	def get_by_origin_name(self, name, default=None):
		name = name.lower()
		for c in self._countries:
			if (c.origin_name or c.name).lower() == name:
				return c
		return default

	def get_by_dial_code(self, dial_code, default=None):
		dial_code = str(dial_code).lstrip('+')
		return self._get_by_field('dial_code', f'+{dial_code}', default)

	def get_by_currency_code(self, currency_code, default=None):
		return self._get_by_field('currency_code', currency_code.upper(), default)

	def filter_by_currency_code(self, currency_code):
		code = currency_code.upper()
		return [c for c in self._countries if c.currency_code == code]

	def filter_by_region(self, region):
		return [c for c in self._countries if c.timezone.startswith(region)]
