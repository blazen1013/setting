import { useEffect, useState } from 'react';
import axios from 'axios';
import EmployeeForm from './components/EmployeeForm.jsx';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000, // 무한 대기 방지
});

// 한국어 상태 매핑
const statusLabelMap = {
  WORKING: '근무중',
  AWAY: '자리비움',
  OUT_ON_BUSINESS: '외근',
  OFF_WORK: '퇴근',
};

export default function App() {
  const [me, setMe] = useState(null); // 로그인한 본인 정보
  const [statusOptions, setStatusOptions] = useState([]);

  const [authCredentials, setAuthCredentials] = useState(null); // { loginId, password }
  const [loginForm, setLoginForm] = useState({ loginId: '', password: '' });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  const clearSession = () => {
    setAuthCredentials(null);
    setMe(null);
    setSuccessMessage('');
  };

  const getAuthConfig = (credentials) => ({
    auth: {
      username: credentials.loginId,
      password: credentials.password,
    },
  });

  // 상태 옵션 불러오기
  const fetchStatusOptions = async () => {
    try {
      const res = await apiClient.get('/employee-status-options');
      // 백엔드에서 [{value,label}] or [string] 형태로 내려올 수 있음
      const opts = res.data?.options ?? [];
      const normalized = opts.map((o) =>
        typeof o === 'string' ? o : o.value ?? ''
      );
      setStatusOptions(normalized);
    } catch {
      setError('상태 정보를 불러오는데 실패했습니다.');
    }
  };

  // 내 정보 불러오기
  const fetchMe = async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get(
        '/employees/me',
        getAuthConfig(credentials)
      );
      setMe(res.data);
    } catch (err) {
      if (err.response?.status === 401) {
        setError('인증 정보가 올바르지 않습니다. 다시 로그인해주세요.');
        clearSession();
      } else if (err.response?.status === 403) {
        setError(err.response?.data?.detail || '접근 권한이 없습니다.');
      } else {
        setError('내 정보를 불러오는데 실패했습니다.');
      }
    } finally {
      setLoading(false);
    }
  };

  // 최초 로드 시 상태 옵션만
  useEffect(() => {
    fetchStatusOptions();
  }, []);

  // 로그인 성공/변경 시 내 정보 불러오기
  useEffect(() => {
    if (!authCredentials) return;
    fetchMe(authCredentials);
  }, [authCredentials]);

  // 로그인 폼 핸들러
  const handleLoginChange = (e) => {
    const { name, value } = e.target;
    setLoginForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleLoginSubmit = (e) => {
    e.preventDefault();
    const loginId = loginForm.loginId.trim();
    const password = loginForm.password;
    if (!loginId || !password) {
      setError('아이디와 비밀번호를 모두 입력해주세요.');
      return;
    }
    setError(null);
    setSuccessMessage('');
    setAuthCredentials({ loginId, password });
    setLoginForm({ loginId, password: '' });
  };

  // 로그아웃
  const handleLogout = () => {
    clearSession();
    setLoginForm({ loginId: '', password: '' });
    setError(null);
  };

  // 내 정보 수정
  const handleSubmit = async (payload) => {
    if (!authCredentials) {
      setError('세션이 만료되었습니다. 다시 로그인해주세요.');
      return;
    }
    if (!me) {
      setError('내 정보를 불러오지 못했습니다.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.put(
        '/employees/me',
        payload,
        getAuthConfig(authCredentials)
      );
      const updated = res.data;
      setMe(updated);
      setSuccessMessage('내 정보가 성공적으로 저장되었습니다.');
    } catch (err) {
      if (err.response?.status === 401) {
        clearSession();
        setError('세션이 만료되었습니다. 다시 로그인해주세요.');
      } else if (err.response?.status === 403) {
        setError(err.response?.data?.detail || '수정 권한이 없습니다.');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('저장 중 문제가 발생했습니다.');
      }
      setSuccessMessage('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>내 정보 관리</h1>

      {loading && <p>로딩 중...</p>}
      {error && <p className="error">{error}</p>}
      {successMessage && <p className="success">{successMessage}</p>}

      {!authCredentials ? (
        <section className="form-section">
          <h2>로그인</h2>
          <form onSubmit={handleLoginSubmit}>
            <div className="form-group">
              <label htmlFor="loginId">아이디</label>
              <input
                id="loginId"
                name="loginId"
                value={loginForm.loginId}
                onChange={handleLoginChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">비밀번호</label>
              <input
                id="password"
                name="password"
                type="password"
                value={loginForm.password}
                onChange={handleLoginChange}
                required
                minLength={4}
              />
            </div>
            <button type="submit" disabled={loading}>
              로그인
            </button>
          </form>
        </section>
      ) : (
        <>
          <div className="toolbar">
            <button type="button" onClick={handleLogout}>
              로그아웃
            </button>
          </div>

          {me ? (
            <>
              {me.status && (
                <span className="status-tag">
                  {statusLabelMap[me.status.status] ?? me.status.status}
                </span>
              )}

              <EmployeeForm
                key={me.emp_id}
                employee={me}
                onSubmit={handleSubmit}
                statusOptions={statusOptions}
              />
            </>
          ) : (
            <p>내 정보 불러오는 중...</p>
          )}
        </>
      )}
    </div>
  );
}
