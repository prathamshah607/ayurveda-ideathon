import React, { useState } from 'react';
import { Camera, Edit2, Save, X } from 'lucide-react';
import {
  Card,
  CardContent,
  Button,
  Input,
  Select,
  TagInput,
  ImageUpload,
  DoshaBarChart,
  Badge,
} from '../../components/ui';
import { Link } from 'react-router-dom';

export function PatientProfile() {
  const [isEditing, setIsEditing] = useState(false);
  const [tongueImage, setTongueImage] = useState<string | null>(null);
  const [nailImage, setNailImage] = useState<string | null>(null);

  // Placeholder profile data
  const [profile, setProfile] = useState({
    name: 'Rahul Kumar',
    email: 'rahul.kumar@email.com',
    age: '35',
    gender: 'male',
    height: '175',
    weight: '72',
    medicalHistory: ['Mild anxiety', 'Previous back injury'],
    familyHistory: ['Diabetes (Father)', 'Hypertension (Mother)'],
    currentMedications: ['Ashwagandha', 'Triphala'],
    allergies: ['None'],
    dietType: 'vegetarian',
    exerciseLevel: 'moderate',
    sleepHours: '7',
    stressLevel: 60,
  });

  const prakritiResult = {
    dominant: 'Vata-Pitta',
    breakdown: { vata: 45, pitta: 35, kapha: 20 },
    completedDate: 'January 10, 2026',
  };

  const bmi = (parseFloat(profile.weight) / Math.pow(parseFloat(profile.height) / 100, 2)).toFixed(1);

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-bold text-text-primary">My Profile</h1>
          <p className="text-text-secondary">Manage your health information</p>
        </div>
        <Button
          variant={isEditing ? 'primary' : 'outline'}
          leftIcon={isEditing ? <Save size={18} /> : <Edit2 size={18} />}
          onClick={() => setIsEditing(!isEditing)}
        >
          {isEditing ? 'Save Changes' : 'Edit Profile'}
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
              Basic Information
            </h2>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  disabled={!isEditing}
                />
                <Input
                  label="Email"
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  disabled={!isEditing}
                />
                <Input
                  label="Age"
                  type="number"
                  value={profile.age}
                  onChange={(e) => setProfile({ ...profile, age: e.target.value })}
                  disabled={!isEditing}
                />
                <Select
                  label="Gender"
                  options={[
                    { value: 'male', label: 'Male' },
                    { value: 'female', label: 'Female' },
                    { value: 'other', label: 'Other' },
                  ]}
                  value={profile.gender}
                  onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                  disabled={!isEditing}
                />
                <Input
                  label="Height (cm)"
                  type="number"
                  value={profile.height}
                  onChange={(e) => setProfile({ ...profile, height: e.target.value })}
                  disabled={!isEditing}
                />
                <Input
                  label="Weight (kg)"
                  type="number"
                  value={profile.weight}
                  onChange={(e) => setProfile({ ...profile, weight: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-text-secondary">Calculated BMI: </span>
                <span className="font-medium text-text-primary">{bmi}</span>
                <span className="text-sm text-text-secondary ml-2">
                  ({parseFloat(bmi) < 18.5 ? 'Underweight' : parseFloat(bmi) < 25 ? 'Normal' : parseFloat(bmi) < 30 ? 'Overweight' : 'Obese'})
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Health Data */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
              Health Data
            </h2>
            <CardContent className="space-y-4">
              <TagInput
                label="Medical History"
                value={profile.medicalHistory}
                onChange={(v) => setProfile({ ...profile, medicalHistory: v })}
                placeholder={isEditing ? 'Add conditions...' : ''}
              />
              <TagInput
                label="Family History"
                value={profile.familyHistory}
                onChange={(v) => setProfile({ ...profile, familyHistory: v })}
                placeholder={isEditing ? 'Add family conditions...' : ''}
              />
              <TagInput
                label="Current Medications"
                value={profile.currentMedications}
                onChange={(v) => setProfile({ ...profile, currentMedications: v })}
                placeholder={isEditing ? 'Add medications...' : ''}
              />
              <TagInput
                label="Allergies"
                value={profile.allergies}
                onChange={(v) => setProfile({ ...profile, allergies: v })}
                placeholder={isEditing ? 'Add allergies...' : ''}
              />
            </CardContent>
          </Card>

          {/* Lifestyle */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
              Lifestyle
            </h2>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <Select
                  label="Diet Type"
                  options={[
                    { value: 'vegetarian', label: 'Vegetarian' },
                    { value: 'vegan', label: 'Vegan' },
                    { value: 'non-vegetarian', label: 'Non-Vegetarian' },
                    { value: 'eggetarian', label: 'Eggetarian' },
                  ]}
                  value={profile.dietType}
                  onChange={(e) => setProfile({ ...profile, dietType: e.target.value })}
                  disabled={!isEditing}
                />
                <Select
                  label="Exercise Level"
                  options={[
                    { value: 'sedentary', label: 'Sedentary' },
                    { value: 'light', label: 'Light (1-2 times/week)' },
                    { value: 'moderate', label: 'Moderate (3-4 times/week)' },
                    { value: 'active', label: 'Active (5+ times/week)' },
                  ]}
                  value={profile.exerciseLevel}
                  onChange={(e) => setProfile({ ...profile, exerciseLevel: e.target.value })}
                  disabled={!isEditing}
                />
                <Input
                  label="Average Sleep (hours)"
                  type="number"
                  value={profile.sleepHours}
                  onChange={(e) => setProfile({ ...profile, sleepHours: e.target.value })}
                  disabled={!isEditing}
                />
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-1.5">
                    Stress Level
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={profile.stressLevel}
                      onChange={(e) => setProfile({ ...profile, stressLevel: parseInt(e.target.value) })}
                      disabled={!isEditing}
                      className="flex-1"
                    />
                    <span className="text-sm font-medium w-12">{profile.stressLevel}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Image Uploads */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
              Self-Assessment Images
            </h2>
            <CardContent className="grid md:grid-cols-2 gap-4">
              <ImageUpload
                label="Upload Tongue Photo"
                icon={<Camera size={18} className="text-primary" />}
                onImageSelect={(file) => setTongueImage(URL.createObjectURL(file))}
                previewUrl={tongueImage || undefined}
                onRemove={() => setTongueImage(null)}
                lastUploadDate="Jan 15, 2026"
                analysisStatus={tongueImage ? 'complete' : 'none'}
                onViewAnalysis={() => console.log('View tongue analysis')}
              />
              <ImageUpload
                label="Upload Nail Photo"
                icon={<Camera size={18} className="text-primary" />}
                onImageSelect={(file) => setNailImage(URL.createObjectURL(file))}
                previewUrl={nailImage || undefined}
                onRemove={() => setNailImage(null)}
                lastUploadDate="Jan 10, 2026"
                analysisStatus={nailImage ? 'complete' : 'none'}
                onViewAnalysis={() => console.log('View nail analysis')}
              />
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Prakriti */}
        <div className="space-y-6">
          {/* Prakriti Card */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-heading text-lg font-semibold text-text-primary">
                Your Constitution
              </h2>
              <Badge variant="primary">{prakritiResult.dominant}</Badge>
            </div>
            <CardContent>
              <DoshaBarChart breakdown={prakritiResult.breakdown} />
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-sm text-text-secondary">
                  Assessment completed: {prakritiResult.completedDate}
                </p>
                <Link to="/assessment/prakriti">
                  <Button variant="ghost" size="sm" className="mt-2">
                    Retake Quiz →
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Prakriti Quiz CTA (if not completed) */}
          <Card className="bg-gradient-to-br from-primary/5 to-accent/5 border-primary/20">
            <CardContent className="text-center py-6">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🧘</span>
              </div>
              <h3 className="font-heading text-lg font-semibold text-text-primary mb-2">
                Discover Your Constitution
              </h3>
              <p className="text-sm text-text-secondary mb-4">
                Take our Prakriti assessment quiz to understand your unique mind-body constitution.
              </p>
              <Link to="/assessment/prakriti">
                <Button>Take the Quiz</Button>
              </Link>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <h3 className="font-medium text-text-primary mb-4">Profile Completeness</h3>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Basic Info</span>
                  <Badge variant="success" size="sm">Complete</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Health Data</span>
                  <Badge variant="success" size="sm">Complete</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Prakriti Assessment</span>
                  <Badge variant="success" size="sm">Complete</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Tongue Analysis</span>
                  <Badge variant="warning" size="sm">Pending</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Nail Analysis</span>
                  <Badge variant="warning" size="sm">Pending</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
