# ㈜스모크 회사 홈페이지

`index.html` 한 파일로 열린다(외부 폰트·이미지·스크립트 없음 → 발표장 오프라인 가능).

- 슬라이드·카드 그림은 SVG로 그린 장면이다. 원근선을 계산해야 해서 `src/gen_site.py`가 `src/template.html`에 장면을 넣어 `index.html`을 만든다.
- 문구·레이아웃 수정: `src/template.html` 수정 → `python3 docs/site/src/gen_site.py docs/site/index.html`

## 글꼴

**원티드 산스(Wanted Sans)** 한 가족만 쓴다 (SIL OFL 1.1). 제목은 SemiBold 600 + 좁은 자간, 본문은 Regular 400, 보조는 Medium 500. **700 이상 굵기는 쓰지 않는다.**

- 페이지에 쓰인 글자만 남긴 서브셋을 `src/fonts.css`에 base64로 넣어 `index.html`에 포함한다(약 100KB). 인터넷이 없어도 같은 글꼴로 보인다.
- 문구를 바꿔 새 글자가 생기면 글꼴을 다시 만든다:
  ```bash
  cd /tmp && npm pack wanted-sans && mkdir ws && tar xzf wanted-sans-*.tgz -C ws
  pip install fonttools brotli
  cd <저장소>/docs/site/src
  python3 gen_site.py ../index.html && python3 build_fonts.py /tmp/ws ../index.html && python3 gen_site.py ../index.html
  ```
