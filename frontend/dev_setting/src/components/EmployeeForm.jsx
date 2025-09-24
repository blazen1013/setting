import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

const statusLabelMap = {
  WORKING: '근무중',
  AWAY: '자리비움',
  OUT_ON_BUSINESS: '외근',
  OFF_WORK: '퇴근',
};

export default function EmployeeForm({ employee, onSubmit, statusOptions }) {
  const [formState, setFormState] = useState({
    name: '',
    email: '',
    mobile: '',
    status: '',
    password: '',
  });

  useEffect(() => {
    if (employee) {
      setFormState({
        name: employee.name,
        email: employee.email,
        mobile: employee.mobile,
        status: employee.status?.status ?? '',
        password: '',
      });
    } else {
      setFormState({
        name: '',
        email: '',
        mobile: '',
        status: '',
        password: '',
      });
    }
  }, [employee]);

  if (!employee) {
    return <p>직원을 선택하면 상세 정보를 수정할 수 있습니다.</p>;
  }

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const payload = {
      name: formState.name,
      email: formState.email,
      mobile: formState.mobile,
      status: formState.status || null,
      password: formState.password || null,
    };
    onSubmit(payload);
  };

  return (
    <section className="form-section">
      <h2>선택한 직원 정보 수정</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">이름</label>
          <input id="name" name="name" value={formState.name} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label htmlFor="email">이메일</label>
          <input id="email" name="email" type="email" value={formState.email} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label htmlFor="mobile">휴대폰</label>
          <input id="mobile" name="mobile" value={formState.mobile} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label htmlFor="status">상태</label>
          <select id="status" name="status" value={formState.status} onChange={handleChange}>
            <option value="">선택 안 함</option>
            {statusOptions.map((option) => (
              <option key={option} value={option}>
                {statusLabelMap[option] ?? option}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="password">새 비밀번호 (옵션)</label>
          <input
            id="password"
            name="password"
            type="password"
            value={formState.password}
            onChange={handleChange}
            placeholder="8자 이상 입력"
            minLength={8}
          />
        </div>

        <button type="submit">저장하기</button>
      </form>
    </section>
  );
}

EmployeeForm.propTypes = {
  employee: PropTypes.shape({
    emp_id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired,
    mobile: PropTypes.string.isRequired,
    status: PropTypes.shape({
      status: PropTypes.string,
    }),
  }),
  onSubmit: PropTypes.func.isRequired,
  statusOptions: PropTypes.arrayOf(PropTypes.string).isRequired,
};
