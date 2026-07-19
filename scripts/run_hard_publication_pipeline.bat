@echo off
setlocal
cd /d "%~dp0\.."

echo === Hard benchmark: RAW (resumable) ===
python -m quorum --config config_hard.yaml eval data/pairs/hard_benchmark --input-mode raw --resume-from results/hard_raw_checkpoint.json --checkpoint results/hard_raw_checkpoint.json
if errorlevel 1 exit /b %errorlevel%

echo === Promote raw checkpoint ===
python -c "import json; from pathlib import Path; p=Path('results/hard_raw_checkpoint.json'); d=json.loads(p.read_text(encoding='utf-8')); d['partial']=False; Path('results/run_hard_raw_final.json').write_text(json.dumps(d, indent=2), encoding='utf-8'); print(len(d['results']), 'pairs')"

echo === Hard benchmark: STRUCTURED (resumable) ===
python -m quorum --config config_hard.yaml eval data/pairs/hard_benchmark --input-mode structured --resume-from results/hard_structured_checkpoint.json --checkpoint results/hard_structured_checkpoint.json
if errorlevel 1 exit /b %errorlevel%

echo === Promote structured checkpoint ===
python -c "import json; from pathlib import Path; p=Path('results/hard_structured_checkpoint.json'); d=json.loads(p.read_text(encoding='utf-8')); d['partial']=False; Path('results/run_hard_structured_final.json').write_text(json.dumps(d, indent=2), encoding='utf-8'); print(len(d['results']), 'pairs')"

echo === Publication package ===
python -m quorum publication-eval --cooper-raw results/run_20260718T182612Z_cooper_raw.json --cooper-structured results/run_20260718T182612Z_cooper_structured.json --hard-raw results/run_hard_raw_final.json --hard-structured results/run_hard_structured_final.json --pairs-dir data/pairs
echo DONE
