from odoo.tests.common import TransactionCase

class TestTestType(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestTestType, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')

  def test_create_test_type(self):
    """Create a test type"""
    TestType = self.env['terralab.testtype']#.sudo(self.demo_user)
    test_type_1 = TestType.create({
      'spreadsheet': None,
      'default_code': 'test_type_1',
      'name': 'Test Type 1',
      'test_result_uom_name': 'uom',
    })
    self.assertEqual(test_type_1.default_code, 'test_type_1')
    self.assertEqual(test_type_1.name, 'Test Type 1')
    self.assertEqual(test_type_1.test_result_uom_name, 'uom')
