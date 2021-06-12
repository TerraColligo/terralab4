from odoo.tests.common import TransactionCase

class TestSubmittedTestVariable(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestSubmittedTestVariable, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')
    SampleType = self.env['terralab.sampletype']#.sudo(self.demo_user)
    TestType = self.env['terralab.testtype']#.sudo(self.demo_user)
    SubmittedSample = self.env['terralab.submittedsample']#.sudo(self.demo_user)
    TestVariableType = self.env['terralab.testvariabletype']#.sudo(self.demo_user)
    SubmittedTest = self.env['terralab.submittedtest']#.sudo(self.demo_user)
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
    self.test_variable_type_1 = TestVariableType.create({
      'spreadsheet': None,
      'test_type': self.test_type_1.id,
      'num': 1,
      'name': 'Test Variable Type 1',
    })
    self.submitted_test_1 = SubmittedTest.create({
      'order': None,
      'test_type': self.test_type_1.id,
      'order_line': None,
      'submitted_sample': self.submitted_sample_1.id,
      'test_result': '123',
      'test_result_uom_name': 'result_uom',
    })

  def test_create_submitted_test_variable(self):
    SubmittedTestVariable = self.env['terralab.submittedtestvariable']#.sudo(self.demo_user)
    submitted_test_variable_1 = SubmittedTestVariable.create({
      'submitted_sample': self.submitted_sample_1.id,
      'submitted_test': self.submitted_test_1.id,
      'test_variable_type': self.test_variable_type_1.id,
      'value': '1',
    })
    self.assertEqual(submitted_test_variable_1.value, '1')
    self.assertEqual(submitted_test_variable_1.name, '%s %s' % (self.submitted_test_1.name_get()[0][1], self.test_variable_type_1.name))
