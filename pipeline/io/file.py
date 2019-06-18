import os
import os.path
import hashlib
import uuid

from pipeline.util import CromObjectMerger

from bonobo.config import Configurable, Option
from pipeline.util import ExclusiveValue
from cromulent import model, reader

class FileWriter(Configurable):
	directory = Option(default="output")

	def __call__(self, data: dict):
		d = data['_OUTPUT']
		dr = os.path.join(self.directory, data['_ARCHES_MODEL'])
		if not os.path.exists(dr):
			os.mkdir(dr)
		uu = data.get('uuid')
		if not uu:
			uu = str(uuid.uuid4())
			print(f'*** No UUID in top-level resource. Using an assigned UUID filename for the content: {uu}')
		fn = os.path.join(dr, "%s.json" % uu)
		fh = open(fn, 'w')
		fh.write(d)
		fh.close()
		return data

class MultiFileWriter(Configurable):
	directory = Option(default="output")

	def __call__(self, data: dict):
		d = data['_OUTPUT']
		uu = data.get('uuid')
		if not uu:
			uu = str(uuid.uuid4())
			print(f'*** No UUID in top-level resource. Using an assigned UUID filename for the content: {uu}')
		dr = os.path.join(self.directory, data['_ARCHES_MODEL'])
		with ExclusiveValue(dr):
			if not os.path.exists(dr):
				os.mkdir(dr)
		ddr = os.path.join(dr, uu)
		with ExclusiveValue(ddr):
			if not os.path.exists(ddr):
				os.mkdir(ddr)
			h = hashlib.md5(d.encode('utf-8')).hexdigest()
			fn = os.path.join(ddr, "%s.json" % (h,))
			if not os.path.exists(fn):
				fh = open(fn, 'w')
				fh.write(d)
				fh.close()
			return data

class MergingFileWriter(Configurable):
	directory = Option(default="output")

	def __call__(self, data: dict):
		d = data['_OUTPUT']
		dr = os.path.join(self.directory, data['_ARCHES_MODEL'])
		merger = CromObjectMerger()
		with ExclusiveValue(dr):
			if not os.path.exists(dr):
				os.mkdir(dr)
			uu = data.get('uuid')
			if not uu:
				uu = str(uuid.uuid4())
				print(f'*** No UUID in top-level resource. Using an assigned UUID filename for the content: {uu}')
			fn = os.path.join(dr, "%s.json" % uu)
			if os.path.exists(fn):
				r = reader.Reader()
				with open(fn, 'r') as fh:
					content = fh.read()
					try:
						m = r.read(content)
						n = r.read(d)
# 						print('========================= MERGING =========================')
# 						print('merging objects:')
# 						print(f'- {m}')
# 						print(f'- {n}')
						merger.merge(m, n)
					except model.DataError:
						print(f'Exception caught while merging data from {fn}:')
						print(d)
						print(content)
						raise

					factory = data['_CROM_FACTORY']
					d = factory.toString(m, False)
			fh = open(fn, 'w')
			fh.write(d)
			fh.close()
			return data
