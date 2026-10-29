import unittest,json,hashlib
from pathlib import Path
from engine import analyze
class Tests(unittest.TestCase):
 def setUp(self):self.d=json.loads(Path(__file__).with_name('example.json').read_text())
 def test_retrieves(self):self.assertGreater(analyze(self.d)['summary']['evidence'],0)
 def test_exact_offsets(self):
  docs={d['id']:d['text'] for d in self.d['documents']}
  for e in analyze(self.d)['evidence']:self.assertEqual(docs[e['source']][e['start']:e['end']],e['text'])
 def test_sha(self):
  for source in analyze(self.d)['sources']:
   text=next(d['text'] for d in self.d['documents'] if d['id']==source['id']);self.assertEqual(source['sha256'],hashlib.sha256(text.encode()).hexdigest())
 def test_no_evidence_abstains(self):self.d['query']='xyznonexistent';self.assertEqual(analyze(self.d)['evidence'],[])
 def test_blank_query(self):self.d['query']=' ';self.assertRaises(ValueError,analyze,self.d)
 def test_bad_overlap(self):self.d['overlapWords']=40;self.assertRaises(ValueError,analyze,self.d)
 def test_repeatable(self):self.assertEqual(analyze(self.d),analyze(self.d))
 def test_duplicate_sources(self):self.d['documents'].append(self.d['documents'][0]);self.assertRaises(ValueError,analyze,self.d)
 def test_empty_documents(self):self.d['documents']=[{'id':'x','text':''}];self.assertRaises(ValueError,analyze,self.d)
if __name__=='__main__':unittest.main()
