# Log

One entry for each recipe, selection or Track B model you train, newest at
the bottom. The numbers come from `experiments.csv`. "Why" and "what it means"
are in your own words: your agent asks you for them and does not make them up.
End the log with your plan for what to try next.

<!-- The form of an entry:

## <date> <tag> (Track A or B)
- changed: what is different from the run before
- why: your reason
- validation: 0.000 (before: 0.000)
- what it means: what you think the result says
-->

##10/29 사진보기
-부산: 바다, 다리, 항구 사진이 많음. 감천마을처럼 언덕에 집이 빽빽한 사진이 많음. 바다 앞 초고층 건물/ 해군, 군함 사진도 꽤 있음
-서울: 롯데타워, 한강다리, 궁궐, 한옥, 한글 간판, 지하철, 마스크 쓴 사람들 모인 사진이 많고 유적, 유물 사진이 많음
-도쿄: 도쿄 타워, 스카이트리, 신사, 도리이, 일본어 간판 라멘집, 자판기, 높은데서 본  스카이 라인, 네온 거리, 전철/기차 사진이 많음
-오사카: 도톤보리 같은 화려한 간판 거리, 일본 표지판, 편의점 약국, 역/플랫폼/전철 사진이 엄청 많음
-타이베이: 중정기념단, 붉은 사원/패루, 붉은 벽돌 옛 건물, 스쿠터, 번체 한자, MRT, 박물관 우뮬 사진이 유독 많음
-confusing pairs:
-photos with no city clues:
 부산: 자동차 외관이나 내부 사진이 너무 많음(모터쇼 행사 같음), 실내공연, 수족관, 기념 비석 등의 사진, 화재 현장 사진이 여러장 연속으로 있음.
 서울:박물관 유물, 자동차, 음식, 메달, 전시 포스터 사진이 있음.
 도쿄:음식, 꽃, 나무, 새, 전시작품, 악기연주, 게임기, 열기구 
 오사카: 음식/음료, 식당 실내, 화단/산책로, 스테인드글라스, 진열 상품, 조명 전시
 타이베이: 유물, 설명 패널, 히비스커스 꽃, 강아지, 흑백 감성 사진, 메달
 
## 29 Oct baseline (Track A)
- changed: 없음. 시작 레시피 그대로(batch 64, RandomResizedCrop + 좌우반전 + ColorJitter, AdamW 3e-4, OneCycle, label smoothing 0.1)이고 선택도 전체 44,257장 그대로.
- why: 시작점 성적을 잡고, 레시피는 그대로 둔 채 시드만 바꿨을 때 점수가 얼마나 흔들리는지 보려고 시드 0과 시드 1로 두 번 돌렸다.
- validation: 0.503 (시드 0), 0.488 (시드 1). 두 시드 평균 0.495. before: 없음(첫 실행)
- what it means: 생각보다 낮은 것 같다. 사진을 봤을 때 각 지역의 특징이 드러난 사진이 꽤 있었는데, 내가 생각한 것보다 특징이 드러나지 않았던 것 같기도 하다. 부산(시드 0 0.382, 시드 1 0.386)과 오사카(0.370, 0.363)는 도쿄(0.641, 0.618)와 타이베이(0.559, 0.521)보다 지역적 특색이 잘 안 드러난 것 같다. 도쿄와 타이베이는 그 지역 특색인 건물 사진이 많았는데, 부산은 사진으로 보았을 때 부산 바다라기보다는 바다 사진의 느낌이 강했고, 오사카도 일본 표지판이나 간판 거리 사진은 있었지만 오사카 사진이라고 판단하기는 어려웠을 것이라고 생각한다. 또 부산(5,191장)과 오사카(7,200장)는 사진 수가 적었다는 점도 이유가 될 수 있다. 레시피는 똑같고 시드만 바꿨는데 점수가 0.015 차이 났으므로, 앞으로 무언가를 바꿔서 0.015보다 적게 오르거나 내리면 그게 내가 바꾼 것 때문인지 그냥 운인지 알 수 없다. 확실하게 효과가 있다고 말하려면 이것보다 훨씬 크게 변해야 한다.
