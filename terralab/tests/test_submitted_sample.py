from odoo.tests.common import TransactionCase
from datetime import datetime
class TestSubmittedSample(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestSubmittedSample, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')
    SampleType = self.env['terralab.sampletype']#.sudo(self.demo_user)
    self.sample_type_1 = SampleType.create({
      'spreadsheet': None,
      'default_code': 'sample_type_1',
      'name': 'Sample Type 1',
    })

  def test_create_submitted_sample(self):
    """Create a submitted sample"""
    SubmittedSample = self.env['terralab.submittedsample']#.sudo(self.demo_user)
    now = datetime.utcnow()
    submitted_sample_1 = SubmittedSample.create({
      'sample_type': self.sample_type_1.id,
      'order': None,
      'serial_number': 'ABC123',
      'name': 'Submitted Sample 1',
      'sample_id': 'SS1',
      'status': 'new',
      'receive_date': now,
      'deadline': now,
      'area': 1,
      'volume': 2,
      'location': '1,1',
      'create_date': now,
    })
    self.assertEqual(submitted_sample_1.serial_number, 'ABC123')
    self.assertEqual(submitted_sample_1.num, 1)
    self.assertEqual(submitted_sample_1.name, 'Submitted Sample 1')
    self.assertEqual(submitted_sample_1.sample_id, 'SS1')
    self.assertEqual(submitted_sample_1.status, 'new')
    self.assertEqual(submitted_sample_1.receive_date, now)
    self.assertEqual(submitted_sample_1.deadline, now)
    self.assertEqual(submitted_sample_1.area, 1)
    self.assertEqual(submitted_sample_1.volume, 2)
    self.assertEqual(submitted_sample_1.location, '1,1')
    self.assertEqual(submitted_sample_1.create_date, now)
