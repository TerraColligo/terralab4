from odoo.tests.common import TransactionCase

class TestSampleType(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestSampleType, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')

  def test_create_sample_type(self):
    """Create a sample type"""
    SampleType = self.env['terralab.sampletype']#.sudo(self.demo_user)
    sample_type_1 = SampleType.create({
      'spreadsheet': None,
      'default_code': 'sample_type_1',
      'name': 'Sample Type 1',
    })
    self.assertEqual(sample_type_1.default_code, 'sample_type_1')
    self.assertEqual(sample_type_1.name, 'Sample Type 1')
