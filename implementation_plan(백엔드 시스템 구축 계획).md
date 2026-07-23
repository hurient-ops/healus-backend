# [Healus AI Cloud Platform] 백엔드 시스템 구축 계획

새로운 Healus 클라우드 서버 및 AI 연동을 위한 백엔드 시스템 구축의 첫 번째 단계(초기 뼈대 및 폴더 세팅) 구현 계획입니다.

## User Review Required

> [!IMPORTANT]
> **프로젝트 폴더 위치 확정**
> 새로운 백엔드 시스템은 기존 앱(`e:\projects\healus`)과 충돌하지 않도록, 독립적인 새로운 폴더인 `e:\projects\healus-backend`에 구축하려고 합니다. 이 위치가 괜찮으신지 확인 부탁드립니다.

## Open Questions

> [!WARNING]
> 1. 로컬 LLM 연동에 가장 유리한 **Python(FastAPI)과 PostgreSQL** 조합을 기본 스택으로 제안해 드립니다. 혹시 사내에서 선호하시는 다른 기술 스택(예: Node.js)이 있으시다면 말씀해 주세요.
> 2. 이번 단계에서는 앱에서 쏘는 데이터를 받을 수 있는 '서버 뼈대'만 먼저 구축할까요, 아니면 로그인(인증) 로직까지 한 번에 구축해 드릴까요?

## Proposed Changes

### 1. 백엔드 폴더 생성 및 Python 환경 세팅
- [NEW] `e:\projects\healus-backend` 디렉토리 생성
- [NEW] Python 가상환경(venv) 구성 및 `requirements.txt` 작성 (FastAPI, Uvicorn, SQLAlchemy, Pydantic, PyJWT 등 패키지 정의)

### 2. FastAPI 초기 프로젝트 구조(Architecture) 구축
- [NEW] `e:\projects\healus-backend\main.py` : 서버 구동 진입점 및 API 라우터 매핑
- [NEW] `e:\projects\healus-backend\api\` : API 엔드포인트 폴더 (환자 회원가입, 펌프 데이터 수집 API)
- [NEW] `e:\projects\healus-backend\core\` : 환경 변수, DB 연결 설정 및 JWT 보안/인증 로직
- [NEW] `e:\projects\healus-backend\models\` : 데이터베이스 테이블 스키마 정의 (Users 테이블, PumpData 시계열 테이블)

## Verification Plan

### Manual Verification
- 세팅 완료 후 서버(`uvicorn main:app --reload`)를 가동합니다.
- 브라우저에서 `http://localhost:8000/docs`에 접속하여, 회원가입 API와 펌프 데이터 수신 API가 시각적으로 잘 나타나는지 Swagger 문서를 통해 검증합니다.
