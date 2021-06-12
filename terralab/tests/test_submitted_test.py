from odoo.tests.common import TransactionCase
from datetime import datetime

class TestSubmittedTest(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestSubmittedTest, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')
    SampleType = self.env['terralab.sampletype']#.sudo(self.demo_user)
    TestType = self.env['terralab.testtype']#.sudo(self.demo_user)
    SubmittedSample = self.env['terralab.submittedsample']#.sudo(self.demo_user)
    self.sample_type_1 = SampleType.create({
      'spreadsheet': None,
      'default_code': 'sample_type_1',
      'name': 'Sample Type 1',
    })
    self.test_type_1 = TestType.create({
      'spreadsheet': None,
      'default_code': 'test_type_1',
      'name': 'Test Type 1',
      'test_result_uom_name': 'uom',
    })
    self.submitted_sample_1 = SubmittedSample.create({
      'sample_type': self.sample_type_1.id,
      'order': None,
      'serial_number': 'ABC123',
      'name': 'Submitted Sample 1',
      'sample_id': 'SS1',
      'status': 'new',
      'area': 1,
      'volume': 2,
      'location': '1,1',
    })

  def test_create_submitted_test(self):
    """Create a submitted test"""
    SubmittedTest = self.env['terralab.submittedtest']#.sudo(self.demo_user)
    submitted_test_1 = SubmittedTest.create({
      'order': None,
      'test_type': self.test_type_1.id,
      'order_line': None,
      'submitted_sample': self.submitted_sample_1.id,
      'test_result': '123',
      'test_result_uom_name': 'result_uom',
    })
    self.assertEqual(submitted_test_1.test_type_name, self.test_type_1.name)
    self.assertEqual(submitted_test_1.order_name, False)
    self.assertEqual(submitted_test_1.order_terralab_status, False)
    self.assertEqual(submitted_test_1.sample_group, '(no order) - (no order status) - Sample Type 1 - SS1')
    self.assertEqual(submitted_test_1.test_result, '123')
    self.assertEqual(submitted_test_1.test_result_uom_name, 'result_uom')
    #self.assertEqual(submitted_test_1.var_1, None)
    #self.assertEqual(submitted_test_1.var_1_type, '')
    #self.assertEqual(submitted_test_1.var_1_value, '')
    #self.assertEqual(submitted_test_1.var_2, None)
    #self.assertEqual(submitted_test_1.var_2_type, '')
    #self.assertEqual(submitted_test_1.var_2_value, '')
    #self.assertEqual(submitted_test_1.var_3, '')
    #self.assertEqual(submitted_test_1.var_3_type, '')
    #self.assertEqual(submitted_test_1.var_3_value, '')
