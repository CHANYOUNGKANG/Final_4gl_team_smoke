# ㈜스모크 회사 홈페이지

`index.html` 한 파일로 열린다(외부 폰트·이미지·스크립트 없음 → 발표장 오프라인 가능).

- 슬라이드·카드 그림은 SVG로 그린 장면이다. 원근선을 계산해야 해서 `src/gen_site.py`가 `src/template.html`에 장면을 넣어 `index.html`을 만든다.
- 문구·레이아웃 수정: `src/template.html` 수정 → `python3 docs/site/src/gen_site.py docs/site/index.html`
