import PropTypes from 'prop-types';

function StatusTag({ status }) {
  if (!status) {
    return <span className="status-tag">상태 없음</span>;
  }
  const statusLabelMap = {
    WORKING: '근무중',
    AWAY: '자리비움',
    OUT_ON_BUSINESS: '외근',
    OFF_WORK: '퇴근',
  };
  return <span className="status-tag">{statusLabelMap[status.status] ?? status.status}</span>;
}

StatusTag.propTypes = {
  status: PropTypes.shape({
    status: PropTypes.string,
  }),
};

export default function EmployeeList({ employees, onSelect, selectedEmployeeId }) {
  return (
    <table className="employee-list">
      <thead>
        <tr>
          <th>직원번호</th>
          <th>이름</th>
          <th>이메일</th>
          <th>휴대폰</th>
          <th>상태</th>
        </tr>
      </thead>
      <tbody>
        {employees.map((employee) => (
          <tr
            key={employee.emp_id}
            onClick={() => onSelect(employee.emp_id)}
            style={{ backgroundColor: employee.emp_id === selectedEmployeeId ? '#dbeafe' : undefined }}
          >
            <td>{employee.emp_no}</td>
            <td>{employee.name}</td>
            <td>{employee.email}</td>
            <td>{employee.mobile}</td>
            <td>
              <StatusTag status={employee.status} />
            </td>
          </tr>
        ))}
        {employees.length === 0 && (
          <tr>
            <td colSpan={5}>등록된 직원이 없습니다.</td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

EmployeeList.propTypes = {
  employees: PropTypes.arrayOf(
    PropTypes.shape({
      emp_id: PropTypes.number.isRequired,
      emp_no: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      email: PropTypes.string.isRequired,
      mobile: PropTypes.string.isRequired,
      status: PropTypes.shape({
        status: PropTypes.string,
      }),
    })
  ),
  onSelect: PropTypes.func.isRequired,
  selectedEmployeeId: PropTypes.number,
};
