# 제출 체크리스트

## 미션 기능

- [x] FastAPI 일정 CRUD 및 입력 검증
- [x] 일정 Summary와 최근 추세 계산
- [x] AI 채팅에 최신 Summary 주입
- [x] 질문·답변 대화 기록 저장 및 다시 불러오기
- [x] Vanilla JavaScript 대시보드와 로딩·오류 상태
- [x] 일정 목록·수정·삭제, Summary 및 요일 그래프
- [x] JSON 내보내기와 다크 모드
- [x] 100개 이상 생성형 시연 일정과 dry-run
- [x] 백엔드 테스트 10개 통과
- [x] 프론트 테스트 6개 통과
- [x] 로컬 브라우저 스모크 시나리오 확인
- [x] README에 환경 변수 이름과 비밀값 관리 안내 기록

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

실제 배포 결과와 URL은 완료 후 이 체크리스트에 기록한다. 현재 공개 앱에는 사용자 인증이 없으므로 시연용 데이터만 사용한다.
