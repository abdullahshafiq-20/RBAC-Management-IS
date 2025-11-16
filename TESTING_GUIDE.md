# Testing Guide - New Features

## Quick Testing Checklist

### ✅ 1. Test Real-Time Analytics Dashboard

**Steps:**
1. Login as `admin` with password `admin123`
2. Navigate to **"Analytics"** tab
3. Verify the following charts appear:
   - ✅ Blood Group Distribution (bar chart)
   - ✅ Anonymization Status (pie chart)
   - ✅ User Actions Last 7 Days (bar chart)
   - ✅ Daily Activity Trend (line chart)
   - ✅ Data Retention Status (bar chart)
   - ✅ Consent Status (pie chart)
   - ✅ Patient Registration Timeline (area chart)

**Expected Results:**
- All charts should display with data
- Charts should be interactive (hover for tooltips)
- No errors in console

---

### ✅ 2. Test GDPR Data Retention Timer

**Steps:**
1. Login as `admin`
2. Navigate to **"System"** tab
3. Scroll to **"Data Retention Timer & Management"** section
4. Check the metrics:
   - 🔴 Expired Records count
   - 🟡 Expiring Soon count
   - 🟢 Active Records count

**Expected Results:**
- Metrics display correct counts
- Expired records table shows (if any exist)
- Expiring soon records table shows (if any exist)
- All records table displays with status and days remaining
- Warning messages appear for expired/expiring records

**Test Edge Cases:**
- Check records with retention date = today
- Check records with retention date in 29 days
- Check records with retention date in 31 days

---

### ✅ 3. Test GDPR Consent Banner

**Steps:**
1. Logout if logged in
2. Login with any credentials:
   - `admin` / `admin123`
   - `dr_bob` / `admin123`
   - `alice_recep` / `admin123`
3. **GDPR Consent Banner should appear immediately**

**Test Scenarios:**

#### Scenario A: Accept Consent
1. Expand "View Privacy Policy & Data Usage"
2. Read the privacy notice
3. Click **"Accept & Continue"**
4. Verify:
   - ✅ Success message appears
   - ✅ Dashboard loads
   - ✅ Sidebar shows "GDPR Consent: Accepted"
   - ✅ Timestamp appears in sidebar
   - ✅ "Revoke Consent" button visible

#### Scenario B: Decline Consent
1. Click **"Decline"**
2. Verify:
   - ❌ Error message appears
   - ❌ Cannot access dashboard
   - ❌ User is logged out

#### Scenario C: Revoke Consent
1. After accepting, click **"Revoke Consent"** in sidebar
2. Verify:
   - ✅ Consent banner reappears
   - ✅ Cannot access dashboard until re-accepted
   - ✅ Action logged in audit trail

---

### ✅ 4. Test Audit Logging

**Steps:**
1. Login as `admin`
2. Navigate to **"Audit Logs"** tab
3. Filter by action: **"consent"**
4. Verify consent actions are logged:
   - User accepted GDPR consent
   - User revoked GDPR consent

**Expected Results:**
- All consent actions appear in logs
- Timestamps are correct
- User ID and details are recorded

---

### ✅ 5. Test Auto-Refresh (Optional)

**Steps:**
1. Login as `admin`
2. Navigate to **"System"** tab
3. Scroll to bottom
4. Check **"Enable auto-refresh (every 30 seconds)"**
5. Wait 30 seconds

**Expected Results:**
- Page refreshes automatically
- Data updates (if any changes occurred)
- No errors during refresh

---

## 🔍 Integration Testing

### Test 1: Complete User Flow
1. **Login** → Consent banner appears
2. **Accept consent** → Dashboard loads
3. **View analytics** → Charts display
4. **Check retention timer** → Metrics show
5. **Revoke consent** → Banner reappears
6. **Re-accept** → Dashboard accessible again
7. **Logout** → Session ends

### Test 2: Multi-Role Testing
Repeat above flow for:
- ✅ Admin role
- ✅ Doctor role
- ✅ Receptionist role

All roles should see consent banner and have access to revoke option.

---

## 🐛 Known Issues & Troubleshooting

### Issue: Charts not displaying
**Solution:** Ensure database has patient data. Run sample data insert from `database.sql`

### Issue: Consent banner not appearing
**Solution:** Clear browser cache and session state. Logout and login again.

### Issue: Auto-refresh causing errors
**Solution:** Disable auto-refresh if database connection is slow

### Issue: Retention timer shows wrong dates
**Solution:** Check system timezone and database timezone match

---

## 📊 Test Data Setup

If you need more test data for analytics:

```sql
-- Add more patients with various retention dates
INSERT INTO patients (name, contact, email, date_of_birth, address, diagnosis, blood_group, consent_given, data_retention_date, added_by) VALUES
('Test Patient 1', '+923001111111', 'test1@email.com', '1990-01-01', 'Test Address', 'Test Diagnosis', 'A+', TRUE, CURRENT_DATE - INTERVAL '10 days', 1),
('Test Patient 2', '+923002222222', 'test2@email.com', '1991-02-02', 'Test Address', 'Test Diagnosis', 'B+', TRUE, CURRENT_DATE + INTERVAL '15 days', 1),
('Test Patient 3', '+923003333333', 'test3@email.com', '1992-03-03', 'Test Address', 'Test Diagnosis', 'O+', TRUE, CURRENT_DATE + INTERVAL '60 days', 1);

-- Anonymize some patients for testing
UPDATE patients SET is_anonymized = TRUE WHERE patient_id IN (1, 2);
```

---

## ✅ Success Criteria

All features pass if:
- ✅ Analytics charts display correctly
- ✅ Retention timer shows accurate data
- ✅ Consent banner appears and functions
- ✅ All actions are logged
- ✅ No console errors
- ✅ All roles can access features
- ✅ Data updates in real-time

---

## 📝 Test Report Template

```
Test Date: ___________
Tester: ___________
Version: 2.0

Feature 1: Real-Time Analytics
Status: [ ] Pass [ ] Fail
Notes: _______________________

Feature 2: Data Retention Timer
Status: [ ] Pass [ ] Fail
Notes: _______________________

Feature 3: GDPR Consent Banner
Status: [ ] Pass [ ] Fail
Notes: _______________________

Overall Status: [ ] Pass [ ] Fail
```

---

**Happy Testing! 🎉**

