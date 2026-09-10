# ecoarchive-impact2026 — 환경아카이브 풀숲 소장현황 분석

재단법인 숲과나눔이 운영하는 환경아카이브 풀숲(https://ecoarchive.org)의 Omeka 데이터베이스 전수(111,106건, 2026-09-10)를 분석해 컬렉션·시간·주제·지역·키워드의 관점에서 소장현황을 보여주는 정적 사이트입니다.

사이트: https://archivelabedu.github.io/ecoarchive-impact2026/

## 구조

```
data/        집계 JSON (사이트가 그리는 데이터, CC BY 4.0)
templates/   Jinja2 페이지 템플릿
content/     방법·소개 마크다운
assets/      CSS, ECharts 헬퍼
scripts/     수집·집계·빌드 스크립트
docs/        빌드 산출물 (GitHub Pages)
```

## 재현

```bash
python3 -m venv venv && venv/bin/pip install pandas jinja2 markdown
venv/bin/python scripts/omeka_api_pull.py <API_KEY>     # Omeka REST API 전수 수집
venv/bin/python scripts/omeka_full_build.py             # 평탄화·파생 필드
venv/bin/python scripts/site_data.py                    # data/*.json 생성
venv/bin/python scripts/build.py                        # docs/ 빌드
```

macOS에서 한글 소스 실행 시 `LC_ALL=en_US.UTF-8`을 설정하십시오.

## 라이선스

- 집계 데이터·그래프: CC BY 4.0
- 소스코드: MIT
- 원자료의 저작권은 각 기증주체와 재단법인 숲과나눔에 있으며 풀숲 이용약관을 따릅니다.
