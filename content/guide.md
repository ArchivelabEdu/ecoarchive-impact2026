환경아카이브 풀숲의 기록으로 보드게임을 만들고 싶은 분을 위한 안내입니다. 코딩 경험이 없어도 됩니다. 아래 데이터는 모두 **키 없이, 브라우저에서 바로** 읽을 수 있고, 읽기만 가능하므로 원본 아카이브를 건드릴 일이 없습니다.

## 1. 무엇을 만들 수 있나

풀숲 데이터 랩이 먼저 만든 다섯 가지가 예시입니다. 모두 HTML 파일 하나로 되어 있고, 같은 카드 덱을 씁니다.

| 게임 | 규칙 한 줄 | 쓰는 데이터 |
|---|---|---|
| [에코폴리](../games/journey.html) | 1982→2025 말판을 주사위로 이동하며 도착한 해의 퀴즈 | 연도 카드 |
| [타임라인 카드배치](../games/timeline.html) | 사건·단체 카드를 연대순 줄의 올바른 자리에 끼워 넣기 | 사건·단체 카드 |
| [인물 스무고개](../games/who.html) | 힌트가 한 줄씩 열리는 인물·단체 맞히기 | 인물·단체 카드 |
| [컬렉션 룰렛](../games/roulette.html) | 특징 키워드 5개만 보고 어느 컬렉션인지 맞히기 | 컬렉션 카드 |
| [에코 도블](../games/photos.html) | 작품사진 4장을 작가·장소·사건과 짝 짓기 | 작품사진 카드 |

그 밖에 생각해 볼 만한 것: 카드 뒤집기 짝 맞추기(사건↔연도), 키워드 빙고, 지역별 사건 지도 퀴즈, 컬렉션 규모 순서 맞히기, 사진 촬영 연대 맞히기.

## 2. 데이터는 어디서 받나

세 가지 경로가 있습니다. 브라우저 게임이라면 **A만으로 충분**합니다.

### A. 카드 덱 JSON (권장)

게임용으로 미리 정리한 덱 두 개입니다. 주소를 그대로 `fetch`로 읽으면 됩니다.

| 파일 | 내용 | 주소 |
|---|---|---|
| cards.json | 235장: 사건 47 · 인물 68 · 단체 40 · 컬렉션 34 · 연도 46 | `https://archivelabedu.github.io/ecoarchive-impact2026/data/cards.json` |
| photo_cards.json | 작품사진 180장 (작가 46인) | `https://archivelabedu.github.io/ecoarchive-impact2026/data/photo_cards.json` |

**cards.json의 카드 종류와 필드** — 모든 카드에 `type`, `front`(이름), `url`(풀숲 원본 링크)이 있고, 종류별로 아래 필드가 더 있습니다.

| type | 필드 | 설명 |
|---|---|---|
| `event` (사건) | `year`, `end`, `subject`, `back`, `count`, `colls`, `image` | 시작·종료 연도, 주제, 설명, 관련 기록 수, 관련 컬렉션, 썸네일 |
| `person` (인물) | `role`, `hints`, `back`, `image` | 역할(사진작가·기증자), 힌트 목록, 설명, 썸네일(현재 없음) |
| `org` (단체) | `year`, `areas`, `count`, `hints`, `back` | 설립 연도, 활동영역 코드, 관련 기록 수, 힌트 목록, 설명 |
| `collection` (컬렉션) | `kind`, `keywords`, `count`, `year`, `back` | 단체/개인, 특징 키워드, 등록 건수, 최초 생산연도, 소개 |
| `year` (연도) | `year`, `count`, `keywords`, `top`, `events`, `orgs`, `chron` | 그 해 기록 수, 특징 키워드, 상위 키워드, 시작된 사건, 설립된 단체, 연표 건수 |

**photo_cards.json 필드** — `id`, `title`, `artist`, `year`, `region`(시도), `loc`(촬영지), `keywords`, `event`(연결된 사건), `org`, `lic`(라이선스), `image`, `url`.

**이미지 경로 규칙** — `image` 값은 `img/ev_1134.jpg`처럼 상대경로입니다. 앞에 `https://archivelabedu.github.io/ecoarchive-impact2026/games/` 를 붙여야 사진이 보입니다.

### B. 집계 데이터 JSON

데이터 랩의 그래프를 그리는 데 쓴 17개 파일입니다. 카드 덱보다 크고 구조가 다양해서, 통계형 게임(어느 해가 더 많을까, 키워드 순위 맞히기 등)에 씁니다. 목록과 필드 설명은 [데이터·방법](../data/index.html) 페이지에 있습니다. 주소는 `https://archivelabedu.github.io/ecoarchive-impact2026/data/파일이름.json` 입니다.

### C. 풀숲 Omeka API (고급)

원본 아카이브(ecoarchive.org)는 Omeka Classic으로 운영되며 REST API가 열려 있습니다. **공개 기록은 키 없이 읽을 수 있고, 키 없이는 아무것도 바꿀 수 없습니다.** 다만 브라우저에서 직접 호출하는 것은 막혀 있으므로(CORS 미허용), 파이썬 스크립트 등으로 데이터를 내려받아 정리하는 용도입니다.

```
https://ecoarchive.org/api/items?per_page=50&page=1
https://ecoarchive.org/api/items/1134
https://ecoarchive.org/api/collections
https://ecoarchive.org/api/files?item=1134
```

- 한 번에 최대 50건입니다. 전체(11만 건)를 받으면 2,200회가 넘는 요청이 되므로, 필요한 컬렉션이나 기간만 받고 결과를 파일로 저장해 다시 쓰세요.
- 원본 아카이브의 서버 부담을 줄이기 위해, 게임에서는 API를 실시간으로 부르지 말고 미리 내려받은 JSON을 쓰는 것이 원칙입니다.
- 자세한 사용법: [Omeka Classic API 문서](https://omeka.readthedocs.io/en/latest/Reference/api/)

## 3. 시작하기

1. **템플릿 복사** — [ecoarchive-vibe-template](https://github.com/ArchivelabEdu/ecoarchive-vibe-template) 저장소에서 **Use this template**을 눌러 내 리포지터리를 만듭니다. `index.html` 하나와 프롬프트 카드(`PROMPTS.md`)가 들어 있습니다.
2. **AI 코딩 도구 열기** — Claude Code, Codex 등 어느 것이든 좋습니다. 폴더를 열고 아래 준비 프롬프트를 먼저 넣습니다.

```
이 폴더의 index.html을 기준으로 작업할 거야. 파일은 index.html 하나만 쓰고, 외부 라이브러리는 CDN으로만 불러와.
데이터는 https://archivelabedu.github.io/ecoarchive-impact2026/data/cards.json 을 fetch로 읽어.
카드의 image 값은 상대경로라서 앞에 https://archivelabedu.github.io/ecoarchive-impact2026/games/ 를 붙여야 해.
한국어로, 모바일에서도 보이게 만들어 줘.
```

3. **게임 규칙을 한 문단으로** — 카드 몇 장을 뽑아, 무엇을 보여 주고, 무엇을 맞히면, 몇 점인지. 예시 프롬프트 다섯 개가 `PROMPTS.md`에 있습니다.
4. **작게 시작해 한 문장씩 늘리기** — 카드 4장, 1라운드부터. 되면 "6×6으로 늘려 줘", "2인용으로 바꿔 줘"처럼 하나씩 추가합니다.
5. **배포** — GitHub 리포지터리 → Settings → Pages → Branch `main`, 폴더 `/(root)`. 1~2분 뒤 `https://아이디.github.io/리포지터리이름/` 에서 열립니다.

## 4. 이용 조건

- **집계 데이터와 카드 덱**(A·B): CC BY 4.0. 출처를 밝히면 자유롭게 쓸 수 있습니다. 표기 예: `데이터: 재단법인 숲과나눔 환경아카이브 풀숲 · 풀숲 데이터 랩 (archivelabedu.github.io/ecoarchive-impact2026)`
- **사건 썸네일과 작품사진**: 각 기록의 라이선스를 따릅니다. 작품사진은 `lic` 필드에 라이선스가 적혀 있으며(공공누리·CC 등), 대부분 출처 표시 조건입니다. 사진을 잘라 쓰거나 색을 바꾸는 것은 "변경금지" 조건이면 안 됩니다. 게임 화면에 작가 이름과 풀숲 링크(`url`)를 함께 보여 주세요.
- **원본 기록의 본문**(C): 풀숲 각 기록 페이지에 표시된 이용 조건을 따릅니다.
- 상업적 이용이나 인쇄물 제작은 재단법인 숲과나눔에 먼저 문의해 주세요.

## 5. 자주 막히는 곳

| 증상 | 해결 |
|---|---|
| 카드가 안 보임 | 데이터 주소를 브라우저 주소창에 직접 열어 JSON이 보이는지 확인. `file://`로 연 페이지는 fetch가 막히므로 로컬 서버(`python3 -m http.server`)로 여세요 |
| 사진이 깨짐 | `image` 앞에 `…/games/` 경로를 붙였는지 확인 |
| 인물 카드에 사진이 없음 | 현재 `person`의 `image`는 모두 비어 있습니다. 실루엣이나 이니셜로 대신하세요 |
| Omeka API가 브라우저에서 안 됨 | 정상입니다(CORS 미허용). 스크립트로 내려받아 JSON으로 저장한 뒤 쓰세요 |
| 한글이 깨짐 | `<meta charset="utf-8">`를 넣어 달라고 하세요 |

## 6. 만든 게임 알려 주기

완성한 게임의 주소를 [데이터 랩 저장소 이슈](https://github.com/ArchivelabEdu/ecoarchive-impact2026/issues)에 남겨 주시면 이 페이지의 예시 목록에 추가합니다. 규칙 아이디어만 있어도 환영합니다.
