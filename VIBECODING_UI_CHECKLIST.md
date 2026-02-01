# 🎨 VIBECODING UI DEVELOPMENT CHECKLIST

## 📋 Project Setup

- [ ] Create new Vibecoding project
- [ ] Initialize folder structure:
  ```
  frontend/
  ├── pages/
  ├── components/
  ├── api/
  ├── styles/
  ├── utils/
  └── app.vibes
  ```
- [ ] Set up environment variables (.env)
  - Backend API URL: `http://localhost:8000`
  - Session storage configuration
- [ ] Initialize version control (git)

---

## 🏠 Core Pages (7 pages)

### **1. Dashboard.vibes** (Home Panel)
**Purpose:** Command center with all insights

**Features to Implement:**
- [ ] Header with user name + role selector (Doctor/Patient toggle)
- [ ] Welcome message based on role
- [ ] Quick stats cards:
  - [ ] Current dosha balance (pie chart)
  - [ ] Health score (gauge)
  - [ ] Days since last diagnosis
- [ ] Widget grid layout:
  - [ ] Geo-Dosha card (Weather + adjusted dosha)
  - [ ] Future risks card (Top 3 predictions)
  - [ ] Dosha clock card (Current hour guidance)
  - [ ] News portal card (Latest articles)
- [ ] Quick action buttons:
  - [ ] "Start New Analysis"
  - [ ] "View Previous Results"
  - [ ] "Chat with AI"
- [ ] Responsive design (mobile + desktop)

**API Calls:**
```vibes
GET /api/v1/dashboard/geo-dosha
GET /api/v1/dashboard/future-risks
GET /api/v1/dashboard/dosha-clock
GET /api/v1/dashboard/news
```

---

### **2. Assessment.vibes** (Multimodal Analysis)
**Purpose:** Main diagnostic interface

**Layout (3 Columns):**

**Left Column: Input Section**
- [ ] Image upload for tongue
  - [ ] Drag-drop area
  - [ ] File type validation (jpg, png)
  - [ ] Preview with zoom
  - [ ] Clear button
- [ ] Image upload for nails
  - [ ] Same features as tongue
  - [ ] Side-by-side preview
- [ ] Vision model output display:
  - [ ] Agni score slider visual
  - [ ] Ama presence dropdown
  - [ ] Color code selector
  - [ ] (Same for nails)

**Center Column: Symptoms Input**
- [ ] Chief complaint text area
  - [ ] Character count indicator
  - [ ] Placeholder suggestion
- [ ] Symptom multi-select
  - [ ] Search/filter
  - [ ] Common symptoms pre-populated
  - [ ] Custom symptom input
- [ ] Additional fields:
  - [ ] Duration slider (1-365 days)
  - [ ] Severity slider (1-10)
  - [ ] Recent triggers (multi-input)
  - [ ] Relief measures (multi-input)
- [ ] Submit button (disabled until min fields filled)

**Right Column: Patient Profile**
- [ ] Collapsible accordion sections:
  - [ ] Basic Info (age, gender, height, weight)
  - [ ] Constitution (known prakriti)
  - [ ] Environment (season, location)
  - [ ] Lifestyle (stress, digestion, sleep)
- [ ] Profile completeness indicator (%)
- [ ] Pre-fill from previous session (if available)
- [ ] Save profile option

**Status Indicators:**
- [ ] Loading spinner during analysis
- [ ] Progress bar (Analyzing... 20%, 40%, etc.)
- [ ] Error messages with clear guidance

**API Call:**
```vibes
POST /api/v1/multimodal/analyze
  Input: { vision_analysis, chief_complaint, symptom_list, profile }
  Output: Diagnosis result + session_id
```

---

### **3. Results.vibes** (Multi-View Results)
**Purpose:** Display diagnosis in multiple formats

**Tab System (3 Tabs):**

#### **Tab 1: Doctor View**
- [ ] Condition (Sanskrit + English)
- [ ] Samprapti (Pathophysiology)
  - [ ] Formatted with highlights
  - [ ] Expandable sections
- [ ] Doshas involved (visual indicators)
- [ ] Shlokas (Classical citations)
  - [ ] Sanskrit text + English translation
  - [ ] Source reference
  - [ ] Clickable for more info
- [ ] Treatment principles
- [ ] Contraindications warning box
- [ ] Confidence score badge
- [ ] Verification button (for doctors)

#### **Tab 2: Patient View**
- [ ] Condition simple explanation
- [ ] "What happened" narrative
- [ ] 3-Day Diet Plan
  - [ ] Day tabs with meals
  - [ ] Clickable recipes (modals)
  - [ ] Print friendly format
  - [ ] Checkboxes to mark completed
- [ ] Daily Routine card
  - [ ] Morning routine
  - [ ] Midday routine
  - [ ] Evening routine
- [ ] Herbs & Remedies
  - [ ] Cards with dosage
  - [ ] Instructions
  - [ ] Warnings
- [ ] Foods to avoid (red highlighted list)
- [ ] Recovery timeline
- [ ] "When to see doctor" alerts

#### **Tab 3: AYUSH Framework**
- [ ] 8-Fold Examination display
  - [ ] Nadi (Pulse)
  - [ ] Jihva (Tongue)
  - [ ] Shabda (Voice)
  - [ ] Sparsha (Touch)
  - [ ] Drik (Eyes)
  - [ ] Mutra (Urine)
  - [ ] Purisha (Stool)
  - [ ] Akriti (Body build)
- [ ] Summary statement
- [ ] Information icons with explanations

**Additional Sections:**
- [ ] Recovery Graph (line chart)
  - [ ] X-axis: Days (0 to recovery_end)
  - [ ] Y-axis: Health score (0-100)
  - [ ] Milestone markers
  - [ ] Tooltip on hover
  - [ ] Export as PNG button
- [ ] Feature Correlations
  - [ ] Heatmap visualization
  - [ ] Legend explanation
  - [ ] "Evidence of cross-modal validation" note
- [ ] Cross-Modal Validation List
  - [ ] Each correlation as a bullet point
  - [ ] Confidence percentages
  - [ ] Icons for validation types

**Action Buttons:**
- [ ] Share/Export (PDF, JSON, CSV)
- [ ] Print friendly version
- [ ] Save to patient record
- [ ] Doctor verification button (if doctor role)
- [ ] Start new analysis

**API Calls:**
```vibes
Already received from /multimodal/analyze
Display: DiagnosisResult object
```

---

### **4. Profile.vibes** (Patient Health Profile)
**Purpose:** Build/edit comprehensive health profile

**Layout: Form with Progressive Sections**

- [ ] Personal Information Section
  - [ ] Age slider (1-120)
  - [ ] Gender radio buttons (M/F/Other)
  - [ ] Height input (cm) with visual indicator
  - [ ] Weight input (kg) with BMI display
  - [ ] BMI category badge (Underweight/Normal/Overweight/Obese)
  - [ ] Body frame estimate (Vata/Pitta/Kapha visual)

- [ ] Constitutional Assessment
  - [ ] Known Prakriti dropdown
  - [ ] "Unsure? Click to triangulate" link
  - [ ] Visual dosha representation

- [ ] Health Status
  - [ ] Current symptoms multi-select (with custom add)
  - [ ] Stress level slider (Low/Med/High visual)
  - [ ] Sleep hours slider (0-12) with quality selector
  - [ ] Digestion quality dropdown + description
  - [ ] Exercise type dropdown
  - [ ] Exercise frequency (days/week)

- [ ] Environmental Context
  - [ ] Current season dropdown
  - [ ] Location picker (for geo-dosha)
  - [ ] Climate type (auto-detected from location)

- [ ] Medical History
  - [ ] Past diseases multi-select
  - [ ] Current medications text area
  - [ ] Family history checklist
  - [ ] Allergies text area

- [ ] Lifestyle Details
  - [ ] Diet type dropdown
  - [ ] Meal timing preferences
  - [ ] Water intake
  - [ ] Herbs currently using

- [ ] Save Profile Button
  - [ ] Validates required fields
  - [ ] Shows completion %
  - [ ] Success notification
  - [ ] Auto-populate in Assessment page

---

### **5. Verification.vibes** (Doctor Override Panel)
**Purpose:** Clinical verification and AI correction

**Layout: Side-by-Side Original vs. Corrected**

**Left Column: Original AI Diagnosis (Read-only)**
- [ ] Condition (highlighted)
- [ ] Treatment recommendations
- [ ] Risks identified
- [ ] Doshas assigned

**Right Column: Doctor Override (Editable)**
- [ ] Corrected condition text area
- [ ] Corrected treatment text area
- [ ] Risk checkboxes
  - [ ] Tick/untick identified risks
  - [ ] Add new risks
  - [ ] Remove risks
- [ ] Modified prescription
  - [ ] Free text editor
  - [ ] Structured form fields
  - [ ] Copy from recommendations

**Additional Fields:**
- [ ] Doctor notes textarea
  - [ ] Why you disagreed with AI
  - [ ] Additional context
  - [ ] Patient-specific notes
- [ ] Confidence level adjuster
  - [ ] How confident is this correction?
  - [ ] Slider 0-100%

**Action Buttons:**
- [ ] Preview (show final result)
- [ ] Sign Off (save as ground truth)
- [ ] Cancel (discard changes)
- [ ] Revert to AI (restore original)

**Verification Indicators:**
- [ ] Changed fields highlighted
- [ ] Change summary box
- [ ] Doctor name/ID (for audit log)
- [ ] Timestamp

**API Call:**
```vibes
POST /api/v1/clinical/verify
  Input: { session_id, corrections, doctor_notes }
  Output: Verification status + improvement credit
```

---

### **6. Analysis.vibes** (Feature Correlation & Deep Dive)
**Purpose:** Show evidence of multimodal reasoning

**Left Panel: Feature Correlation Heatmap**
- [ ] Interactive heatmap visualization
  - [ ] Rows: Features (Nail Ridges, Joint Pain, Agni, etc.)
  - [ ] Columns: Features
  - [ ] Color intensity: Correlation strength
  - [ ] Hover: Shows exact correlation %
- [ ] Legend (0% = no correlation, 100% = perfect)
- [ ] Feature list with definitions
- [ ] Download heatmap as image

**Right Panel: Correlation Insights**
- [ ] Each correlation as a card:
  - [ ] "Feature A ↔ Feature B"
  - [ ] Correlation percentage
  - [ ] Clinical interpretation
  - [ ] Confidence level
  - [ ] Source (Text/Vision/Profile)
- [ ] Sort by: Strength, Type, Confidence
- [ ] Filter by: Validated, Uncertain, Weak

**Bottom: Ayurveda Q&A**
- [ ] Dynamic FAQ based on diagnosis
  - [ ] "Why does eating ice cream hurt my joints?"
  - [ ] "What makes my digestion weak?"
  - [ ] "Why do I feel worse in winter?"
- [ ] Search Q&A
- [ ] Ask custom question (triggers chat)

**API Calls:**
```vibes
Already in DiagnosisResult.feature_correlations
Also: /api/v1/chat/ask (for custom questions)
```

---

### **7. Chat.vibes** (Role-Based Chat Interface)
**Purpose:** Conversational AI for doctor/patient

**Layout: Chat Interface**

**Header:**
- [ ] Role indicator (Doctor/Patient)
- [ ] Role switcher (toggle)
- [ ] Current session info
- [ ] Clear history button

**Chat Area:**
- [ ] Message history with timestamps
- [ ] Doctor messages: Blue background
- [ ] AI responses: Green background
- [ ] System messages: Gray
- [ ] Typing indicator when processing
- [ ] Scroll to bottom on new message
- [ ] Copy message button on hover

**Knowledge Base Indicator:**
- [ ] Doctor mode: "Using Sushruta DB"
- [ ] Patient mode: "Using Home Remedy DB"
- [ ] Icon showing active knowledge source

**Input Area:**
- [ ] Message text input with focus
- [ ] Send button (or Enter key)
- [ ] Character count (if applicable)
- [ ] Suggested questions dropdown:
  - [ ] Role-specific suggestions
  - [ ] Recent questions
  - [ ] Popular questions

**Sidebar (Optional):**
- [ ] Conversation history
- [ ] Save chat
- [ ] Export as PDF
- [ ] Session management

**API Calls:**
```vibes
POST /api/v1/chat/ask
  Input: { user_role, message, session_id }
  Output: { response, context_used }
```

---

## 🧩 Reusable Components (10 components)

### **1. ImageUpload.vibes**
```vibes
component ImageUpload {
  prop title: "Upload Image"
  prop accept: ".jpg,.png"
  prop maxSize: 5 // MB
  prop onUpload: function
  
  render {
    <container class="image-upload">
      <label>{title}</label>
      <dropzone {accept} {maxSize} on:files={onUpload}>
        <placeholder>Drag image or click to upload</placeholder>
        <preview if:image />
      </dropzone>
    </container>
  }
}
```

### **2. DoshaIndicator.vibes**
```vibes
component DoshaIndicator {
  prop vata: number
  prop pitta: number
  prop kapha: number
  
  render {
    <div class="dosha-wheel">
      <circle class="vata" style="--percent: {vata}%">
        Vata {vata}%
      </circle>
      <circle class="pitta" style="--percent: {pitta}%">
        Pitta {pitta}%
      </circle>
      <circle class="kapha" style="--percent: {kapha}%">
        Kapha {kapha}%
      </circle>
    </div>
  }
}
```

### **3. RecoveryGraph.vibes**
```vibes
component RecoveryGraph {
  prop timeline: array // ["Day 0", "Day 7", ...]
  prop healthScores: array // [30, 45, 60, ...]
  prop milestones: array // [{day, description}]
  
  render {
    <LineChart {timeline} {healthScores}>
      <Milestones items={milestones} />
    </LineChart>
  }
}
```

### **4. SymptomInput.vibes**
```vibes
component SymptomInput {
  prop symptoms: array
  prop onChange: function
  
  render {
    <div class="symptom-input">
      <input placeholder="Add symptoms..." on:enter={addSymptom} />
      <tags items={symptoms} on:remove={removeSymptom} />
    </div>
  }
}
```

### **5. DoshaClockWidget.vibes**
```vibes
component DoshaClockWidget {
  prop currentTime: string
  prop doshaInfo: object
  
  render {
    <card>
      <h3>🕐 Dosha Clock</h3>
      <time>{currentTime}</time>
      <dosha-badge>{doshaInfo.dosha}</dosha-badge>
      <principle>{doshaInfo.principle}</principle>
      <activities>
        {doshaInfo.activities.map(a => <li>{a}</li>)}
      </activities>
    </card>
  }
}
```

### **6. RiskGauge.vibes**
```vibes
component RiskGauge {
  prop disease: string
  prop riskPercent: number
  prop alertLevel: string // Low/Med/High/Critical
  
  render {
    <div class="risk-gauge" data-level={alertLevel}>
      <label>{disease}</label>
      <gauge value={riskPercent} max={100} />
      <percent>{riskPercent}%</percent>
      <alert>{alertLevel}</alert>
    </div>
  }
}
```

### **7. DietPlanCard.vibes**
```vibes
component DietPlanCard {
  prop day: number
  prop meals: object // {breakfast: [], lunch: [], ...}
  
  render {
    <card class="diet-plan">
      <h3>Day {day}</h3>
      {Object.entries(meals).map(([meal, items]) => (
        <section>
          <h4>{meal}</h4>
          <ul>{items.map(item => <li>{item}</li>)}</ul>
        </section>
      ))}
    </card>
  }
}
```

### **8. FeatureHeatmap.vibes**
```vibes
component FeatureHeatmap {
  prop features: array
  prop correlationMatrix: 2DArray
  
  render {
    <table class="heatmap">
      <thead>
        <tr>
          <th>Feature</th>
          {features.map(f => <th>{f}</th>)}
        </tr>
      </thead>
      <tbody>
        {correlationMatrix.map((row, i) => (
          <tr>
            <td>{features[i]}</td>
            {row.map(val => <td class="heat-{intensity(val)}" title="{val}%"></td>)}
          </tr>
        ))}
      </tbody>
    </table>
  }
}
```

### **9. NewsCard.vibes**
```vibes
component NewsCard {
  prop article: object
  
  render {
    <card class="news-card">
      <badge>{article.category}</badge>
      <h3>{article.title}</h3>
      <p>{article.snippet}</p>
      <footer>
        <source>{article.source}</source>
        <date>{article.published_date}</date>
        <link href={article.url}>Read More →</link>
      </footer>
    </card>
  }
}
```

### **10. VerificationForm.vibes**
```vibes
component VerificationForm {
  prop originalDiagnosis: object
  prop onSubmit: function
  
  render {
    <form on:submit={onSubmit}>
      <h2>Clinical Verification</h2>
      <textarea name="corrected_diagnosis" 
        value={originalDiagnosis.diagnosis} />
      <textarea name="corrected_treatment" 
        value={originalDiagnosis.treatment} />
      <checkboxes name="risk_unticked" items={originalDiagnosis.risks} />
      <textarea name="doctor_notes" placeholder="Your notes..." />
      <button type="submit">Sign Off</button>
    </form>
  }
}
```

---

## 🎨 Design System

### **Color Palette**
```css
/* Dosha Colors */
--vata-color: #B8860B;      /* Gold - Air */
--pitta-color: #DC143C;     /* Crimson - Fire */
--kapha-color: #4169E1;     /* Royal Blue - Water */

/* Semantic Colors */
--success: #28A745;
--warning: #FFC107;
--danger: #DC3545;
--info: #17A2B8;

/* Alert Levels */
--critical: #DC143C;
--high: #FF6347;
--medium: #FFA500;
--low: #90EE90;

/* UI Colors */
--primary: #2C5F2D;        /* Ayurveda green */
--background: #F5F5F5;
--text: #333333;
--border: #CCCCCC;
```

### **Typography**
```css
--font-primary: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
--font-code: 'Courier New', Courier, monospace;

--heading-1: 28px bold
--heading-2: 24px bold
--heading-3: 20px bold
--body: 16px regular
--small: 14px regular
--tiny: 12px regular
```

### **Spacing**
```css
--xs: 4px
--sm: 8px
--md: 16px
--lg: 24px
--xl: 32px
--xxl: 48px
```

### **Breakpoints**
```css
--mobile: 480px
--tablet: 768px
--desktop: 1024px
--wide: 1280px
```

---

## 📱 Responsive Design

- [ ] Mobile (480px): Single column layout
- [ ] Tablet (768px): Two column layout
- [ ] Desktop (1024px): Multi-column with sidebar
- [ ] Wide (1280px): Full multi-panel layout
- [ ] Test on actual devices
- [ ] Touch-friendly buttons (48px min)
- [ ] Readable text on all sizes

---

## 🔗 API Integration Checklist

- [ ] Base URL configured (`.env`)
- [ ] Error handling for all requests
- [ ] Loading states (spinners, disabled buttons)
- [ ] Session management (localStorage)
- [ ] Request retry logic
- [ ] Response caching where appropriate
- [ ] Timeout handling
- [ ] Network error messages
- [ ] Authentication headers (if needed)
- [ ] CORS handled properly

---

## ♿ Accessibility

- [ ] Semantic HTML structure
- [ ] ARIA labels on interactive elements
- [ ] Keyboard navigation support
- [ ] Color contrast ratios (WCAG AA)
- [ ] Image alt texts
- [ ] Form labels properly associated
- [ ] Skip navigation link
- [ ] Focus indicators visible
- [ ] Error messages clear and linked to inputs
- [ ] Screen reader tested

---

## 🧪 Testing Checklist

- [ ] Unit tests for components
- [ ] Integration tests for pages
- [ ] E2E tests for user flows
- [ ] Mobile responsiveness
- [ ] Cross-browser compatibility
- [ ] Performance profiling
- [ ] Load testing
- [ ] Accessibility audit
- [ ] User acceptance testing
- [ ] Doctor workflow testing
- [ ] Patient workflow testing

---

## 📦 Build & Deployment

- [ ] Production build configuration
- [ ] Environment variable management
- [ ] Asset optimization (images, fonts)
- [ ] Code splitting for performance
- [ ] Service worker for offline support
- [ ] Analytics integration
- [ ] Error reporting (Sentry, etc.)
- [ ] Performance monitoring
- [ ] CDN configuration
- [ ] SSL/TLS setup

---

## 📊 Development Timeline

**Week 1-2: Setup & Core Pages**
- Project scaffold and setup
- Dashboard page
- Assessment page structure

**Week 3-4: Core Components**
- ImageUpload, DoshaIndicator, RecoveryGraph
- SymptomInput, DietPlan, RiskGauge
- Heatmap component

**Week 5-6: Results & Verification**
- Results page (all 3 tabs)
- Verification panel
- Profile page

**Week 7: Dashboard Features**
- Geo-Dosha widget
- Future risks widget
- Dosha clock widget
- News portal

**Week 8: Chat & Polish**
- Chat interface
- Role-based logic
- Responsive design polish
- Bug fixes

**Week 9-10: Testing & Deployment**
- Unit/integration tests
- E2E tests
- Performance optimization
- Deployment setup

---

## ✅ Final Checklist

- [ ] All 7 pages implemented
- [ ] All 10 components implemented
- [ ] All API endpoints integrated
- [ ] Responsive design tested
- [ ] Accessibility verified
- [ ] Performance optimized
- [ ] Error handling complete
- [ ] User testing completed
- [ ] Documentation updated
- [ ] Ready for production deployment

---

**🎨 Ready to build the most advanced Ayurvedic diagnostic UI!**
