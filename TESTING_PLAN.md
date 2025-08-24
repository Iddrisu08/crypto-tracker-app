# Enhanced Analytics Testing Plan

## Development Environment Setup
- **Development Branch**: `feature/enhanced-analytics`
- **Development Ports**: Backend: 5001, Frontend: 3001 (will be set during frontend start)
- **Production Ports**: Backend: 5000, Frontend: 5174 (on main branch)

## Pre-Enhancement Testing Checklist

### Backend API Tests
- [ ] `/portfolio` endpoint returns correct data
- [ ] `/live_profit_loss` endpoint functions properly
- [ ] `/daily_profit_loss` endpoint calculates correctly
- [ ] `/transactions` endpoint returns transaction history
- [ ] `/add_transaction` endpoint accepts new transactions
- [ ] DCA calculations are accurate
- [ ] Manual transaction integration works
- [ ] Price caching functions correctly

### Frontend Tests
- [ ] Application loads without errors
- [ ] Live stats display correctly
- [ ] Daily profit/loss shows accurate data
- [ ] Portfolio overview functions properly
- [ ] Charts render without issues
- [ ] Transaction history displays correctly
- [ ] Add transaction form works
- [ ] Dark/light theme toggle functions
- [ ] Auto-refresh mechanism works
- [ ] Manual refresh buttons function

## Enhanced Analytics Testing Checklist

### New Backend Features
- [ ] `/performance_metrics` endpoint returns comprehensive analytics
- [ ] ROI calculations are mathematically correct
- [ ] Annualized return calculations are accurate
- [ ] Portfolio allocation percentages are correct
- [ ] DCA vs lump sum analysis functions
- [ ] Average purchase price calculations are correct
- [ ] Historical performance data is accurate

### New Frontend Features
- [ ] Analytics dashboard displays without errors
- [ ] Portfolio allocation pie chart renders correctly
- [ ] Performance metrics cards show accurate data
- [ ] Analytics integrate with existing refresh mechanisms
- [ ] New components follow existing design patterns
- [ ] Analytics data updates with portfolio changes

## Integration Testing
- [ ] New analytics work with existing manual transactions
- [ ] Analytics update correctly when new transactions are added
- [ ] Performance remains acceptable with new calculations
- [ ] No conflicts with existing API endpoints
- [ ] Frontend state management handles new data correctly

## Performance Testing
- [ ] Page load time remains under 3 seconds
- [ ] API response times remain under 1 second
- [ ] No memory leaks in new calculations
- [ ] Browser performance is not degraded

## User Acceptance Testing
- [ ] Analytics provide valuable insights
- [ ] Data is easy to understand and interpret
- [ ] New features enhance rather than complicate the experience
- [ ] Analytics help answer key investment questions

## Rollback Testing
- [ ] Can successfully switch back to main branch
- [ ] Production environment remains unaffected
- [ ] No data corruption during development
- [ ] Easy to revert if issues are found

## Testing Commands

### Start Development Environment
```bash
# Terminal 1 - Backend
cd crypto-tracker-backend
python3 app.py  # Runs on port 5001

# Terminal 2 - Frontend  
cd crypto-tracker-frontend
npm run dev     # Should auto-assign port (likely 3001)
```

### Start Production Environment (for comparison)
```bash
# Switch to main branch
git checkout main

# Terminal 1 - Backend
cd crypto-tracker-backend
python3 app.py  # Runs on port 5000

# Terminal 2 - Frontend
cd crypto-tracker-frontend
npm run dev     # Should auto-assign port (likely 5174)
```

### Test API Endpoints
```bash
# Test development backend
curl http://localhost:5001/portfolio
curl http://localhost:5001/performance_metrics

# Test production backend (for comparison)
curl http://localhost:5000/portfolio
```