import PropTypes from 'prop-types';

const statusLabelMap = {
  WORKING: '근무중',
  AWAY: '자리비움',
  OUT_ON_BUSINESS: '외근',
  OFF_WORK: '퇴근',
};

export default function EmployeeList({ employees, onSelect, selectedEmployeeId }) {
  return (
    <table className="employee-list">
      <thead>
        <tr>
          <th>이름</th>
          <th>이메일</th>
          <th>휴대폰</th>
          <th>상태</th>
        </tr>
      </thead>
      <tbody>
        {employees.map((e) => (
          <tr
            key={e.emp_id}
            onClick={() => onSelect(e.emp_id)}
            style={{
              backgroundColor: e.emp_id === selectedEmployeeId ? '#e0f2fe' : 'transparent',
            }}
          >
            <td>{e.name}</td>
            <td>{e.email}</td>
            <td>{e.mobile}</td>
            <td>{statusLabelMap[e.status?.status] ?? e.status?.status ?? '-'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

EmployeeList.propTypes = {
  employees: PropTypes.arrayOf(
    PropTypes.shape({
      emp_id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      email: PropTypes.string.isRequired,
      mobile: PropTypes.string.isRequired,
      status: PropTypes.shape({
        status: PropTypes.string,
      }),
    })
  ).isRequired,
  onSelect: PropTypes.func.isRequired,
  selectedEmployeeId: PropTypes.number,
};
