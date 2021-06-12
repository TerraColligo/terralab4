from odoo.tests.common import TransactionCase

class TestTargetUseRange(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestTargetUseRange, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')
    TargetUse = self.env['terralab.targetuse']#.sudo(self.demo_user)
    self.target_use_1 = TargetUse.create({
      'spreadsheet': None,
      'default_code': 'target_use_1',
      'name': 'Target Use 1',
    })
    TestType = self.env['terralab.testtype']#.sudo(self.demo_user)
    self.test_type_1 = TestType.create({
      'sample_types': [],
      'spreadsheet': None,
      'default_code': 'test_type_1',
      'name': 'Test Type 1',
      'test_products': [],
      'test_result_uom_name': 'uom',
    })

  def test_create_target_use_range(self):
    """Create a target use range"""
    TargetUseRange = self.env['terralab.targetuserange']#.sudo(self.demo_user)
    target_use_range_1 = TargetUseRange.create({
      'spreadsheet': None,
      'test_type': self.test_type_1.id,
      'target_use': self.target_use_1.id,
      'num_thresholds': 5,
      'threshold_1': 1,
      'threshold_2': 2,
      'threshold_3': 3,
      'threshold_4': 4,
      'threshold_5': 5,
    })
    self.assertEqual(target_use_range_1.name, '%s (%s)' % (self.target_use_1.name, self.test_type_1.name))
    self.assertEqual(target_use_range_1.num_thresholds, 5)
    self.assertEqual(target_use_range_1.threshold_1, 1)
    self.assertEqual(target_use_range_1.threshold_2, 2)
    self.assertEqual(target_use_range_1.threshold_3, 3)
    self.assertEqual(target_use_range_1.threshold_4, 4)
    self.assertEqual(target_use_range_1.threshold_5, 5)
