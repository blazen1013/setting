import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import EmployeeList from './components/EmployeeList.jsx';
import EmployeeForm from './components/EmployeeForm.jsx';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default function App() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState(null);
  const [statusOptions, setStatusOptions] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');

  const selectedEmployee = useMemo(
    () => employees.find((employee) => employee.emp_id === selectedEmployeeId) ?? null,
    [employees, selectedEmployeeId]
  );

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/employees');
      setEmployees(response.data);
      if (!selectedEmployeeId && response.data.length > 0) {
        setSelectedEmployeeId(response.data[0].emp_id);
      }
      setError(null);
    } catch (err) {
      setError('직원 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatusOptions = async () => {
    try {
      const response = await apiClient.get('/employee-status-options');
      setStatusOptions(response.data.options);
    } catch (err) {
      setError('상태 정보를 불러오는데 실패했습니다.');
    }
  };

  useEffect(() => {
    fetchEmployees();
    fetchStatusOptions();
  }, []);

  const handleSelectEmployee = (empId) => {
    setSelectedEmployeeId(empId);
    setSuccessMessage('');
    setError(null);
  };

  const handleSubmit = async (payload) => {
    try {
      if (!selectedEmployee) {
        setError('먼저 직원을 선택해주세요.');
        return;
      }
      const response = await apiClient.put(`/employees/${selectedEmployee.emp_id}`, payload);
      setEmployees((prev) => prev.map((employee) => (employee.emp_id === response.data.emp_id ? response.data : employee)));
      setSuccessMessage('직원 정보가 성공적으로 저장되었습니다.');
      setError(null);
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('저장 중 문제가 발생했습니다.');
      }
      setSuccessMessage('');
    }
  };

  return (
    <div className="container">
      <h1>직원 상태 및 연락처 관리</h1>
      {loading && <p>로딩 중...</p>}
      {error && <p className="error">{error}</p>}
      {successMessage && <p className="success">{successMessage}</p>}
      <EmployeeList
        employees={employees}
        onSelect={handleSelectEmployee}
        selectedEmployeeId={selectedEmployeeId}
      />
      <EmployeeForm
        key={selectedEmployee?.emp_id ?? 'form'}
        employee={selectedEmployee}
        onSubmit={handleSubmit}
        statusOptions={statusOptions}
      />
    </div>
  );
}
