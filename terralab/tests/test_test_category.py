from odoo.tests.common import TransactionCase

class TestTestCategory(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestTestCategory, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')

  def test_create_test_category(self):
    """Create a test category"""
    TestCategory = self.env['product.category']#.sudo(self.demo_user)
    test_category_1 = TestCategory.create({
      'terralab_spreadsheet': None,
      'terralab_default_code': 'test_category_1',
      'name': 'Test Category 1',
    })
    self.assertEqual(test_category_1.terralab_default_code, 'test_category_1')
    self.assertEqual(test_category_1.name, 'Test Category 1')
