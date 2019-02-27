# Extracters

from bonobo.config import Configurable, Option, use
from bonobo.constants import NOT_MODIFIED
import uuid
from extracters.cleaners import date_cleaner


# Here we extract the data from the sources and collect it together

# ~~~~ Core Functions ~~~~

all_names = {
	'gpi_people': ['uid', 'label', 'ulan', 'birth', 'death', 'active_early', 'active_late', 
		'nationality', 'aat_nationality_1', 'aat_nationality_2', 'aat_nationality_3'],
	'knoedler': ['star_id', 'pi_record_no', 'stock_book_no', 'page_number', 'row_number', 
		'description', 'subject', 'genre', 'object_type', 'materials', 'dimensions', 'folio', 
		'working_note', 'verbatim_notes', 'link', 'main_heading', 'subheading', 'auction_sale', 
		'auction_purchase','object_id', 'share_note', 'sale_event', 'purchase_event', 'inventory_event'],
	'purchase_info': ['uid', 'amount', 'currency', 'k_amount', 'k_curr', 'note', 'k_note', 
		'year', 'month', 'day', 'dec_amount', 'currency_aat', 'dec_k_amount', 'k_curr_aat'],
	'sale_info': ['uid', 'type', 'year', 'month', 'day', 'share_amount', 'share_currency', 
		'share_note', 'amount', 'currency', 'note', 'dec_amount', 'currency_aat', 
		'dec_share_amount', 'share_currency_aat'],
	'raw': ['orig_file', 'star_id', 'pi_id', 'stock_book_id', 'knoedler_id', 'page_num', 
		'row_num', 'consign_num', 'consign_name', 'consign_loc', 'consign_ulan_id', 
		'artist_name_1', 'artist_name_auth_1', 'nationality_1', 'attrib_mod_1', 'attrib_mod_auth_1', 'star_rec_no_1', 'artist_ulan_1', 
		'artist_name_2', 'artist_name_auth_2', 'nationality_2', 'attrib_mod_2', 'attrib_mod_auth_2', 'star_rec_no_2', 'artist_ulan_2', 
		'title', 'description', 'subject', 'genre', 'object_type', 'materials', 'dimensions', 
		'entry_date_year', 'entry_date_month', 'entry_date_day', 'sale_date_year', 
		'sale_date_month', 'sale_date_day', 'purchase_amount', 'purchase_currency', 
		'purchase_note', 'knoedler_purchase_amount', 'knoedler_purchase_currency', 'knoedler_purchase_note',
		'price_amount', 'price_currency', 'price_note', 'share_amount', 'share_currency', 'share_note',
		'seller_name_1', 'seller_loc_1', 'seller_mod_1', 'seller_name_auth_1', 'seller_auth_loc_1', 'seller_auth_mod_1', 'seller_ulan_1',
		'seller_name_2', 'seller_loc_2', 'seller_mod_2', 'seller_name_auth_2', 'seller_auth_loc_2', 'seller_auth_mod_2', 'seller_ulan_2',
		'joint_owner_1', 'joint_owner_sh_1', 'joint_owner_ulan_1', 
		'joint_owner_2', 'joint_owner_sh_2', 'joint_owner_ulan_2',
		'joint_owner_3', 'joint_owner_sh_3', 'joint_owner_ulan_3', 'transaction',
		'buyer_name_1', 'buyer_loc_1', 'buyer_mod_1', 'buyer_name_auth_1', 'buyer_addr_auth_1', 'buyer_auth_mod_1', 'buyer_ulan_1',
		'buyer_name_2', 'buyer_loc_2', 'buyer_mod_2', 'buyer_name_auth_2', 'buyer_addr_auth_2', 'buyer_auth_mod_2', 'buyer_ulan_2',
		'folio',
		'prev_owner_1', 'prev_owner_loc_1', 'prev_owner_ulan_1',
		'prev_owner_2', 'prev_owner_loc_2', 'prev_owner_ulan_2',
		'prev_owner_3', 'prev_owner_loc_3', 'prev_owner_ulan_3',
		'prev_owner_4', 'prev_owner_loc_4', 'prev_owner_ulan_4',				
		'prev_owner_5', 'prev_owner_loc_5', 'prev_owner_ulan_5',
		'prev_owner_6', 'prev_owner_loc_6', 'prev_owner_ulan_6',
		'prev_owner_7', 'prev_owner_loc_7', 'prev_owner_ulan_7',
		'prev_owner_8', 'prev_owner_loc_8', 'prev_owner_ulan_8',
		'prev_owner_9', 'prev_owner_loc_9', 'prev_owner_ulan_9',
		'post_owner', 'post_owner_ulan', 'present_loc_geog', 'present_loc_inst', 'present_loc_acc', 'present_loc_note',
		'present_owner_ulan', 'working_notes', 'verbatim_notes', 'link', 'heading', 'subheading',
		'MATT_object_id', 'MATT_inventory_id', 'MATT_sale_event_id', 'MATT_purchase_event_id'
		]
}

aat_label_cache = {}


class AddArchesModel(Configurable):
	model = Option()
	def __call__(self, data):
		data['_ARCHES_MODEL'] = self.model
		return data

class AddFieldNames(Configurable):
	key = Option()
	def __call__(self, *data):	
		if len(data) == 1 and type(data[0]) == tuple:
			data = data[0]
		names = all_names.get(self.key, [])
		return dict(zip(names, data))		


def get_actor_type(ulan, uuid_cache):
	if not ulan:
		return "Actor"
	s = 'SELECT type FROM actor_type WHERE ulan="%s"' % ulan
	res = uuid_cache.execute(s)
	v = res.fetchone()
	if v:
		return v[0]
	else:
		# Almost certainly a Person
		return "Actor"

def fetch_uuid(key, uuid_cache):
	return add_uuid({'uid':key}, uuid_cache=uuid_cache)['uuid']

@use('uuid_cache')
def add_uuid(thing: dict, uuid_cache=None):
	# Need access to select from the uuid_cache
	s = 'SELECT uuid FROM mapping WHERE key="%s"' % (thing['uid']) 
	res = uuid_cache.execute(s)
	row = res.fetchone()
	if row is None:
		uu = str(uuid.uuid4())
		c = 'INSERT INTO mapping (key, uuid) VALUES ("%s", "%s")' % (thing['uid'], uu)
		uuid_cache.execute(c)
		thing['uuid'] = uu
	else:
		thing['uuid'] = row[0]
	return thing

@use('gpi')
def get_aat_label(term, gpi=None):
	if term in aat_label_cache:
		return aat_label_cache[term]
	else:
		res = gpi.execute('SELECT aat_label FROM aat WHERE aat_id=%s' % (term,))
		l = res.fetchone()
		if l:
			aat_label_cache[term] = l[0]
		else:
			print("Got no hit in matt's aat table for %s" % term)
			print("Implement lookup to AAT via http")
			return "XXX - FIX ME"
		return l[0]


# ~~~~ Object Tables ~~~~

@use('gpi')
@use('uuid_cache')
def make_objects(object_id, gpi=None, uuid_cache=None):

	data = {'uid': object_id}
	fields = ['recno', 'book', 'page', 'row', 'subject', 'genre', 'object_type', 'materials', 'dimensions']
	for f in fields[4:]:
		data[f] = []
	s = 'SELECT pi_record_no, stock_book_no, page_number, row_number, subject, genre, object_type, materials, dimensions FROM knoedler WHERE object_id="%s"' % object_id
	res = gpi.execute(s)
	for r in res:
		# multiple rows per object with different information possible
		row = dict(zip(fields, r))
		uu = fetch_uuid(row['recno'], uuid_cache)
		source = [row['recno'], uu, row['book'], row['page'], row['row']]
		for lo in ['subject', 'genre', 'materials', 'dimensions']:
			if row[lo]:
				if data[lo]:
					found = 0
					for l in data[lo]:
						if l['value'] == row[lo]:
							l['sources'].append(source)
							found =1
							break
					if not found:
						data[lo].append({"value": row[lo], "sources": [source]})
				else:
					data[lo] = [{"value": row[lo], "sources": [source]}]

		if row['object_type'] and not data['object_type']:
			data['object_type'] = row['object_type']
			if data['object_type'] in ["Painting [?]", "Watercolor; Painting", "Watercolor"]:
				data['object_type'] = "Painting"
	return data

@use('uuid_cache')
@use('gpi')
def make_objects_artists(data, gpi=None, uuid_cache=None):
	object_id = data['uid']
	s = 'SELECT a.artist_uid, peep.person_label, peep.person_ulan, a.artist_attribution_mod, a.attribution_is_preferred, a.star_record_no, k.stock_book_no, k.page_number, k.row_number ' + \
		'FROM knoedler_artists as a, gpi_people as peep, knoedler as k ' + \
		'WHERE a.object_id="%s" AND peep.person_uid = a.artist_uid AND k.star_record_no = a.star_record_no' % object_id
	res = gpi.execute(s)

	artists = []
	artistById = {}
	for row in res:
		attr = dict(zip(["artist", "label", "ulan", "mod", "pref", 'star_id', "book", "page", "row"], row))
		if attr['mod']:
			attr['mod'] = attr['mod'].lower()
			if attr['mod'].startswith('and '):
				attr['mod'] = None

		uu = fetch_uuid("K-ROW-%s-%s-%s" % (attr['book'], attr['page'], attr['row']), uuid_cache)

		if attr['artist'] in artistById:
			# Add source
			artistById[attr['artist']]['sources'].append([ attr['star_id'], uu, attr['book'], attr['page'], attr['row']])				
			# Check mod is recorded
			if attr['mod']:
				artistById[attr['artist']]['mod'] = attr['mod']
			if attr['pref']:
				artistById[attr['artist']]['pref'] = 1
		else:
			ut = fetch_uuid(attr['artist'], uuid_cache)
			atype = get_actor_type(attr['ulan'], uuid_cache)
			who = {'uuid': ut, 'uid': attr['artist'], 'ulan': attr['ulan'], 'type': atype, 'mod': attr['mod'], 'label': attr['label'], 'pref': attr['pref'],
					'sources': [ [attr['star_id'], uu, attr['book'], attr['page'], attr['row']] ]}
			artists.append(who)
			artistById[attr['artist']] = who

	data['artists'] = artists
	return data


# These are separated out so that they can be parallelized

@use('uuid_cache')
@use('gpi')
def make_objects_dims(data, gpi=None, uuid_cache=None):
	object_id = data['uid']

	# Pull in parsed dimensions
	s = 'SELECT d.object_id, d.star_record_no, d.dimension_value, d.dimension_unit_aat, d.dimension_type_aat, ' + \
		'k.stock_book_no, k.page_number, k.row_number, k.object_type FROM knoedler_dimensions as d, knoedler as k ' + \
		'WHERE k.star_record_no = d.star_record_no AND d.object_id = "%s"' % object_id
	res = gpi.execute(s)
	dfields = ['object_id', 'star_record_no', 'value', 'unit', 'type', 'book', 'page', 'row', 'obj_type']
	dimByType = {300055624: [], 300055644: [], 300055647: [], 300072633: [], 300055642: []}
	dims = []
	for dim in res:
		dimdata = dict(zip(dfields, dim))
		# see if we have the same value, if so don't create a new Dimension
		newdim = None
		if 'type' in dimdata:
			for d in dimByType[dimdata['type']]:
				if d['value'] == dimdata['value']:
					newdim = d
					break
		else:
			# no type for this dimension :(
			if data['obj_type'] == "Sculpture":
				# Assert that it's Depth
				dimdata['type'] = 300072633
			else:
				# Assert "Unknown" (aka 'size (general extent)')
				dimdata['type'] = 300055642

		if newdim is None:
			# create a new Dimension of appropriate type
			newdim = {'type': dimdata['type'], 'value': dimdata['value'], 'unit': dimdata['unit'], 'sources': []}
			dimByType[dimdata['type']].append(newdim)
			dims.append(newdim)
		# And now add reference
		uu = fetch_uuid("K-ROW-%s-%s-%s" % (dimdata['book'], dimdata['page'], dimdata['row']), uuid_cache)
		newdim['sources'].append([dimdata['star_record_no'], uu, dimdata['book'], dimdata['page'], dimdata['row']])
	data['dimensions_clean'] = dims

	return data


@use('uuid_cache')
@use('gpi')
def make_objects_names(data, gpi=None, uuid_cache=None):
	object_id = data['uid']
	# Pull in object names
	tfields = ['value', 'preferred', 'star_no', 'book', 'page', 'row']
	s = 'SELECT t.title, t.is_preferred_title, t.star_record_no, k.stock_book_no, k.page_number, k.row_number ' + \
		'FROM knoedler_object_titles as t, knoedler as k WHERE t.star_record_no = k.star_record_no AND t.object_id = "%s"' % object_id
	res = gpi.execute(s)
	names = []
	nameByVal = {}
	for row in res:
		title = dict(zip(tfields, row))

		# XXX clean value, generate comparison value
		# SHOULD WE DO THIS? (Rob thinks yes)
		value = title['value']
		if value[0] == '"' and value[-1] == '"':
			value = value[1:-1]
			title['value'] = value
		compValue = value.lower()

		uu = fetch_uuid("K-ROW-%s-%s-%s" % (title['book'], title['page'], title['row']), uuid_cache)	
		if compValue in nameByVal:
			nameByVal[compValue]['sources'].append([title['star_no'], uu, title['book'], title['page'], title['row']])
			if title['preferred']:
				nameByVal[compValue]['value'] = title['value']
		else:
			name = {'value': title['value'], 'pref': title['preferred'], 'sources': [[title['star_no'], uu, title['book'], title['page'], title['row']]]}
			nameByVal[compValue] = name
			names.append(name)
	data['names'] = names
	return data


@use('gpi')
def make_objects_tags_ids(data, gpi=None):
	object_id = data['uid']
	# Pull in "tags"
	# knoedler_depicts_aat - https://linked.art/model/object/aboutness/#depiction
	# knoedler_materials_classified_as_aat - https://linked.art/model/object/identity/#types (n.b. from LA docs that all objects must also have aat:300133025 (works of art) in addition to any of these tags)
	# knoedler_materials_object_aat - https://linked.art/model/object/physical/#materials
	# knoedler_materials_support_aat - https://linked.art/model/object/physical/#parts (where there are multiple terms per object, attach all terms to one Part)
	# knoedler_materials_technique_aat - https://linked.art/model/provenance/production.html#roles-techniques
	# knoedler_style_aat - https://linked.art/model/object/aboutness/#style
	# knoedler_subject_classified_as_aat - http://linked.art/model/object/aboutness/#classifications

	tagMap = {"knoedler_depicts_aat": "depicts", "knoedler_materials_classified_as_aat": "classified_as",
			"knoedler_materials_object_aat": "object_material", "knoedler_materials_support_aat": "support_material",
			"knoedler_materials_technique_aat": "technique", "knoedler_style_aat": "style", 
			"knoedler_subject_classified_as_aat": "subject"}

	s = 'SELECT tag_type, aat_term FROM knoedler_object_tags WHERE object_id="%s"' % object_id
	res = gpi.execute(s)
	tags = []
	for tag in res:
		lbl = get_aat_label(tag[1], gpi=gpi)
		tags.append({"type": tagMap[tag[0]], "aat": str(tag[1]), "label": lbl})
	data['tags'] = tags

	# Pull in Identifiers
	s = 'SELECT knoedler_number FROM knoedler_object_identifiers WHERE object_id="%s"' % object_id
	res = gpi.execute(s)
	ids = [str(x[0]) for x in res]
	data['knoedler_ids'] = ids

	return data

# ~~~~ Acquisitions ~~~~

@use('gpi')
@use('uuid_cache')
def add_purchase_people(thing: dict, gpi=None, uuid_cache=None):	
	s = 'SELECT b.purchase_buyer_uid, b.purchase_buyer_share, p.person_label, p.person_ulan ' + \
		'FROM knoedler_purchase_buyers AS b, gpi_people as p ' + \
		'WHERE b.purchase_event_id="%s" AND b.purchase_buyer_uid=p.person_uid' % thing['uid']
	buyers = []
	res = gpi.execute(s)
	for row in res:
		uu = fetch_uuid(row[0], uuid_cache)
		atype = get_actor_type(str(row[3]), uuid_cache)
		buyers.append({'uuid': uu, 'ulan': row[3], 'type': atype, 'label': str(row[2]), 'share': row[1]})
	thing['buyers'] = buyers

	s = 'SELECT s.purchase_seller_uid, s.purchase_seller_auth_mod, p.person_label, p.person_ulan ' + \
		'FROM knoedler_purchase_sellers AS s, gpi_people as p ' + \
		'WHERE s.purchase_event_id="%s" AND s.purchase_seller_uid=p.person_uid' % thing['uid']
	sellers = []
	res = gpi.execute(s)
	for row in res:
		uu = fetch_uuid(row[0], uuid_cache)
		atype = get_actor_type(str(row[3]), uuid_cache)
		sellers.append({'uuid': uu, 'ulan': row[3], 'type': atype, 'label': str(row[2]), 'mod': row[1]})
	thing['sellers'] = sellers
	return thing

@use('gpi')
@use('uuid_cache')
def add_purchase_thing(thing: dict, gpi=None, uuid_cache=None):
	s = 'SELECT k.star_record_no, k.stock_book_no, k.page_number, k.row_number, k.object_id, n.title ' + \
		'FROM knoedler as k, knoedler_object_titles as n ' + \
		'WHERE k.object_id = n.object_id AND n.is_preferred_title = 1 AND k.purchase_event_id="%s"' % thing['uid']
	res = gpi.execute(s)

	thing['sources'] = []
	thing['objects'] = []
	for row in res:
		uu = fetch_uuid("K-ROW-%s-%s-%s" % (row[1], row[2], row[3]), uuid_cache)
		thing['sources'].append([str(row[0]), uu, row[1], row[2], row[3]])
		ouu = fetch_uuid(str(row[4]), uuid_cache)
		thing['objects'].append({'uid': str(row[4]), 'uuid': ouu, 'label': row[5]})
	return thing

@use('gpi')
@use('uuid_cache')
def add_sale_people(thing: dict, gpi=None, uuid_cache=None):	
	s = 'SELECT s.sale_buyer_uid, p.person_label, p.person_ulan, s.sale_buyer_mod, s.sale_buyer_auth_mod ' + \
		'FROM knoedler_sale_buyers AS s, gpi_people as p ' + \
		'WHERE s.sale_event_id="%s" AND s.sale_buyer_uid=p.person_uid' % thing['uid']
	buyers = []
	res = gpi.execute(s)
	for row in res:
		uu = fetch_uuid(row[0], uuid_cache)
		atype = get_actor_type(str(row[2]), uuid_cache)
		buyers.append({'uuid': uu, 'ulan': row[2], 'type': atype, 'label': str(row[1]), 'mod': row[3], 'auth_mod': row[4]})
	thing['buyers'] = buyers

	s = 'SELECT s.sale_seller_uid, p.person_label, p.person_ulan, s.sale_seller_share ' + \
		'FROM knoedler_sale_sellers AS s, gpi_people as p ' + \
		'WHERE s.sale_event_id="%s" AND s.sale_seller_uid=p.person_uid' % thing['uid']
	sellers = []
	res = gpi.execute(s)
	for row in res:
		uu = fetch_uuid(row[0], uuid_cache)
		atype = get_actor_type(str(row[2]), uuid_cache)
		sellers.append({'uuid': uu, 'type': atype, 'ulan': row[2], 'label': str(row[1]), 'share': row[3]})
	thing['sellers'] = sellers
	return thing

@use('gpi')
@use('uuid_cache')
def add_sale_thing(thing: dict, gpi=None, uuid_cache=None):
	s = 'SELECT k.star_record_no, k.stock_book_no, k.page_number, k.row_number, k.object_id, n.title ' + \
		'FROM knoedler as k, knoedler_object_titles as n ' + \
		'WHERE k.object_id = n.object_id AND n.is_preferred_title = 1 AND k.sale_event_id="%s"' % thing['uid']
	res = gpi.execute(s)
	thing['sources'] = []
	thing['objects'] = []
	for row in res:
		uu = fetch_uuid("K-ROW-%s-%s-%s" % (row[1], row[2], row[3]), uuid_cache)
		thing['sources'].append([str(row[0]), uu, row[1], row[2], row[3]])
		ouu = fetch_uuid(str(row[4]), uuid_cache)
		thing['objects'].append({'uid': str(row[4]), 'uuid':ouu, 'label': row[5]})
	return thing



@use('raw')
def find_raw(*row, raw=None):
	(recno, obj_id, inv_id, sale_id, purch_id) = row
	s = 'SELECT * FROM raw_knoedler WHERE pi_record_no="%s"' % recno
	res = raw.execute(s)
	t = list(res.fetchone())
	t.extend([obj_id, inv_id, sale_id, purch_id])
	return tuple(t)

def make_missing_purchase_data(data: dict):
	# This is the raw data from the export, as Matt screwed up the processing for purchases :(
	# Entry date is the inventory date

	def process_amount(amnt):
		if not amnt:
			return amnt
		amnt = amnt.replace('[', '')
		amnt = amnt.replace(']', '')
		amnt = amnt.replace('?', '')
		amnt = amnt.strip()
		try:
			return float(amnt)
		except:
			print("Could not process %s when decimalizing" % amnt)
			return None

	currencies = {
		"pounds": 300411998,
		"dollars": 300411994,
		"francs": 300412016,
		"marks": 300412169,
		"dollar": 300411994,
		"florins": 300412160,
		"thalers": 300412168,
		"lire": 300412015,
		"Swiss francs":300412001,
		None: None
	}


	seller1 = {'name': data['seller_name_1'], 'loc': data['seller_loc_1'], 'loc_auth': data['seller_auth_loc_1'], 
		'mod': data['seller_mod_1'], 'mod_auth': data['seller_auth_mod_1'], 'ulan': data['seller_ulan_1']}
	seller2 = {'name': data['seller_name_2'], 'loc': data['seller_loc_2'], 'loc_auth': data['seller_auth_loc_2'], 
		'mod': data['seller_mod_2'], 'mod_auth': data['seller_auth_mod_2'], 'ulan': data['seller_ulan_2']}


	knoedler = {'label': "Knoedler", 'type': 'Group', 'share': None, 'uuid': 'c19d4bfc-0375-4994-98f3-0659cffc40d8'}

	return {
		'uid': 'rob-%s-%s' % (data['pi_id'], data['MATT_inventory_id']),
		"amount": data['purchase_amount'],
		'dec_amount': process_amount(data['purchase_amount']),
		'currency_aat': currencies[data['purchase_currency']],
		"currency": data['purchase_currency'],
		'k_amount': data['knoedler_purchase_amount'],
		'k_curr': data['knoedler_purchase_currency'],
		'dec_k_amount': process_amount(data['knoedler_purchase_amount']),
		'k_curr_aat': currencies[data['knoedler_purchase_currency']],
		"note": data['purchase_note'],
		'k_note': data['knoedler_purchase_note'],
		'year': data['entry_date_year'],
		'month': data['entry_date_month'],
		'day': data['entry_date_day'],
		"sellers": [seller1, seller2],
		'buyers': [knoedler],
		"object_id": data['MATT_object_id'],
		"inventory_id": data['MATT_inventory_id'],
		"pi_id": data['pi_id'],
		"star_id": data['star_id'],
		"transaction_type": data['transaction'],
		'sources': [],
		'objects': [],
		'sale_event_id': data['MATT_sale_event_id'],
		'purchase_event_id': data['MATT_purchase_event_id']
	}


@use('gpi')
@use('uuid_cache')
def make_missing_shared(data: dict, gpi=None, uuid_cache=None):
	# Generate our UUID
	data['uuid'] = fetch_uuid(data['uid'], uuid_cache)

	# Build the object reference (just UUID and label)
	s = "SELECT title FROM knoedler_object_titles WHERE is_preferred_title=1 AND object_id = '%s'" % (data['object_id'])		
	res = gpi.execute(s)
	label = res.fetchone()[0]
	data['objects'] = [{'uuid': fetch_uuid(data['object_id'], uuid_cache), 'label': label}]

	# String to Int / Date conversions
	if not data['day']:
		data['day'] = 1
	else:
		data['day'] = int(data['day'])
	if not data['month']:
		data['month'] = 1
	else:
		data['month'] = int(data['month'])			
	if data['year']:
		data['year'] = int(data['year'])

	# Add Source
	s = 'SELECT k.stock_book_no, k.page_number, k.row_number FROM knoedler as k ' \
		'WHERE k.pi_record_no = "%s"' % data['pi_id']
	res =  gpi.execute(s)
	(book, page, row) = res.fetchone()
	uu = fetch_uuid("K-ROW-%s-%s-%s" % (book, page, row), uuid_cache)
	data['sources'] = [[None, uu, book, page, row]]

	return data


@use('gpi')
@use('uuid_cache')
def make_missing_purchase(data: dict, gpi=None, uuid_cache=None):
	if data['transaction_type'] == "Unsold" and not data['amount'] and not data['note'] and not data['sellers'][0]['name']:
		# Inventory
		return None	
	else:

		# Calculate Knoedler amount
		k_amnt = data['dec_k_amount']
		k_curr = data['k_curr_aat']
		amnt = data['dec_amount']
		curr = data['currency_aat']
		if k_amnt is not None and k_amnt != amnt and k_curr == curr:
			data['buyers'][0]['share'] = k_amnt / amnt
		else:
			data['buyers'][0]['share'] = 1.0

		# Clean up Sellers
		# Find people by: (1) check ULAN
		# Then: (2) Seems like Matt generated people that he didn't use.
		# And thus there are ids for the sellers, with reference to the row.

		new_sellers = []
		for sell in data['sellers']:
			if sell['name'] is None and sell['ulan'] is None:
				continue
			if sell['ulan'] is not None:
				s = "SELECT person_uid, person_label FROM gpi_people WHERE person_ulan = %s" % (sell['ulan'])
			else:
				s = "SELECT DISTINCT names.person_uid, names.person_name as uid " \
					"FROM gpi_people_names_references as ref, gpi_people_names as names " \
					'WHERE ref.person_name_id = names.person_name_id AND ref.source_record_id = "KNOEDLER-%s" and ' \
					'names.person_name = "%s"' % (data['star_id'], sell['name'])

			res = gpi.execute(s)
			rows = res.fetchall()
			if len(rows) == 1:
				(puid, plabel) = rows[0]
				puu = fetch_uuid(puid, uuid_cache)
				ptyp = get_actor_type(sell['ulan'], uuid_cache)
			else:
				print("Sent: %s Got: %s" % (sell['name'], len(rows)))
				continue
			new_sellers.append({'type': ptyp, 'uuid': puu, 'label': plabel, 'mod': ''})
		data['sellers'] = new_sellers

		return data


def make_inventory(data: dict):
	if data['transaction_type'] != "Unsold" or data['amount'] or data['note'] or data['sellers'][0]['name']:
		# purchase
		return None	
	else:
		# pass through to make_la_inventory
		return data


# ~~~~ People Tables ~~~~

@use('gpi')
@use('uuid_cache')
def add_person_names(thing: dict, gpi=None, uuid_cache=None):
	s = 'SELECT * FROM gpi_people_names WHERE person_uid="%s"' % (thing['uid'])
	thing['names'] = []
	for r in gpi.execute(s):
		name = [r[0]]
		nid = r[2]
		# s2 = 'SELECT source_record_id from gpi_people_names_references WHERE 
		#    person_name_id=%r' % (nid,)
		s2 = 'SELECT k.star_record_no, k.stock_book_no, k.page_number, k.row_number ' \
			'FROM knoedler AS k, gpi_people_names_references AS ref WHERE k.star_record_no ' \
			'= ref.source_record_id AND ref.person_name_id=%r' % (nid,)
		for r2 in gpi.execute(s2):
			# uid, book, page, row
			val = [r2[0]]

			uu = fetch_uuid("K-ROW-%s-%s-%s" % (r2[1], r2[2], r2[3]), uuid_cache)		
			val.append(uu)
			val.append([r2[1], r2[2], r2[3]])
			name.append(val)
		thing['names'].append(name)
	return thing

@use('gpi')
def add_person_aat_labels(data: dict, gpi=None):
	if data['aat_nationality_1']:
		data['aat_nationality_1_label'] = get_aat_label(data['aat_nationality_1'], gpi=gpi)
	if data['aat_nationality_2']:
		data['aat_nationality_2_label'] = get_aat_label(data['aat_nationality_2'], gpi=gpi)
	if data['aat_nationality_3']:
		data['aat_nationality_4_label'] = get_aat_label(data['aat_nationality_3'], gpi=gpi)
	return data

@use('gpi')
@use('uuid_cache')
def add_person_locations(data: dict, gpi=None, uuid_cache=None):
	# XXX Should probably have referred to by from the record
	# XXX This should be a fan, not an add

	places = {}
	fields = ['loc', 'recno', 'book', 'page', 'row']
	fields2 = ['loc', 'auth', 'recno', 'book', 'page', 'row']

	s = "SELECT s.purchase_seller_loc, k.star_record_no, k.stock_book_no, k.page_number, k.row_number " + \
		" FROM knoedler_purchase_sellers as s, knoedler as k " + \
		" WHERE s.purchase_seller_uid ='%s' AND s.purchase_event_id = k.purchase_event_id" % data['uid']
	for row in gpi.execute(s):
		if row[0]:
			pl = dict(zip(fields, row))
			print(pl)
			# hohum, get source info...
			uu = fetch_uuid("K-ROW-%s-%s-%s" % (pl['book'], pl['page'], pl['row']), uuid_cache)
			source = [pl['recno'], uu, pl['book'], pl['page'], pl['row']]
			if pl['loc'] in places:
				places[pl['loc']].append(source)
			else:
				places[pl['loc']] = [source]

	s = 'SELECT s.sale_buyer_loc, s.sale_buyer_addr, k.star_record_no, k.stock_book_no, k.page_number, k.row_number ' + \
		' FROM knoedler_sale_buyers as s, knoedler as k ' + \
		" WHERE sale_buyer_uid = '%s' AND s.sale_event_id = k.sale_event_id" % data['uid']
	for row in gpi.execute(s):
		if row[0] or row[1]:
			pl = dict(zip(fields2, row))
			print(pl)
			uu = fetch_uuid("K-ROW-%s-%s-%s" % (pl['book'], pl['page'], pl['row']), uuid_cache)
			source = [pl['recno'], uu, pl['book'], pl['page'], pl['row']]
			if pl['auth'] in places:
				places[pl['auth']].append(source)
			else:
				places[pl['auth']] = [source]
			# if pl['loc'] in places, then merge refs
			if pl['loc'] in places:
				places[pl['auth']].extend(places[pl['loc']])
				del places[pl['loc']]

	data['places'] = [{"label": k, "sources": v} for (k,v) in places.items()]
	return data

def clean_dates(data: dict):
	data['birth_clean'] = date_cleaner(data['birth'])
	data['death_clean'] = date_cleaner(data['death'])
	return data


# ~~~~ Stock Book ~~~~

def make_stock_books(*thing):
	# make baseline
	uid = thing[0]
	return {'uid': 'K-BOOK-%s' % uid, 'identifier': uid}

@use('gpi')
def fan_pages(thing: dict, gpi=None):
	# For each incoming book, find all the pages
	s = 'SELECT DISTINCT page_number, link, main_heading, subheading FROM knoedler WHERE stock_book_no = %s ORDER BY page_number' % (thing['identifier'])
	for r in gpi.execute(s):
		page = {'parent': thing, 'identifier': r[0], 'image': r[1], 'heading': r[2], 'subheading': r[3], 
			'uid': 'K-PAGE-%s-%s' % (thing['identifier'], r[0])}
		yield page

@use('gpi')
def fan_rows(thing: dict, gpi=None):
	# For each incoming book, find all the pages
	s = 'SELECT DISTINCT row_number, star_record_no, pi_record_no, description, working_note, verbatim_notes ' + \
		'FROM knoedler WHERE stock_book_no = %s AND page_number = %s ORDER BY row_number' % \
		(thing['parent']['identifier'], thing['identifier'])
	for r in gpi.execute(s):
		row = {'parent': thing, 'identifier': r[0], 'star_id': r[1], 'pi_id': r[2], 'description': r[3],
			'working': r[4], 'verbatim': r[5],
			'uid': 'K-ROW-%s-%s-%s' % (thing['parent']['identifier'], thing['identifier'], r[0])}
		yield row





