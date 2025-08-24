# 🧪 Complete Test Suite Commands

## 🚀 **Run These Commands One by One**

### **Prerequisites:**
Make sure both servers are running:
```bash
# Terminal 1: Frontend
cd crypto-tracker-frontend
npm run dev

# Terminal 2: Backend  
cd crypto-tracker-backend
python3 app.py
```

---

## **🔍 TEST 1: Portfolio Features**

```bash
cd crypto-tracker-frontend
npx playwright test tests/portfolio.spec.js --reporter=line
```

**What this tests:**
- ✅ Portfolio overview displays
- ✅ Refresh button works
- ✅ BTC and ETH holdings show
- ✅ Investment vs Current Value chart renders
- ✅ Error handling

---

## **📊 TEST 2: Analytics Dashboard**

```bash
npx playwright test tests/analytics.spec.js --reporter=line
```

**What this tests:**
- ✅ Analytics dashboard loads
- ✅ Key metrics cards display
- ✅ Bitcoin performance section
- ✅ Ethereum performance section
- ✅ DCA strategy analysis
- ✅ Portfolio allocation pie chart
- ✅ Performance periods (best/worst weeks)
- ✅ Refresh functionality
- ✅ Loading states

---

## **💰 TEST 3: Transaction Management**

```bash
npx playwright test tests/transactions.spec.js --reporter=line
```

**What this tests:**
- ✅ Transaction form displays
- ✅ Transaction history shows
- ✅ Form validation works
- ✅ Refresh history button
- ✅ Price fetching functionality

---

## **🎯 TEST 4: Full Integration Test**

```bash
npx playwright test --reporter=line
```

**What this tests:**
- ✅ All features working together
- ✅ Cross-browser compatibility
- ✅ Mobile responsiveness
- ✅ Complete user journey

---

## **📊 View Detailed Results**

After running tests:
```bash
npx playwright show-report
```

---

## **🔧 Debug Mode (if tests fail)**

```bash
# Run with visible browser
npx playwright test --headed

# Debug specific test
npx playwright test tests/analytics.spec.js --debug

# Run in UI mode
npx playwright test --ui
```

---

## **📱 Test Mobile Responsiveness**

```bash
npx playwright test --project="Mobile Chrome"
npx playwright test --project="Mobile Safari"
```

---

## **🚨 Quick Status Check**

```bash
# Test if servers are running
curl http://localhost:5173
curl http://127.0.0.1:5001/portfolio
```

---

## **📋 Expected Results**

### **All Tests Should Show:**
- ✅ **Portfolio Tests**: 5 tests passing
- ✅ **Analytics Tests**: 8 tests passing  
- ✅ **Transaction Tests**: 5 tests passing
- ✅ **Total**: ~18 tests passing

### **Test Report Will Include:**
- 📊 Pass/fail statistics
- 🎥 Screenshots of failures
- 📹 Video recordings
- 📋 Detailed error messages
- ⏱️ Performance metrics

---

## **🎉 Success Indicators**

You'll know everything is working when:
- ✅ All tests pass
- ✅ No red error messages
- ✅ Screenshots show your UI correctly
- ✅ Portfolio values are accurate
- ✅ Analytics charts render properly
- ✅ Transaction forms validate correctly

**Run these commands in order and let me know the results!** 🚀