from odoo.tests.common import TransactionCase

class TestTargetUse(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestTargetUse, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')

  def test_create_target_use(self):
    """Create a target use"""
    TargetUse = self.env['terralab.targetuse']#.sudo(self.demo_user)
    target_use_1 = TargetUse.create({
      'spreadsheet': None,
      'default_code': 'target_use_1',
      'name': 'Target Use 1',
    })
    self.assertEqual(target_use_1.default_code, 'target_use_1')
    self.assertEqual(target_use_1.name, 'Target Use 1')
