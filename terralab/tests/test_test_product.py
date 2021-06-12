from odoo.tests.common import TransactionCase

class TestTestProduct(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestTestProduct, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')
    TestCategory = self.env['product.category']#.sudo(self.demo_user)
    self.test_category_1 = TestCategory.create({
      'terralab_spreadsheet': None,
      'terralab_default_code': 'test_category_1',
      'name': 'Test Category 1',
    })
    TestType = self.env['terralab.testtype']#.sudo(self.demo_user)
    self.test_type_1 = TestType.create({
      'sample_types': [],
      'spreadsheet': None,
      'default_code': 'test_type_1',
      'name': 'Test Type 1',
      'test_result_uom_name': 'uom',
    })
    self.test_type_2 = TestType.create({
      'sample_types': [],
      'spreadsheet': None,
      'default_code': 'test_type_2',
      'name': 'Test Type 2',
      'test_result_uom_name': 'uom',
    })

  def test_create_test_product(self):
    """Create a test product"""
    TestProduct = self.env['product.template']#.sudo(self.demo_user)
    test_product_1 = TestProduct.create({
      'default_code': 'test_product_1',
      'name': 'Test Product 1',
      'terralab_spreadsheet': None,
      'terralab_test_types': [self.test_type_1.id, self.test_type_2.id],
    })
    self.assertEqual(test_product_1.default_code, 'test_product_1')
    self.assertEqual(test_product_1.name, 'Test Product 1')
    self.assertEqual(test_product_1.terralab_test_types_count, 2)
