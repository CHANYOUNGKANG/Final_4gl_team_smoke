# ㈜스모크 회사 홈페이지

`index.html` 한 파일로 열린다(외부 폰트·이미지·스크립트 없음 → 발표장 오프라인 가능).

- 슬라이드·카드 그림은 SVG로 그린 장면이다. 원근선을 계산해야 해서 `src/gen_site.py`가 `src/template.html`에 장면을 넣어 `index.html`을 만든다.
- 문구·레이아웃 수정: `src/template.html` 수정 → `python3 docs/site/src/gen_site.py docs/site/index.html`

## 글꼴

| 용도 | 글꼴 | 라이선스 |
| --- | --- | --- |
| 제목의 한글 | 가석원 **Gasoek One** | SIL OFL 1.1 |
| 제목의 영문·숫자 (SMOKE NET 등) | **Unbounded** | SIL OFL 1.1 |
| 본문 | **IBM Plex Sans KR** | SIL OFL 1.1 |

- 페이지에 쓰인 글자만 남긴 서브셋을 `src/fonts.css`에 base64로 넣어 `index.html`에 포함한다(약 115KB). 인터넷이 없어도 같은 글꼴로 보인다.
- 문구를 바꿔 새 글자가 생기면 글꼴을 다시 만든다:
  ```bash
  cd docs/site/src
  npm pack @fontsource/gasoek-one @fontsource/unbounded @fontsource/ibm-plex-sans-kr   # 임시 폴더에서
  for f in *.tgz; do mkdir -p "${f%.tgz}" && tar xzf "$f" -C "${f%.tgz}"; done
  pip install fonttools brotli
  python3 gen_site.py ../index.html && python3 build_fonts.py <압축 푼 폴더> ../index.html && python3 gen_site.py ../index.html
  ```
