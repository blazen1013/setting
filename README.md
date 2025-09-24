# Colink 협업 플랫폼 초기 프로젝트

이 저장소는 FastAPI 백엔드와 React 프론트엔드를 이용하여 직원의 상태와 연락처 정보를 관리하는 애플리케이션의 초기 구성을 제공합니다. MySQL `collab_platform` 데이터베이스 스키마를 기반으로 직원의 상태(근무중, 자리비움, 외근, 퇴근)와 이름, 이메일, 휴대폰, 비밀번호를 수정할 수 있습니다.

## 백엔드 (FastAPI)

- 위치: [`backend/app`](backend/app)
- 주요 기능
  - `/employees` : 직원 목록과 최신 상태 조회
  - `/employees/{emp_id}` : 직원 정보, 상태, 비밀번호 갱신
  - `/employee-status-options` : 사용 가능한 상태 값 조회
  - `/health` : 헬스체크
- ORM: SQLAlchemy (기존 테이블과 연결되며 `employee_status` 보조 테이블 자동 생성)
- 비밀번호: Bcrypt 해시(passlib) 사용
- CORS: 기본적으로 `http://localhost:5173`, `http://localhost:3000` 허용. `.env` 로 오버라이드 가능

### 실행 방법

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 환경 설정 수정
uvicorn app.main:app --reload
```

MySQL 접속 정보는 `.env` 의 `DATABASE_URL` 에 `mysql+pymysql://<사용자>:<비밀번호>@<호스트>:<포트>/<DB>` 형태로 설정합니다.

## 프론트엔드 (React + Vite)

- 위치: [`frontend`](frontend)
- 직원 목록, 상태, 연락처, 비밀번호 수정 UI 제공
- API 호출은 기본적으로 `http://localhost:8000` FastAPI 서버를 사용하며 `.env` 로 조정 가능

### 실행 방법

```bash
cd frontend
npm install
cp .env.example .env  # 필요 시 API 주소 변경
npm run dev
```

개발 서버 실행 후 `http://localhost:5173` 에 접속하면 UI 를 확인할 수 있습니다.

## 데이터베이스 준비

아래 테이블은 이미 준비된 `collab_platform` 데이터베이스 정의입니다. FastAPI 애플리케이션은 여기에 `employee_status` 테이블을 추가로 생성하여 직원의 최신 상태를 저장합니다.

```
CREATE TABLE employee_status (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    emp_id INT NOT NULL,
    status ENUM('WORKING','AWAY','OUT_ON_BUSINESS','OFF_WORK') NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_employee_status_emp (emp_id),
    FOREIGN KEY (emp_id) REFERENCES employee(emp_id)
);
```

## 개발 시 주의 사항

- 비밀번호는 평문으로 저장하지 않고 반드시 API 를 통해 해시 처리합니다.
- API 요청 시 필수 값(name, email, mobile)은 항상 포함되어야 합니다.
- 프론트엔드에서 상태를 선택하지 않으면 기존 상태가 유지됩니다.

## 향후 개선 아이디어

- 인증/인가 및 감사 로그 연동
- 상태 변경 이력 테이블 구축 (현재는 최신 상태만 저장)
- 테스트 코드 및 CI 파이프라인 추가
