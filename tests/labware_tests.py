import unittest
import labware

class MicroplateTest(unittest.TestCase):

	expected_margin = 9 # ANSI standard.

	def setUp(self):
		self.plate = labware.Microplate()
		self.plate.calibrate(x=10, y=10, z=10)

	def a1_calibration_test(self):
		a1 = self.plate.well('A1').coordinates()
		self.assertEqual(a1, (10, 10, 10))

	def a2_coordinate_test(self):
		a2 = self.plate.well('A2').coordinates()
		self.assertEqual(a2, (10, 10+self.expected_margin, 10))

	def b1_coordinate_test(self):
		b1 = self.plate.well('B1').coordinates()
		self.assertEqual(b1, (10+self.expected_margin, 10, 10))

	def b2_coordinate_test(self):
		b2 = self.plate.well('B2').coordinates()
		margin = self.expected_margin
		self.assertEqual(b2, (10+margin, 10+margin, 10))

	def coordinate_lowercase_test(self):
		b2 = self.plate.well('b2').coordinates()
		margin = self.expected_margin
		self.assertEqual(b2, (10+margin, 10+margin, 10))

	def row_sanity_test(self):
		row = chr( ord('a') + self.plate.rows + 1 )
		with self.assertRaises(ValueError):
			self.plate.well('{}1'.format(row))

	def col_sanity_test(self):
		col = chr( self.plate.cols + 1 )
		with self.assertRaises(ValueError):
			self.plate.well('A{}'.format(col))

	def deck_calibration_test(self):

		m_offset = 10

		config = {
			'calibration': {
				'a1': {
					'type':'microplate_96',
					'x': m_offset,
					'y': m_offset,
					'z': m_offset
				}
			}
		}

		deck = labware.Deck(a1=labware.Microplate())
		deck.configure(config)

		margin = self.expected_margin

		plate = deck.slot('a1')

		a1 = plate.well('a1').coordinates()
		b2 = plate.well('b2').coordinates()

		self.assertEqual(a1, (m_offset, m_offset, m_offset))
		self.assertEqual(b2, (m_offset+margin, m_offset+margin, m_offset))

	def well_liquid_allocation_test(self):
		set_vol = 50
		# Add an initial value of 100ul water to this well.
		self.plate.well('A1').allocate(water=set_vol)
		vol = self.plate.well('A1').get_volume('water')
		self.assertEqual(vol, set_vol)

	def well_liquid_capacity_test(self):
		set_vol = 10000
		# Way too much water for a microplate!
		with self.assertRaises(ValueError):
			self.plate.well('A1').allocate(water=set_vol)

class TiprackTest(unittest.TestCase):

	expected_margin = 9 # ANSI standard.

	def setUp(self):
		self.rack = labware.Tiprack()
		self.rack.calibrate(x=10, y=10, z=10)

	def a1_calibration_test(self):
		a1 = self.rack.slot('A1').coordinates()
		self.assertEqual(a1, (10, 10, 10))

	def a2_coordinate_test(self):
		a2 = self.rack.slot('A2').coordinates()
		self.assertEqual(a2, (10, 10+self.expected_margin, 10))

	def b1_coordinate_test(self):
		b1 = self.rack.slot('B1').coordinates()
		self.assertEqual(b1, (10+self.expected_margin, 10, 10))

	def b2_coordinate_test(self):
		b2 = self.rack.slot('B2').coordinates()
		margin = self.expected_margin
		self.assertEqual(b2, (10+margin, 10+margin, 10))

	def coordinate_lowercase_test(self):
		b2 = self.rack.slot('b2').coordinates()
		margin = self.expected_margin
		self.assertEqual(b2, (10+margin, 10+margin, 10))

	def row_sanity_test(self):

		row = chr( ord('a') + self.rack.rows + 1 )
		with self.assertRaises(ValueError):
			self.rack.slot('{}1'.format(row))
		
		row = chr( ord('a') + self.rack.rows - 1 )
		self.rack.slot('{}1'.format(row))

	def col_sanity_test(self):

		col = self.rack.cols + 1

		with self.assertRaises(ValueError):
			self.rack.slot('A{}'.format(col))

		col = self.rack.cols
		self.rack.slot('A{}'.format(col))

	def deck_calibration_test(self):

		m_offset = 10

		config = {
			'calibration': {
				'a1': {
					'type':'tiprack_P2',
					'x': m_offset,
					'y': m_offset,
					'z': m_offset
				}
			}
		}

		deck = labware.Deck(a1=labware.Tiprack())
		deck.configure(config)

		margin = self.expected_margin

		rack = deck.slot('a1')

		a1 = rack.slot('a1').coordinates()
		b2 = rack.slot('b2').coordinates()

		self.assertEqual(a1, (m_offset, m_offset, m_offset))
		self.assertEqual(b2, (m_offset+margin, m_offset+margin, m_offset))

	def tip_inventory_test(self):

		self.assertEqual(self.rack.slot('a1').get_tip(), True)

		with self.assertRaises(Exception):
			self.rack.slot('a1').get_tip()

		""" Secondary syntax just in case. """

		slot = self.rack.slot('a2')
		self.assertEqual(slot.get_tip(), True)

		with self.assertRaises(Exception):
			slot.get_tip()