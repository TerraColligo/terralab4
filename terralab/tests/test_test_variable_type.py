from odoo.tests.common import TransactionCase

class TestTestVariableType(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestTestVariableType, self).setUp(*args, **kwargs)
    # Create test type to use in tests
    #self.demo_user = self.env.ref('base.user_demo')
    TestType = self.env['terralab.testtype']#.sudo(self.demo_user)
    self.test_type_1 = TestType.create({
      'sample_types': [],
      'spreadsheet': None,
      'default_code': 'test_type_1',
      'name': 'Test Type 1',
      'test_products': [],
      'test_result_uom_name': 'uom',
    })

  def test_create_test_variable_type(self):
    """Create a test variable type"""
    TestVariableType = self.env['terralab.testvariabletype']#.sudo(self.demo_user)
    test_variable_type_1 = TestVariableType.create({
      'spreadsheet': None,
      'test_type': self.test_type_1.id,
      'num': 1,
      'name': 'Test Variable Type 1',
    })
    self.assertEqual(test_variable_type_1.num, 1)
    self.assertEqual(test_variable_type_1.name, 'Test Variable Type 1')
