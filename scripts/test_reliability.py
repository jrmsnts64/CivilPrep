import copy, unittest, datetime as dt
import seasonal_update as season
from quality_audit import audit, numeric

class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.bank=season.load_js('questions.js')
    def test_existing_bank(self):
        d=audit(self.bank);self.assertEqual(d['records'],590);self.assertEqual(d['mathChecked'],d['numericalRecords'])
    def test_bad_answer(self):
        q=copy.deepcopy(next(q for q in self.bank if q['id']==101));q['answer']=(q['answer']+1)%4
        with self.assertRaises(ValueError):numeric(q)
    def test_duplicate(self):
        bank=copy.deepcopy(self.bank); rows=[q for q in bank if q['category']=='Clerical Skills'];a,b=rows[:2]
        for k in ('question','choices','answer','explanation'):b[k]=copy.deepcopy(a[k])
        with self.assertRaisesRegex(ValueError,'Exact duplicate'):audit(bank)
    def test_seasonal_candidates(self):
        season.NOW=dt.datetime.now(season.PH).isoformat();bank=self.bank
        for cycle in ('2027-03-14','2027-08-08'):
            pack=season.candidates(bank,cycle);self.assertEqual(len(pack['replacements']),20)
            lookup={x['replaceId']:x['question'] for x in pack['replacements']};new=[lookup.get(q['id'],q) for q in bank];audit(new)
    def test_unavailable_reference_preserves_previous_hash(self):
        from unittest.mock import patch
        season.NOW='test';old={'sources':[{'name':'CSC advisories','hash':'old','lastSuccessfulCheck':'previous'}]}
        with patch.object(season,'fetch',side_effect=OSError('unavailable')):
            sources,links,changed=season.monitor(old)
        c=sources[0];self.assertEqual(c['status'],'unavailable');self.assertEqual(c['hash'],'old');self.assertEqual(c['lastSuccessfulCheck'],'previous')
if __name__=='__main__':unittest.main()
