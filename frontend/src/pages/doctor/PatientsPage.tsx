import React from 'react';
import { Search, Plus, MoreVertical, Filter } from 'lucide-react';
import { Card, CardContent, Button, Badge, Input } from '../../components/ui';

// Placeholder patients data
const patients = [
  { id: 'P001', name: 'Rajesh Kumar', age: 45, gender: 'Male', prakriti: 'Vata-Pitta', lastVisit: '2 days ago', status: 'Active Treatment', condition: 'Amavata' },
  { id: 'P002', name: 'Priya Sharma', age: 32, gender: 'Female', prakriti: 'Pitta-Kapha', lastVisit: '1 week ago', status: 'Follow-up', condition: 'Skin disorder' },
  { id: 'P003', name: 'Amit Patel', age: 58, gender: 'Male', prakriti: 'Kapha', lastVisit: '3 days ago', status: 'New Patient', condition: 'Prameha' },
  { id: 'P004', name: 'Sunita Devi', age: 41, gender: 'Female', prakriti: 'Vata', lastVisit: '5 days ago', status: 'Active Treatment', condition: 'Anxiety' },
  { id: 'P005', name: 'Vikram Singh', age: 52, gender: 'Male', prakriti: 'Pitta', lastVisit: 'Today', status: 'Consultation', condition: 'Digestive issues' },
  { id: 'P006', name: 'Meera Reddy', age: 28, gender: 'Female', prakriti: 'Vata-Kapha', lastVisit: '2 weeks ago', status: 'Completed', condition: 'Migraine' },
];

const statusColors: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'error'> = {
  'Active Treatment': 'primary',
  'Follow-up': 'warning',
  'New Patient': 'info',
  'Consultation': 'success',
  'Completed': 'default' as 'primary',
};

export function PatientsPage() {
  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-bold text-text-primary">Patients</h1>
          <p className="text-text-secondary">Manage your patient records</p>
        </div>
        <Button leftIcon={<Plus size={18} />}>
          Add Patient
        </Button>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" size={18} />
              <input
                type="text"
                placeholder="Search patients by name, ID, or condition..."
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-200 bg-surface focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
              />
            </div>
            <Button variant="outline" leftIcon={<Filter size={18} />}>
              Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Patients Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left py-4 px-6 font-medium text-text-primary">Patient</th>
                <th className="text-left py-4 px-6 font-medium text-text-primary">Age/Gender</th>
                <th className="text-left py-4 px-6 font-medium text-text-primary">Prakriti</th>
                <th className="text-left py-4 px-6 font-medium text-text-primary">Condition</th>
                <th className="text-left py-4 px-6 font-medium text-text-primary">Status</th>
                <th className="text-left py-4 px-6 font-medium text-text-primary">Last Visit</th>
                <th className="text-left py-4 px-6 font-medium text-text-primary">Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((patient) => (
                <tr key={patient.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                        <span className="text-primary font-medium">
                          {patient.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{patient.name}</p>
                        <p className="text-sm text-text-secondary">ID: {patient.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-6 text-text-secondary">
                    {patient.age} yrs / {patient.gender}
                  </td>
                  <td className="py-4 px-6">
                    <Badge variant="primary" size="sm">{patient.prakriti}</Badge>
                  </td>
                  <td className="py-4 px-6 text-text-secondary">{patient.condition}</td>
                  <td className="py-4 px-6">
                    <Badge variant={statusColors[patient.status]} size="sm">
                      {patient.status}
                    </Badge>
                  </td>
                  <td className="py-4 px-6 text-text-secondary">{patient.lastVisit}</td>
                  <td className="py-4 px-6">
                    <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                      <MoreVertical size={18} className="text-text-secondary" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination placeholder */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100">
          <p className="text-sm text-text-secondary">Showing 1-6 of 247 patients</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled>Previous</Button>
            <Button variant="outline" size="sm">Next</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
