from odoo.tests.common import TransactionCase
from datetime import datetime

# This is the primary test, which uses all other objects to create an order.

class TestOrder(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestOrder, self).setUp(*args, **kwargs)
    self.now = datetime.utcnow()
    #self.demo_user = self.env.ref('base.user_demo')
    User = self.env['res.users']#.sudo(self.demo_user)
    SampleType = self.env['terralab.sampletype']#.sudo(self.demo_user)
    TestType = self.env['terralab.testtype']#.sudo(self.demo_user)
    SubmittedSample = self.env['terralab.submittedsample']#.sudo(self.demo_user)
    TestVariableType = self.env['terralab.testvariabletype']#.sudo(self.demo_user)
    SubmittedTest = self.env['terralab.submittedtest']#.sudo(self.demo_user)
    TestCategory = self.env['product.category']#.sudo(self.demo_user)
    TestProduct = self.env['product.template']#.sudo(self.demo_user)
    # We need to create an empty order already here to refer to it
    self.customer = User.search([])[0]
    Order = self.env['sale.order']#.sudo(self.demo_user)
    self.order_1 = Order.create({
      'partner_id': self.customer.id,
    })
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
    self.test_type_2 = TestType.create({
      'spreadsheet': None,
      'default_code': 'test_type_2',
      'name': 'Test Type 2',
      'test_result_uom_name': 'uom',
    })
    self.test_variable_type_1 = TestVariableType.create({
      'spreadsheet': None,
      'test_type': self.test_type_1.id,
      'num': 1,
      'name': 'Test Variable Type 1',
    })
    self.test_variable_type_2 = TestVariableType.create({
      'spreadsheet': None,
      'test_type': self.test_type_1.id,
      'num': 2,
      'name': 'Test Variable Type 2',
    })
    self.test_variable_type_3 = TestVariableType.create({
      'spreadsheet': None,
      'test_type': self.test_type_2.id,
      'num': 1,
      'name': 'Test Variable Type 3',
    })
    self.test_category_1 = TestCategory.create({
      'terralab_spreadsheet': None,
      'terralab_default_code': 'test_category_1',
      'name': 'Test Category 1',
    })
    self.test_product_1 = TestProduct.create({
      'default_code': 'test_product_1',
      'name': 'Test Product 1',
      'terralab_spreadsheet': None,
      'terralab_test_types': [self.test_type_1.id, self.test_type_2.id],
    })
    self.submitted_sample_1 = SubmittedSample.create({
      'sample_type': self.sample_type_1.id,
      'order': self.order_1.id,
      'test_products': [self.test_product_1.id],
      'serial_number': 'ABC123',
      'name': 'Submitted Sample 1',
      'sample_id': 'SS1',
      'status': 'new',
      'area': 1,
      'volume': 2,
      'location': '1,1',
    })

  def test_create_order(self):
    self.order_1.write({
      'terralab_report_text_1': 'Boilerplate 1',
      'terralab_report_text_2': 'Boilerplate 2',
      'terralab_report_text_3': 'Boilerplate 3',
      'terralab_report_text_4': 'Boilerplate 4',
    })
    self.assertEqual(self.order_1.terralab_report_text_1, 'Boilerplate 1')
    self.assertEqual(self.order_1.terralab_report_text_2, 'Boilerplate 2')
    self.assertEqual(self.order_1.terralab_report_text_3, 'Boilerplate 3')
    self.assertEqual(self.order_1.terralab_report_text_4, 'Boilerplate 4')
    self.assertEqual(self.order_1.terralab_status, 'draft')
    self.assertEqual(self.order_1.terralab_submitted_samples_count, 1)
    self.assertEqual(self.order_1.terralab_submitted_tests_count, 2)
    self.assertEqual(self.order_1.terralab_submitted_test_variables_count, 3)
    self.assertEqual(self.order_1.terralab_next_action, 'Submit order')
    self.assertEqual(self.order_1.terralab_draft_date.date(), self.now.date())
    self.assertEqual(self.order_1.terralab_submitted_date, False)
    self.assertEqual(self.order_1.terralab_accepted_date, False)

    # Check submitted samples
    self.assertEqual(self.order_1.terralab_submitted_samples[0].sample_type.id, self.sample_type_1.id)
    self.assertEqual(self.order_1.terralab_submitted_samples[0].create_date, self.order_1.create_date)

    # Check generated order lines
    self.assertEqual(self.order_1.order_line[0].terralab_submitted_sample.id, self.order_1.terralab_submitted_samples[0].id)
    self.assertEqual(self.order_1.order_line[0].terralab_submitted_tests[0].test_type.id, self.test_type_1.id)
    self.assertEqual(self.order_1.order_line[0].terralab_submitted_tests[1].test_type.id, self.test_type_2.id)

    # Check submitted tests
    self.assertEqual(self.order_1.terralab_submitted_tests[0].test_type.id, self.test_type_1.id)
    self.assertEqual(self.order_1.terralab_submitted_tests[0].var_1_type.id, self.test_variable_type_1.id)
    self.assertEqual(self.order_1.terralab_submitted_tests[0].var_2_type.id, self.test_variable_type_2.id)
    self.assertEqual(self.order_1.terralab_submitted_tests[1].test_type.id, self.test_type_2.id)
    self.assertEqual(self.order_1.terralab_submitted_tests[1].var_1_type.id, self.test_variable_type_3.id)

    # Check submitted test variables
    self.assertEqual(self.order_1.terralab_submitted_test_variables[0].test_variable_type.id, self.test_variable_type_1.id)
    self.assertEqual(self.order_1.terralab_submitted_test_variables[0].order_name, self.order_1.name)
    self.assertEqual(self.order_1.terralab_submitted_test_variables[0].num, 1)
    self.assertEqual(self.order_1.terralab_submitted_test_variables[1].test_variable_type.id, self.test_variable_type_2.id)
    self.assertEqual(self.order_1.terralab_submitted_test_variables[1].order_name, self.order_1.name)
    self.assertEqual(self.order_1.terralab_submitted_test_variables[1].num, 2)
    self.assertEqual(self.order_1.terralab_submitted_test_variables[2].test_variable_type.id, self.test_variable_type_3.id)
    self.assertEqual(self.order_1.terralab_submitted_test_variables[2].order_name, self.order_1.name)
    self.assertEqual(self.order_1.terralab_submitted_test_variables[2].num, 1)

    # Submit order
    self.order_1.action_terralab_submit()
    self.assertEqual(self.order_1.terralab_status, 'submitted')
    self.assertEqual(self.order_1.terralab_submitted_date.date(), self.now.date())

    # Accept order
    self.order_1.action_terralab_accept()
    self.assertEqual(self.order_1.terralab_status, 'accepted')
    self.assertEqual(self.order_1.terralab_accepted_date.date(), self.now.date())
