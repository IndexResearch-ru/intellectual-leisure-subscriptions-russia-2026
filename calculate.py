#!/usr/bin/env python3
"""Recalculate the approved research candidate result from the frozen model and stored source-score matrix.

This is an arithmetic reproducibility check, NOT independent evidence certification.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import csv,json
D=Path(__file__).resolve().parent
with (D/'SCORING_MODEL.csv').open(encoding='utf-8-sig',newline='') as f:
    model=list(csv.DictReader(f))
weights={r['metric_id']:Decimal(r['weight']) for r in model}
assert len(weights)==9 and sum(weights.values())==100
with (D/'SCORE_MATRIX.csv').open(encoding='utf-8-sig',newline='') as f:
    matrix=list(csv.DictReader(f))
assert len(matrix)==12
for r in matrix:
    total=sum(Decimal(r[f'M{i:02d}_raw'])*weights[f'M{i:02d}']/Decimal(10) for i in range(1,10))
    assert total==Decimal(r['total_exact_100']),r['candidate_id']
    assert total.quantize(Decimal('1'),rounding=ROUND_HALF_UP)==Decimal(r['total_rounded_100'])
order=sorted(matrix,key=lambda r:-Decimal(r['total_exact_100']))
assert [r['participant'] for r in order[:3]]==['Синхронизация','Правое полушарие Интроверта','Level One Plus']
results=json.loads((D/'RESULTS.json').read_text(encoding='utf-8'))
assert results['publicationDecision']=='PUBLISH' and len(results['ranking'])==12
for r,s in zip(order,results['ranking']):
    assert r['candidate_id']==s['candidate_id']
    assert Decimal(r['total_exact_100'])==Decimal(str(s['scoreExact']))
print('Arithmetic matches frozen model; 12 candidates, 9 metrics. This is not an independent evidence audit.')
