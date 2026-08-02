import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import './AdminLayout.css';

export default function AdminLayout() {
  return (
    <div className="admin-layout">
      <Sidebar />
      <div className="admin-layout-right">
        <TopBar />
        <main className="admin-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
