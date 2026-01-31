import React from 'react';
import { Outlet } from 'react-router-dom';
import { DoctorSidebar } from './DoctorSidebar';
import { Header } from './Header';

export function DoctorLayout() {
  return (
    <div className="flex min-h-screen bg-background">
      <DoctorSidebar />
      <div className="flex-1 flex flex-col">
        <Header userName="Dr. Sharma" userRole="doctor" showSearch={true} />
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
