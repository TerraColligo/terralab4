from odoo.tests.common import TransactionCase

class TestSpreadsheetImport(TransactionCase):
  def setUp(self, *args, **kwargs):
    super(TestSpreadsheetImport, self).setUp(*args, **kwargs)
    #self.demo_user = self.env.ref('base.user_demo')

  def test_spreadsheet_import(self):
    """Import existing spreadsheet"""
    Spreadsheet = self.env['terralab.spreadsheet']#.sudo(self.demo_user)
    spreadsheet = Spreadsheet.search([])[0]
    result = spreadsheet.action_import_tests_and_products()
    # Check that a valid action result was returned
    self.assertEqual(result['effect']['fadeout'], 'slow')
