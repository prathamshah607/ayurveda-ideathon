import React from 'react';
import { Outlet } from 'react-router-dom';
import { PatientSidebar } from './PatientSidebar';
import { Header } from './Header';

export function PatientLayout() {
  return (
    <div className="flex min-h-screen bg-background">
      <PatientSidebar />
      <div className="flex-1 flex flex-col">
        <Header userName="Rahul Kumar" userRole="patient" showSearch={false} />
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
