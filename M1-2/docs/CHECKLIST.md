# 제출 체크리스트 — 미션 원문 대조

최종 점검일: 2026-10-26. 필수 기능 구현과 실제 검증 범위를 구분한다.

## 미션 기능

- [x] FastAPI 일정 CRUD 및 입력 검증
- [x] 일정 Summary와 최근 추세 계산
- [x] AI 채팅에 최신 Summary 주입
- [x] 질문·답변 대화 기록 저장 및 다시 불러오기
- [x] Vanilla JavaScript 대시보드와 로딩·오류 상태
- [x] 화면에서 일정 추가·목록·삭제, API에서 일정 수정, Summary 및 요일 그래프
- [x] JSON 내보내기와 다크 모드
- [x] 100개 이상 생성형 시연 일정과 dry-run
- [x] 백엔드 테스트 14개 통과
- [x] 프론트 테스트 8개 통과
- [x] 로컬 브라우저 스모크 시나리오 확인
- [x] README에 환경 변수 이름과 비밀값 관리 안내 기록
- [x] 요약 카드에 분석 기간·개수·트렌드 표시
- [x] 잘못된 부분 수정은 422이며 기존 데이터 유지
- [x] AI 요청당 출력 토큰 제한 및 공급자 오류 안내
- [x] 대화 복원 실패 시 기존 메시지 유지 및 오류 안내

## 제출 및 배포

- [x] GitHub 반영: https://github.com/hongbinwee/codyssey-m
- [x] Render backend 배포: https://myschedule-ai-api.onrender.com
- [x] Vercel frontend 배포: https://myschedule-ai.vercel.app
- [x] Backend, Swagger, Frontend URL 기입
- [x] Render `/health`·`/docs`·OpenAPI 및 Vercel 정적 파일 HTTP 200 확인
- [x] 실제 Vercel 두 origin의 CORS 허용 승인 및 적용
- [x] 허용 origin preflight HTTP 200 / 다른 origin HTTP 400 확인
- [x] 실제 배포 화면 스크린샷 3종 README에 추가
- [x] 배포 URL에서 일정 생성·새로고침 후 유지 및 API 수정·삭제 확인
- [x] 배포된 `/api/chat`에서 실제 AI 답변 1회와 자동 저장 확인
- [x] Vercel 화면에서 대화 선택·새로고침 후 메시지 복원 확인
- [x] 복원 검증 탭의 브라우저 오류 없음 및 CORS 확인

일정 삭제 확인창은 내장 브라우저 자동화가 멈춰 끝까지 조작하지 못했다. 삭제 API는 임시 일정 1건으로 검증했고, 새 화면에서 해당 일정이 사라지고 Summary가 복원된 것을 확인했다. AI 호출은 배포된 API에서 실행하고 실제 화면에서 저장된 질문·답변을 불러오는 방식으로 검증했다.

## 원문 항목별 근거

| 요구사항 | 확인 위치·근거 |
|---|---|
| Python 3.10+·venv·필수 패키지 | `backend/requirements.txt`, 로컬 venv 테스트 |
| 데이터 100개 이상·의미 있는 패턴 | seed dry-run 165개, 실제 Summary 100개 이상 확인 |
| FastAPI·CORS·Swagger | `app/main.py`, 배포 `/docs`·OpenAPI, origin별 preflight |
| Firestore·환경 변수 키 관리 | Repository와 core, 실제 CRUD·대화 저장; 비밀 파일 공개 제외 |
| 데이터 API 5개 | 배포 OpenAPI 5개 경로·메서드 확인, CRUD·Summary 테스트 |
| 대화 API 4개·전체 messages 조회 | 배포 OpenAPI, Repository, 대화 상세·화면 복원 |
| `/api/chat`·컨텍스트 주입·자동 저장 | Chat/Prompt/AI Service, fake 통합 테스트와 기존 실제 호출 |
| Vanilla UI·추가·삭제·요약·채팅·로딩·기록 | `frontend` 구현, 테스트·배포 화면 캡처 |
| Render·Vercel 고정 배포 | 두 실제 URL 공개 접속 및 최신 수정본 배포 확인 |
| README·환경 변수·스크린샷 3종 | `README.md`, `docs/screenshots/` |

## 제출 직전 수동 확인

- [ ] 일반 브라우저에서 본인이 추가한 임시 일정의 삭제 확인창을 승인하고 목록·요약 갱신 확인. 내장 브라우저 자동화에서 이 확인창만 완료하지 못했으며, 삭제 API·화면 삭제 로직 테스트는 통과했다.
- [ ] 미션 제출 화면에 GitHub M1-2 링크·Vercel 링크·Render/Swagger 링크 입력 및 제출. 외부 제출 자체는 수행하지 않았다.

선택 과제 중 그래프·추가 통계·JSON export·다크 모드는 구현했다. Function Calling·MCP/GPT Actions는 선택 항목으로 미구현이다. 현재 공개 앱은 인증·사용자별 데이터 분리가 없는 시연용 서비스다.
