"""Deterministic BM25 evidence retrieval with stable source hashes and exact offsets.
This retrieves evidence; it neither generates answers nor establishes factual truth.
"""
from collections import Counter
import hashlib,json,math,re

def tokens(text):return re.findall(r'\w+',text.casefold(),re.UNICODE)

def analyze(data):
    docs=data['documents'];query=data['query'];limit=int(data.get('limit',5));size=int(data.get('chunkWords',120));overlap=int(data.get('overlapWords',20))
    if not isinstance(query,str) or not tokens(query):raise ValueError('query must contain at least one word')
    if not isinstance(docs,list) or not docs:raise ValueError('Provide a non-empty documents list')
    if not 1<=limit<=50 or not 20<=size<=1000 or not 0<=overlap<size:raise ValueError('Invalid retrieval settings')
    ids=set();chunks=[];sources=[]
    for d in docs:
        sid=d['id'];text=d['text']
        if not isinstance(sid,str) or sid in ids:raise ValueError('Document IDs must be unique strings')
        if not isinstance(text,str):raise ValueError('Document text must be a string')
        ids.add(sid);sha=hashlib.sha256(text.encode()).hexdigest();sources.append({'id':sid,'sha256':sha,'characters':len(text)})
        words=list(re.finditer(r'\S+',text))
        for start in range(0,len(words),size-overlap):
            stop=min(start+size,len(words));a,b=words[start].start(),words[stop-1].end();excerpt=text[a:b]
            chunks.append({'source':sid,'sourceSha256':sha,'start':a,'end':b,'text':excerpt,'terms':Counter(tokens(excerpt))})
            if stop==len(words):break
    if not chunks:raise ValueError('Documents contain no searchable text')
    N=len(chunks);avg=sum(sum(c['terms'].values()) for c in chunks)/N;df=Counter()
    for c in chunks:df.update(c['terms'].keys())
    q=set(tokens(query));scored=[]
    for c in chunks:
        length=sum(c['terms'].values());score=0
        for term in q:
            f=c['terms'][term]
            if f:
                idf=math.log(1+(N-df[term]+.5)/(df[term]+.5));score+=idf*(f*2.2)/(f+1.2*(.25+.75*length/max(avg,1)))
        if score>0:scored.append({k:v for k,v in c.items() if k!='terms'}|{'score':round(score,8),'matchedTerms':sorted(q&c['terms'].keys())})
    scored.sort(key=lambda c:(-c['score'],c['source'],c['start']))
    # Suppress heavily overlapping excerpts from the same source.
    selected=[]
    for c in scored:
        if any(c['source']==s['source'] and max(0,min(c['end'],s['end'])-max(c['start'],s['start']))/max(1,min(c['end']-c['start'],s['end']-s['start']))>.5 for s in selected):continue
        selected.append(c)
        if len(selected)>=limit:break
    matched=set(t for c in selected for t in c['matchedTerms'])
    return {'product':'EvidenceKit','version':'0.1.0','summary':{'documents':len(docs),'chunks':N,'evidence':len(selected),'queryTermCoverage':len(matched)/len(q)},'evidence':selected,'unmatchedTerms':sorted(q-matched),'sources':sources,'findings':[] if selected else [{'severity':'warning','code':'no_evidence','detail':'No lexical evidence matched this query. Abstain rather than infer.'}],'limitations':['Lexical BM25 retrieval, not semantic search or an LLM answer generator.','Scores and query-term coverage are not probabilities of truth.','Conflicting documents are returned as evidence; contradiction detection is not implemented.','Offsets use Unicode code points in the original text, not UTF-8 byte offsets.']}
